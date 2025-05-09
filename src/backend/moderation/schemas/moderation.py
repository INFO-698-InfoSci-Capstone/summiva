"""
Moderation Schemas
=================
Pydantic models for the moderation service API.
"""
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, HttpUrl, validator
import uuid
from datetime import datetime

from backend.core.imports import setup_imports
setup_imports()

from backend.core.schemas.base import BaseModel as SummivaBaseModel


class ContentSource(str, Enum):
    """Source of the content being analyzed."""
    USER_GENERATED = "user_generated"
    WEBSITE = "website"
    DOCUMENT = "document"
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    CHAT = "chat"
    OTHER = "other"


class ModerationCategory(str, Enum):
    """Categories of content issues that can be detected."""
    PROFANITY = "profanity"
    TOXICITY = "toxicity"
    IDENTITY_ATTACK = "identity_attack"
    INSULT = "insult"
    THREAT = "threat"
    SEXUAL_EXPLICIT = "sexual_explicit"
    HATE_SPEECH = "hate_speech"
    OTHER = "other"


class ModerationOptions(SummivaBaseModel):
    """Options for content moderation analysis."""
    check_profanity: bool = Field(True, description="Check content for profanity")
    check_toxicity: bool = Field(True, description="Check content for toxicity")
    check_identity_attacks: bool = Field(True, description="Check content for identity-based attacks")
    check_threats: bool = Field(True, description="Check content for threats")
    min_confidence_threshold: float = Field(
        0.7, 
        description="Minimum confidence threshold (0-1)",
        ge=0.0, 
        le=1.0
    )
    custom_blocklist: Optional[List[str]] = Field(
        None,
        description="Custom words to add to blocklist"
    )
    language: str = Field("en", description="Language code for analysis (ISO 639-1)")

    class Config:
        schema_extra = {
            "example": {
                "check_profanity": True,
                "check_toxicity": True,
                "min_confidence_threshold": 0.7,
                "custom_blocklist": ["badword1", "badword2"],
                "language": "en"
            }
        }


class ModerationCategoryResult(SummivaBaseModel):
    """Result for a specific moderation category."""
    detected: bool = Field(..., description="Whether the issue was detected")
    confidence: float = Field(..., description="Confidence score (0-1)")
    severity: Optional[float] = Field(None, description="Severity of the issue (0-1) if detected")
    spans: Optional[List[Dict[str, int]]] = Field(
        None,
        description="Text spans where issues were detected [{'start': int, 'end': int}]"
    )


class ModerationResult(SummivaBaseModel):
    """Results from content moderation analysis."""
    flagged: bool = Field(..., description="Whether the content was flagged for any issues")
    categories: Dict[str, ModerationCategoryResult] = Field(
        ...,
        description="Results for each moderation category"
    )
    summary: str = Field(..., description="Summary of moderation results")
    model_used: str = Field(..., description="Name of the model used for analysis")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of analysis")


class ModerationRequest(SummivaBaseModel):
    """Request to analyze content for moderation issues."""
    content: str = Field(..., description="Content to analyze")
    options: Optional[ModerationOptions] = Field(
        default_factory=ModerationOptions,
        description="Moderation analysis options"
    )
    source: ContentSource = Field(
        ContentSource.OTHER,
        description="Source of the content"
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request ID"
    )

    class Config:
        schema_extra = {
            "example": {
                "content": "This is some text that needs to be analyzed for inappropriate content.",
                "options": {
                    "check_profanity": True,
                    "check_toxicity": True,
                    "min_confidence_threshold": 0.7
                },
                "source": "user_generated"
            }
        }


class ModerationResponse(SummivaBaseModel):
    """Response from content moderation analysis."""
    result: ModerationResult = Field(..., description="Moderation analysis results")
    request_id: Optional[str] = Field(None, description="Unique request ID from the request")
    original_length: int = Field(..., description="Length of the original content")


class BatchModerationRequest(SummivaBaseModel):
    """Request to analyze multiple content items for moderation."""
    items: Dict[str, str] = Field(
        ...,
        description="Dictionary of content items to analyze, with ID keys"
    )
    options: Optional[ModerationOptions] = Field(
        default_factory=ModerationOptions,
        description="Moderation analysis options"
    )
    source: ContentSource = Field(
        ContentSource.OTHER,
        description="Source of the content"
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique request ID"
    )

    class Config:
        schema_extra = {
            "example": {
                "items": {
                    "item1": "First content to analyze",
                    "item2": "Second content to analyze"
                },
                "options": {
                    "check_profanity": True,
                    "check_toxicity": True
                },
                "source": "user_generated"
            }
        }


class BatchModerationResponse(SummivaBaseModel):
    """Response for batch content moderation."""
    results: Dict[str, ModerationResult] = Field(
        ...,
        description="Dictionary of results keyed by content ID"
    )
    request_id: Optional[str] = Field(None, description="Unique request ID from the request")