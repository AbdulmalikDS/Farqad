from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None
    chunk_size: Optional[int] = 50 #change from 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0