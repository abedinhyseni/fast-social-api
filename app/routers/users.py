from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import Follow, User
from app.schemas.user import UserOut, UserProfile, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _profile(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "bio": user.bio or "",
        "avatar_url": user.avatar_url or "",
        "created_at": user.created_at,
        "followers_count": len(user.followers),
        "following_count": len(user.following),
    }


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.bio is not None:
        current_user.bio = data.bio
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserProfile)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _profile(user)


@router.post("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.followed_id == user_id).first():
        raise HTTPException(status_code=400, detail="Already following")
    db.add(Follow(follower_id=current_user.id, followed_id=user_id))
    db.commit()


@router.delete("/{user_id}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    follow = db.query(Follow).filter(Follow.follower_id == current_user.id, Follow.followed_id == user_id).first()
    if not follow:
        raise HTTPException(status_code=400, detail="Not following this user")
    db.delete(follow)
    db.commit()


@router.get("/{user_id}/followers", response_model=list[UserProfile])
def get_followers(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [_profile(u) for u in user.followers]


@router.get("/{user_id}/following", response_model=list[UserProfile])
def get_following(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return [_profile(u) for u in user.following]
