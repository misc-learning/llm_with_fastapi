import os
import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from analytics import (
    cache_query,
    get_analytics_summary,
    get_cached_query,
    get_user_history,
    track_request,
)
from auth import create_access_token, get_current_user, require_admin, user_db
from models import (
    DashboardResponse,
    HealthResponse,
    HistoryResponse,
    LoginRequest,
    QueryRequest,
    QueryResponse,
    TokenResponse,
)
from retrieval import execute_query, initialize_retrieval

# setup logging
logger.add("log/main.log")

# initialize app
app = FastAPI(
    title="LLM with FastAPI",
    version="1.0",
    description="Advanced AI Data Pipeline with authentification and monitoring",
)

# mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}")


# initialize retrieval system on startup
@app.on_event("startup")
async def startup_event():
    """Initialize retrieval system on app startup."""
    initialize_retrieval()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean on app shutdown."""
    logger.info("Application shtting down")


# authentification endpoints
@app.post("/token", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """Login endpoint to obtain JWT token (accepts json)

    Args:
        credentials (LoginRequest): _description_
    """
    user = user_db.get(credentials.username)
    if not user or user["password"] != credentials.password:
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        {"sub": credentials.username, "role": user["role"]}
    )
    logger.info(f"User {credentials.username} logged in successfully")
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}


# query endpoints
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest, user: dict = Depends(get_current_user)):
    """Query endpoint with caching and performance tracking

    Args:
        request (QueryRequest): _description_
        user (dict, optional): _description_. Defaults to Depends(get_current_user).
    """
    start_time = time.time()
    cache_key = f"{request.question}:{user['username']}"

    # check cache first
    cached_result = get_cached_query(cache_key)
    if cached_result:
        logger.info(f"Cache hit for query : {request.question[:50]}")
        return {
            "question": request.question,
            "answer": cached_result["answer"],
            "cached": True,
            "response_time": 0.001,
            "user": user["username"],
        }

    try:
        logger.info(f"User {user['username']} asked: {request.question}")
        answer = execute_query(request.question)
        # cache the result
        cache_query(cache_key, answer, user["username"])

        elapsed_time = time.time() - start_time

        # track request history =>
        track_request(user["username"], request.question, elapsed_time)

        return {
            "question": request.question,
            "answer": answer,
            "cached": False,
            "response_time": elapsed_time,
            "user": user["username"],
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/history", response_model=HistoryResponse)
async def get_history(user: dict = Depends(get_current_user)):
    """Get query history for current user

    Args:
        user (dict, optional): _description_. Defaults to Depends(get_current_user).
    """
    history = get_user_history(user["username"])
    return {
        "user": user["username"],
        "query_count": len(history),
        "history": history[-10:],
    }


# health and monitorung endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check point"""
    analytics = get_analytics_summary()
    return {
        "status": "healthy",
        "query_engine_initialized": True,
        "cached_queries": analytics["cached_queries"],
    }


@app.get("/dashboard", response_model=DashboardResponse)
async def dashboard(user: dict = Depends(get_current_user)):
    """Advanced monitoring dashboard with detailed metrics

    Args:
        user (dict, optional): _description_. Defaults to Depends(get_current_user).
    """
    analytics = get_analytics_summary()
    return {
        "status": "Pipeline running",
        "user": user["username"],
        "role": user["role"],
        "total_queries": analytics["total_queries"],
        "total_users": analytics["total_users"],
        "cached_queries": analytics["cached_queries"],
        "avg_response_time": analytics["avg_response_time"],
    }


@app.get("/admin/stats")
async def admin_stats(user: dict = Depends(require_admin)):
    """Admin only endpoint for comprehensive statistics

    Args:
        user (dict, optional): _description_. Defaults to Depends(require_admin).
    """
    analytics = get_analytics_summary()
    return {
        "admin": user["username"],
        "total_requests": analytics["total_requests"],
        "cached_queries": analytics["cached_queries"],
        "cache_size": analytics["cache_size"],
        "avg_response_time": analytics["avg_response_time"],
    }


# landing page
@app.get("/", response_class=FileResponse)
async def landing_page():
    """Serve the landing page HTML"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "static", "index.html")

    logger.info(f"Attempting to serve : {html_file}")
    logger.info(f"File exists: {os.path.exists(html_file)}")

    if os.path.exists(html_file):
        return html_file
    else:
        logger.error(f"Lanfing page not found at {html_file}")
        raise HTTPException(status_code=404, detail="Landing page not found")
