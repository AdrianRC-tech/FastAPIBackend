from fastapi import FastAPI
from app.routers import users

app = FastAPI(
    title="SendCloud Assignment - Rate Limiting API",
    description="API with user management and rate limiting capabilities (10 requests per 60 seconds)",
    version="1.0.0"
)

# Routers
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Hey! Welcome to my SendCloud Backend API assignment"}