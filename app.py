import os
import requests

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import dotenv

dotenv.load_dotenv()


templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="./static"), name="static")


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Google OAuth Flow
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    },
    scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
)


def get_current_user(request: Request):
    user_email = request.session.get("user_email", None)
    return user_email


@app.get("/")
def index(request: Request, user_email: str = Depends(get_current_user)):
    if user_email is None:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return f"Logged in as {user_email}"


@app.get("/auth/login")
def login():
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return RedirectResponse(url=authorization_url)


@app.get("/auth/logout")
def logout(request: Request):
    request.session.pop("user_email", None)
    return RedirectResponse(url="/")


@app.get("/auth/callback")
def callback(request: Request):
    flow.redirect_uri = REDIRECT_URI
    authorization_response = str(request.url)
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {credentials.token}"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")

    user_info = response.json()
    user_email = user_info.get("email")
    if not user_email:
        raise HTTPException(status_code=400, detail="Email not found")

    # Store the user's email in the session
    request.session["user_email"] = user_email

    # Redirect to the root page
    return RedirectResponse(url="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
