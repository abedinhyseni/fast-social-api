# FastSocialAPI
FastAPI REST API — Social/Community Mobile App

 Context

 Building a greenfield FastAPI REST API for a social/community mobile app. 
 Requirements: JWT auth (register + login + refresh), SQLite via SQLAlchemy ORM,
 social features (posts, comments, likes, follows).

 ---
 Project Structure

 FastSocialAPI/
 app/
  main.py              # App factory, CORS, router registration
  database.py          # SQLAlchemy engine, SessionLocal, Base
  dependencies.py      # get_db(), get_current_user()
  models/
  user.py          # User, Follow (association table)
  post.py          # Post, Like (association table)
  comment.py       # Comment
  schemas/
  user.py          # UserCreate, UserOut, UserProfile
  post.py          # PostCreate, PostOut
  comment.py       # CommentCreate, CommentOut
  token.py         # Token, TokenRefresh
  routers/
  auth.py          # POST /auth/register, /auth/login, /auth/refresh
  users.py         # GET /users/me, /users/{id}, follow/unfollow, followers/following
  posts.py         # CRUD /posts, like/unlike, feed
  comments.py      # GET/POST /posts/{id}/comments, DELETE /comments/{id}
  core/
  config.py        # Settings via pydantic-settings (SECRET_KEY, TOKEN_EXPIRE_MINUTES)
  security.py      # hash_password, verify_password, create_access_token, create_refresh_token, decode_token
  .env                     # SECRET_KEY, DATABASE_URL
  requirements.txt

 ---
 Key Endpoints

   Method           Path                               Description                     
   POST     /auth/register          Create account                                     
   POST     /auth/login             Returns access + refresh tokens                    
   POST     /auth/refresh           Exchange refresh token → new access token          
   GET      /users/me               Current user profile                               
   GET      /users/{id}             Public profile                                     
   POST     /users/{id}/follow      Follow user                                        
   DELETE   /users/{id}/follow      Unfollow user                                      
   GET      /users/{id}/followers   Follower list                                      
   GET      /users/{id}/following   Following list                                     
   GET      /posts                  Feed (posts from followed users + own, paginated)  
   POST     /posts                  Create post                                        
   GET      /posts/{id}             Single post                                        
   PUT      /posts/{id}             Edit own post                                      
   DELETE   /posts/{id}             Delete own post                                    
   POST     /posts/{id}/like        Like post                                          
   DELETE   /posts/{id}/like        Unlike post                                        
   GET      /posts/{id}/comments    List comments                                      
   POST     /posts/{id}/comments    Add comment                                        
   DELETE   /comments/{id}          Delete own comment                                 
 
 ---
 Database Models

 - User: id, username, email, hashed_password, bio, avatar_url, created_at
 - Follow: follower_id → User, followed_id → User (composite PK)
 - Post: id, author_id → User, content, image_url, created_at, updated_at
 - Like: user_id → User, post_id → Post (composite PK)
 - Comment: id, author_id → User, post_id → Post, content, created_at

 ---
 Dependencies (requirements.txt)

 fastapi
 uvicorn[standard]
 sqlalchemy
 python-jose[cryptography]
 passlib[bcrypt]
 python-multipart
 pydantic[email]
 pydantic-settings
 python-dotenv

 ---
 Implementation Steps

 1. requirements.txt — list dependencies above
 2. .env — SECRET_KEY, DATABASE_URL=sqlite:///./social.db, ACCESS_TOKEN_EXPIRE_MINUTES=30, REFRESH_TOKEN_EXPIRE_DAYS=7
 3. app/core/config.py — Settings class via pydantic-settings reading .env
 4. app/core/security.py — bcrypt password hashing, JWT access + refresh token creation/decoding
 5. app/database.py — SQLAlchemy engine, SessionLocal, Base
 6. app/models/ — all ORM models; call Base.metadata.create_all() on startup
 7. app/schemas/ — Pydantic v2 models for request/response validation
 8. app/dependencies.py — get_db() (DB session), get_current_user() (JWT bearer extraction)
 9. app/routers/auth.py — register, login, refresh
 10. app/routers/users.py — profile, follow/unfollow, followers/following
 11. app/routers/posts.py — CRUD, feed, like/unlike
 12. app/routers/comments.py — list, create, delete
 13. app/main.py — assemble app, add CORS (allow_origins=["*"] for mobile), include all routers, create DB tables on startup

 ---
 Verification

 # Install deps
 pip install -r requirements.txt

 # Start server
 uvicorn app.main:app --reload

 # Auto-generated docs available at:
 http://localhost:8000/docs   (Swagger UI)
 http://localhost:8000/redoc

 # Test flow:
 1. POST /auth/register  → create user
 2. POST /auth/login     → get access + refresh tokens
 3. GET  /users/me       → pass Bearer token in Authorization header
 4. POST /posts          → create a post
 5. POST /posts/{id}/like → like it