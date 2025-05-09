from dataclasses import dataclass, asdict
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class SummaryItem:
    id: str
    title: str
    url: str
    group: str
    tags: List[str]
    short_summary: str
    full_summary: str
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SummaryItem':
        """Create a SummaryItem from a dictionary"""
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert SummaryItem to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert SummaryItem to JSON string"""
        return json.dumps(self.to_dict(), default=str)