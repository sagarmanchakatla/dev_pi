from fastapi import FastAPI

app = FastAPI(
    title="Platform API",
    description="Production-grade SaaS API",
    version="0.1.0"
)

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}
