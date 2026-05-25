from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(tags=["comments"])


def _comment_out(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at,
        "author": {
            "id": comment.author.id,
            "username": comment.author.username,
            "bio": comment.author.bio or "",
            "avatar_url": comment.author.avatar_url or "",
            "created_at": comment.author.created_at,
            "followers_count": len(comment.author.followers),
            "following_count": len(comment.author.following),
        },
    }


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return [_comment_out(c) for c in post.comments]


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Post).filter(Post.id == post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")
    comment = Comment(author_id=current_user.id, post_id=post_id, content=data.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _comment_out(comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(comment)
    db.commit()
