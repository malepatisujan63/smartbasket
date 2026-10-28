from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import engine, Base, SessionLocal
from ml.engine import ml_engine
from routers import auth, products, categories, cart, orders, users, recommendations, analytics, mlops, ai_assistant, retailers

app = FastAPI(
    title="Amazon-AI Retail Sales Intelligence Platform API",
    description="Production-grade Full-Stack E-Commerce & AI Analytics Platform with Scikit-Learn, XGBoost, and SHAP Explainability",
    version="1.0.0"
)

# CORS Middleware for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Vercel domain and localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(mlops.router)
app.include_router(ai_assistant.router)
app.include_router(retailers.router)


@app.on_event("startup")
def startup_event():
    print("Initializing Database Schema...")
    Base.metadata.create_all(bind=engine)
    
    print("Bootstrapping AI Data and Training ML Models...")
    db = SessionLocal()
    try:
        ml_engine.bootstrap_database(db)
        ml_engine.fit_recommendation_models(db)
    finally:
        db.close()
    print("Amazon-AI Backend Service is READY and Online!")


@app.get("/")
def root():
    return {
        "status": "online",
        "platform": "Amazon-AI Retail Sales Intelligence Platform",
        "version": "1.0.0",
        "message": "Welcome to the AI-Powered E-Commerce & Analytics Engine!"
    }
