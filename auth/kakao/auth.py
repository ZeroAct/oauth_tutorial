import os
from urllib.parse import parse_qs, urlparse

import httpx
import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

from enums import Platform
from scheme import UserInfo

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")


router = APIRouter()


@router.get("/login")
async def login():
    """
    카카오 로그인 URL로 리다이렉트
    """
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_API_KEY}&redirect_uri={KAKAO_REDIRECT_URI}&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


@router.get("/callback")
async def callback(code: str, request: Request):
    """
    카카오 인증 후 리다이렉트 콜백
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    user_info_url = "https://kapi.kakao.com/v2/user/me"

    # Access Token 요청
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_API_KEY,
                "redirect_uri": KAKAO_REDIRECT_URI,
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
        platform=Platform.KAKAO.value,
        name=user_info["kakao_account"]["profile"].get("nickname", ""),
        email=user_info["kakao_account"].get("email", ""),
        image=user_info["kakao_account"]["profile"].get("profile_image_url", None),
    ).model_dump()

    return RedirectResponse(url="/")
