import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import vault_router, discovery_router, funding_router, intelligence_router

app = FastAPI(
    title="Nexus Scientific Research & Grant Intelligence API",
    version="1.0.0",
    description="Federated scientific collaboration, zero-knowledge hypothesis vaults, and autonomous grant synthesis."
)

allowed_origins_env = os.getenv("NEXUS_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router, prefix="/api/v1/vault", tags=["Vault"])
app.include_router(discovery_router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(funding_router, prefix="/api/v1/funding", tags=["Funding"])
app.include_router(intelligence_router, prefix="/api/v1/intelligence", tags=["Intelligence"])

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "nexus-api",
        "version": "1.0.0",
        "pep_enforcement": "active",
        "lattice_version": "v1.0"
    }

if __name__ == "__main__":
    import uvicorn
    reload_flag = os.getenv("NEXUS_RELOAD", "false").lower() == "true"
    uvicorn.run("nexus_api.main:app", host="0.0.0.0", port=8000, reload=reload_flag)
