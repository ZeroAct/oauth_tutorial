import os

import httpx
import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from enums import Platform
from scheme import UserInfo

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


router = APIRouter()


@router.get("/login")
async def login():
    """
    구글 로그인 URL로 리다이렉트
    """
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code"
        f"&scope=openid%20https://www.googleapis.com/auth/userinfo.email%20https://www.googleapis.com/auth/userinfo.profile"
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str, request: Request):
    """
    구글 인증 후 리다이렉트 콜백
    """
    token_url = "https://oauth2.googleapis.com/token"
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    # Access Token 요청
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=token_response.status_code, detail="Failed to get access token"
            )

        access_token = token_response.json().get("access_token")

        # 사용자 정보 요청
        user_response = await client.get(
            user_info_url, headers={"Authorization": f"Bearer {access_token}"}
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code, detail="Failed to get user info"
            )

        user_info = user_response.json()

    request.session["user_info"] = UserInfo(
        platform=Platform.GOOGLE.value,
        name=user_info.get("name", "unknown"),
        email=user_info.get("email", "unknown"),
        image=user_info.get("picture", None),
    ).model_dump()

    return RedirectResponse(url="/")
