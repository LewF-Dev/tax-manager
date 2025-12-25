"""Authentication routes."""
from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.database import get_db
from app.models.user import User
from app.core.config import settings

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

# Lazy initialize Supabase client
def get_supabase() -> Client:
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Login page."""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
    })


@router.post("/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle login."""
    try:
        # Authenticate with Supabase
        supabase = get_supabase()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        
        if not response.user:
            return RedirectResponse(url="/login?error=Invalid credentials", status_code=303)
        
        # Check if user exists in our database
        user = db.query(User).filter(User.supabase_id == response.user.id).first()
        if not user:
            return RedirectResponse(url="/login?error=User not found", status_code=303)
        
        # Set session cookie with JWT token
        redirect = RedirectResponse(url="/dashboard", status_code=303)
        redirect.set_cookie(
            key="access_token",
            value=response.session.access_token,
            httponly=True,
            max_age=3600,  # 1 hour
            samesite="lax"
        )
        return redirect
        
    except Exception as e:
        return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, error: str = None):
    """Signup page."""
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "error": error,
    })


@router.post("/auth/signup")
async def signup(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Handle signup."""
    try:
        # Create user in Supabase Auth
        supabase = get_supabase()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        
        if not response.user:
            return RedirectResponse(url="/signup?error=Signup failed", status_code=303)
        
        # Create user in our database
        user = User(
            supabase_id=response.user.id,
            email=email,
            full_name=full_name,
            subscription_status="active",  # For testing
        )
        db.add(user)
        db.commit()
        
        return RedirectResponse(url="/login?success=Account created", status_code=303)
        
    except Exception as e:
        return RedirectResponse(url=f"/signup?error={str(e)}", status_code=303)


@router.get("/logout")
async def logout():
    """Handle logout."""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except:
        pass
    return RedirectResponse(url="/login", status_code=303)
