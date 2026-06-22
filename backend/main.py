from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

from app.database import engine, Base
from app.routes import auth, swings, drills, account

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwingCheck API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(swings.router)
app.include_router(drills.router)
app.include_router(account.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Respect the host-provided $PORT (Render/Heroku/etc.); default to 8000 locally.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
