from datetime import datetime
from typing import Optional, Dict, Any

class Result:
    def __init__(self, 
                 id: str,
                 crew_id: str,
                 crew_name: str,
                 inputs: Dict[str, str],
                 result: Any,
                 created_at: Optional[str] = None):
        self.id = id
        self.crew_id = crew_id
        self.crew_name = crew_name
        self.inputs = inputs
        self.result = result
        self.created_at = created_at or datetime.now().isoformat()