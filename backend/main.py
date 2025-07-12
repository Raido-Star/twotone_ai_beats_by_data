"""
AI Agent Platform Backend
Main FastAPI application with comprehensive AI agent capabilities
"""

import os
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

# Import our modules
from .core.config import settings
from .core.database import get_db, init_db
from .core.security import verify_token, create_access_token
from .core.websocket import ConnectionManager
from .models.user import User
from .models.agent import Agent
from .models.conversation import Conversation
from .api.v1.agents import router as agents_router
from .api.v1.conversations import router as conversations_router
from .api.v1.users import router as users_router
from .api.v1.auth import router as auth_router
from .api.v1.chat import router as chat_router
from .api.v1.marketplace import router as marketplace_router
from .services.agent_service import AgentService
from .services.llm_service import LLMService
from .services.vector_service import VectorService
from .services.websocket_service import WebSocketService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
agent_service = AgentService()
llm_service = LLMService()
vector_service = VectorService()
websocket_service = WebSocketService()
connection_manager = ConnectionManager()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AI Agent Platform...")
    
    # Initialize database
    await init_db()
    
    # Initialize vector database
    await vector_service.initialize()
    
    # Initialize LLM service
    await llm_service.initialize()
    
    logger.info("AI Agent Platform started successfully!")
    yield
    
    logger.info("Shutting down AI Agent Platform...")
    await vector_service.close()
    await llm_service.close()
    logger.info("AI Agent Platform shut down successfully!")

# Create FastAPI app
app = FastAPI(
    title="AI Agent Platform API",
    description="Professional AI Agent Platform for building, deploying, and managing AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# API Models
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: str
    database: bool
    vector_db: bool
    llm_service: bool

class AgentCreateRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    system_prompt: str = Field(..., description="System prompt for the agent")
    model: str = Field(default="gpt-4", description="LLM model to use")
    tools: List[str] = Field(default_factory=list, description="List of tools the agent can use")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Agent settings")

class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    agent_id: str = Field(..., description="Agent ID")
    conversation_id: Optional[str] = None
    stream: bool = Field(default=False, description="Enable streaming")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    
    # Check database connection
    try:
        db_healthy = await agent_service.health_check()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False
    
    # Check vector database
    try:
        vector_healthy = await vector_service.health_check()
    except Exception as e:
        logger.error(f"Vector database health check failed: {e}")
        vector_healthy = False
    
    # Check LLM service
    try:
        llm_healthy = await llm_service.health_check()
    except Exception as e:
        logger.error(f"LLM service health check failed: {e}")
        llm_healthy = False
    
    return HealthResponse(
        timestamp=datetime.utcnow().isoformat(),
        database=db_healthy,
        vector_db=vector_healthy,
        llm_service=llm_healthy,
    )

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat/{agent_id}")
async def websocket_chat(
    websocket: WebSocket,
    agent_id: str,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time chat with agents"""
    
    # Authenticate user
    user_id = None
    if token:
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return
    
    # Accept connection
    await connection_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message
            response = await websocket_service.process_message(
                agent_id=agent_id,
                user_id=user_id,
                message=data.get("message", ""),
                conversation_id=data.get("conversation_id"),
                websocket=websocket
            )
            
            # Send response back
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=4000, reason="Internal server error")
    finally:
        await connection_manager.disconnect(websocket)

# API Routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(agents_router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(conversations_router, prefix="/api/v1/conversations", tags=["Conversations"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(marketplace_router, prefix="/api/v1/marketplace", tags=["Marketplace"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Agent Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Agent management endpoints
@app.post("/api/v1/agents/create")
async def create_agent(
    request: AgentCreateRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new AI agent"""
    try:
        agent = await agent_service.create_agent(
            user_id=user_id,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            model=request.model,
            tools=request.tools,
            settings=request.settings,
            db=db
        )
        return {"message": "Agent created successfully", "agent": agent}
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/")
async def list_agents(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's agents"""
    try:
        agents = await agent_service.get_user_agents(user_id, db)
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/")
async def chat_with_agent(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Chat with an AI agent"""
    try:
        response = await agent_service.chat_with_agent(
            user_id=user_id,
            agent_id=request.agent_id,
            message=request.message,
            conversation_id=request.conversation_id,
            stream=request.stream,
            db=db
        )
        return response
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )