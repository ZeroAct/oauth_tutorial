import os

import dotenv

dotenv.load_dotenv()

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from auth import get_user_info, router
from scheme import UserInfo

SECRET_KEY = os.getenv("SECRET_KEY")
templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static"), name="static")
app.include_router(router, prefix="/auth", tags=["auth"])
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.get("/")
async def index(request: Request, user_info: UserInfo = Depends(get_user_info)):
    if user_info is None:
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        return templates.TemplateResponse("index.html", {"request": request, "user_info": user_info})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
