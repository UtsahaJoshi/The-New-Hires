from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import User
from .auth_utils import create_access_token, decode_access_token
import os
import httpx
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.get("/github/login")
async def github_login():
    redirect_uri = "http://localhost:5173/login"
    return {
        "url": f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=repo,user:email&redirect_uri={redirect_uri}"
    }

@router.get("/github/callback")
async def github_callback(code: str, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Debug: Received code {code}")
        print(f"Debug: Client ID {GITHUB_CLIENT_ID}")
        
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            print("Debug: exchanging code for token...")
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": "http://localhost:5173/login",
                },
            )
            print(f"Debug: Token response status: {response.status_code}")
            print(f"Debug: Token response body: {response.text}")
            
            data = response.json()
            access_token = data.get("access_token")
            
            if not access_token:
                print(f"Error: No access token. Data: {data}")
                raise HTTPException(status_code=400, detail=f"Failed to retrieve access token: {data}")

            # Get user info
            print("Debug: Fetching user info...")
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json",
                },
            )
            print(f"Debug: User response status: {user_response.status_code}")
            user_data = user_response.json()
            print(f"Debug: User data: {user_data.get('login')}")
            
            # Check if user exists
            stmt = select(User).where(User.github_id == str(user_data["id"]))
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                print("Debug: Creating new user...")
                user = User(
                    github_id=str(user_data["id"]),
                    username=user_data["login"],
                    avatar_url=user_data["avatar_url"],
                    access_token=access_token,
                    xp=0,
                    level=1
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
            else:
                print("Debug: Updating existing user...")
                user.access_token = access_token
                await db.commit()
            
            # Create JWT
            jwt_token = create_access_token({"sub": user.username, "id": user.id})
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "avatar_url": user.avatar_url,
                    "level": user.level,
                    "xp": user.xp
                }
            }
    except Exception as e:
        print(f"CRITICAL ERROR in github_callback: {str(e)}")
        import traceback
        with open("error.log", "a") as f:
            f.write(f"\n--- Error at {datetime.now()} ---\n")
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
