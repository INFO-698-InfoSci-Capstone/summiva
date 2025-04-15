 
from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    url: str | None = None
    text: str | None = None