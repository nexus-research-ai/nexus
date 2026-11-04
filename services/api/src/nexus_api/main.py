from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import vault_router, discovery_router, funding_router, intelligence_router, literature_router

app = FastAPI(
    title="Nexus Scientific Research & Grant Intelligence API",
    version="1.0.0",
    description="Federated scientific collaboration, zero-knowledge hypothesis vaults, and autonomous grant synthesis."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vault_router, prefix="/api/v1/vault", tags=["Vault"])
app.include_router(discovery_router, prefix="/api/v1/discovery", tags=["Discovery"])
app.include_router(funding_router, prefix="/api/v1/funding", tags=["Funding"])
app.include_router(intelligence_router, prefix="/api/v1/intelligence", tags=["Intelligence"])
app.include_router(literature_router, prefix="/api/v1/literature", tags=["Literature"])

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
    uvicorn.run("nexus_api.main:app", host="0.0.0.0", port=8000, reload=True)
