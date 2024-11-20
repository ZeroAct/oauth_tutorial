import os
from urllib.parse import parse_qs, urlparse

import httpx
import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from enums import Platform
from scheme import UserInfo

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")


router = APIRouter()


@router.get("/login")
async def login():
    """
    네이버 로그인 URL로 리다이렉트
    """
    auth_url = (
        f"https://nid.naver.com/oauth2.0/authorize"
        f"?client_id={NAVER_CLIENT_ID}&redirect_uri={NAVER_REDIRECT_URI}&state={NAVER_CLIENT_SECRET}&response_type=code"
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
async def callback(code: str, request: Request):
    """
    네이버 인증 후 리다이렉트 콜백
    """
    token_url = "https://nid.naver.com/oauth2.0/token"
    # user_info_url = "https://kapi.kakao.com/v2/user/me"

    # Access Token 요청
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": NAVER_CLIENT_ID,
                "client_secret": NAVER_CLIENT_SECRET,
                "code": code,
                "state": code,
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
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code, detail="Failed to get user info"
            )

        user_info = user_response.json()

    request.session["user_info"] = UserInfo(
        platform=Platform.NAVER.value,
        name=user_info["response"].get("name", "unknown"),
        email=user_info["response"].get("email", "unknown"),
        image=user_info["response"].get("profile_image", None),
    ).model_dump()

    return RedirectResponse(url="/")
