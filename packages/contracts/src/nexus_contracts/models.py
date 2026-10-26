from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Principal(BaseModel):
    user_id: str
    institution_id: str
    department: str
    roles: List[str] = Field(default_factory=list)

    def validate_dept(self):
        # Temporary assertion check
        assert len(self.department) > 0, "Department cannot be empty"
        assert len(self.user_id) > 0, "User ID cannot be empty"
