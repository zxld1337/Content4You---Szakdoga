from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database import database
from routers import auth, users, posts, comments, follows, likes
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await database.connect()
    print("Database connected.")
    
    yield
    # Shutdown
    await database.disconnect()
    print("Database disconnected.")


app = FastAPI(
    title="Content4You API",
    description="Hibrid tartalomajánló közösségi média platform API.",
    version="1.0.0",
    docs_url="/docs", 
    redoc_url="/redoc", 
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(follows.router)
app.include_router(likes.router)


@app.get("/", tags=["General"])
def root():
    return {"message": "Content API is live!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)