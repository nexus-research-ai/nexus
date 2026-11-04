from fastapi import APIRouter
from pydantic import BaseModel
from nexus_workspace.priority_proof import PriorityProofEngine
from nexus_workspace.vault import PrivateVault

router = APIRouter()
vault = PrivateVault()

class SealRequest(BaseModel):
    hypothesis: str
    author_id: str
    institution: str

@router.post("/seal")
def seal_hypothesis(req: SealRequest):
    proof = vault.seal_hypothesis(req.hypothesis, req.author_id, req.institution)
    return {"status": "sealed", "proof": proof}

@router.get("/proof/{cert_number}")
def get_proof(cert_number: str):
    proof = vault.get_proof(cert_number)
    if not proof:
        return {"error": "Certificate not found"}
    return proof
