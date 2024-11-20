from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from scheme import UserInfo

from . import google, kakao, naver


def get_user_info(request: Request) -> UserInfo:
    user_info = request.session.get("user_info", None)
    return user_info


router = APIRouter()
router.include_router(google.router, prefix="/google")
router.include_router(kakao.router, prefix="/kakao")
router.include_router(naver.router, prefix="/naver")


@router.get("/login/{provider}")
def login(provider: str):
    if provider == "google":
        return RedirectResponse(url="/auth/google/login")
    elif provider == "kakao":
        return RedirectResponse(url="/auth/kakao/login")
    elif provider == "naver":
        return RedirectResponse(url="/auth/naver/login")
    else:
        raise NotImplementedError


@router.get("/logout")
def logout(request: Request):
    request.session.pop("user_info", None)
    return RedirectResponse(url="/")
