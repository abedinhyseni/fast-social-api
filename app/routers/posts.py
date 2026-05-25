from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.post import Like, Post
from app.models.user import User
from app.schemas.post import PostCreate, PostOut, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


def _post_out(post: Post) -> dict:
    return {
        "id": post.id,
        "content": post.content,
        "image_url": post.image_url or "",
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "bio": post.author.bio or "",
            "avatar_url": post.author.avatar_url or "",
            "created_at": post.author.created_at,
            "followers_count": len(post.author.followers),
            "following_count": len(post.author.following),
        },
        "likes_count": len(post.likes),
        "comments_count": len(post.comments),
    }


@router.get("", response_model=list[PostOut])
def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    following_ids = [u.id for u in current_user.following] + [current_user.id]
    posts = (
        db.query(Post)
        .filter(Post.author_id.in_(following_ids))
        .order_by(Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_post_out(p) for p in posts]


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(author_id=current_user.id, content=data.content, image_url=data.image_url)
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_out(post)


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_out(post)


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if data.content is not None:
        post.content = data.content
    if data.image_url is not None:
        post.image_url = data.image_url
    post.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(post)
    return _post_out(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(post)
    db.commit()


@router.post("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Post).filter(Post.id == post_id).first():
        raise HTTPException(status_code=404, detail="Post not found")
    if db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first():
        raise HTTPException(status_code=400, detail="Already liked")
    db.add(Like(user_id=current_user.id, post_id=post_id))
    db.commit()


@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    like = db.query(Like).filter(Like.user_id == current_user.id, Like.post_id == post_id).first()
    if not like:
        raise HTTPException(status_code=400, detail="Not liked")
    db.delete(like)
    db.commit()
