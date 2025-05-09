"""
Moderation API
=============
API endpoints for content moderation.
"""
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Security, Query, BackgroundTasks, status
from pydantic import HttpUrl

from backend.core.imports import setup_imports
setup_imports()

from backend.core.api import create_api_router
from backend.core.schemas.base import APIResponse
from backend.moderation.schemas.moderation import (
    ModerationRequest,
    ModerationResponse,
    ModerationResult,
    BatchModerationRequest,
    BatchModerationResponse,
    ModerationOptions,
    ContentSource
)
from backend.moderation.services.moderation_service import ModerationService
from config.logs.logging import setup_logging

# Setup router with standardized tags and responses
router = create_api_router(
    tags=["Moderation"],
    prefix="/moderation",
)

# Get logger for this module
logger = setup_logging("moderation.api")

@router.post(
    "/analyze", 
    response_model=APIResponse[ModerationResponse],
    summary="Analyze content for moderation",
    description="Analyze text content for profanity, toxicity, and other moderation concerns."
)
async def analyze_content(request: ModerationRequest):
    """
    Analyze content for moderation issues.
    
    - Supports profanity filtering using better-profanity
    - Supports toxicity detection using Jigsaw Toxicity BERT
    - Returns detailed analysis with confidence scores
    """
    try:
        logger.debug(f"Received moderation request for content (length: {len(request.content)})")
        
        # Get moderation service instance
        moderation_service = ModerationService()
        
        # Analyze content
        result = await moderation_service.analyze_content(
            content=request.content,
            options=request.options,
            source=request.source
        )
        
        logger.info(f"Successfully analyzed content for moderation (length: {len(request.content)})")
        return APIResponse(
            data=ModerationResponse(
                result=result,
                request_id=request.request_id,
                original_length=len(request.content)
            ),
            message="Content analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Error analyzing content for moderation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing moderation request: {str(e)}"
        )

@router.post(
    "/batch",
    response_model=APIResponse[BatchModerationResponse],
    summary="Batch analyze multiple content items",
    description="Process multiple content items for moderation in a single batch request."
)
async def batch_analyze_content(request: BatchModerationRequest):
    """
    Analyze multiple content items in a single request.
    
    - More efficient for processing multiple items
    - Returns results with the same IDs as provided in the request
    """
    try:
        logger.debug(f"Received batch moderation request with {len(request.items)} items")
        
        # Get moderation service instance
        moderation_service = ModerationService()
        
        # Process each item
        results = {}
        for item_id, content in request.items.items():
            result = await moderation_service.analyze_content(
                content=content,
                options=request.options,
                source=request.source
            )
            results[item_id] = result
        
        logger.info(f"Successfully processed batch moderation request with {len(request.items)} items")
        return APIResponse(
            data=BatchModerationResponse(
                results=results,
                request_id=request.request_id
            ),
            message="Batch moderation analysis completed successfully"
        )
    except Exception as e:
        logger.error(f"Error processing batch moderation request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch moderation request: {str(e)}"
        )

@router.post(
    "/filter",
    response_model=APIResponse[str],
    summary="Filter content for inappropriate text",
    description="Clean content by replacing inappropriate text with specified placeholder."
)
async def filter_content(
    request: ModerationRequest,
    placeholder: str = Query("***", description="Replacement text for inappropriate content")
):
    """
    Filter inappropriate content and return cleaned version.
    
    - Replaces profanity and inappropriate content with placeholder
    - Maintains original text structure and length
    """
    try:
        logger.debug(f"Received content filtering request (length: {len(request.content)})")
        
        # Get moderation service instance
        moderation_service = ModerationService()
        
        # Filter content
        filtered_content = await moderation_service.filter_content(
            content=request.content,
            placeholder=placeholder,
            options=request.options
        )
        
        logger.info(f"Successfully filtered content (length: {len(request.content)})")
        return APIResponse(
            data=filtered_content,
            message="Content filtered successfully"
        )
    except Exception as e:
        logger.error(f"Error filtering content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error filtering content: {str(e)}"
        )

@router.get(
    "/health",
    summary="Get moderation service health",
    description="Check if all moderation models and services are operational."
)
async def health_check():
    """Health check endpoint for the moderation service."""
    try:
        moderation_service = ModerationService()
        status_info = await moderation_service.get_health()
        
        return APIResponse(
            data=status_info,
            message="Moderation service is healthy"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Moderation service is unhealthy: {str(e)}"
        )

@router.get(
    "/scrape-and-analyze",
    response_model=APIResponse[ModerationResponse],
    summary="Scrape URL and analyze content",
    description="Scrape content from a URL and perform moderation analysis."
)
async def scrape_and_analyze(
    url: HttpUrl = Query(..., description="URL to scrape content from"),
    options: Optional[ModerationOptions] = None
):
    """
    Scrape content from a URL and perform moderation analysis.
    
    - Uses Safe-Scraper to safely extract content
    - Performs moderation analysis on the scraped content
    """
    try:
        logger.debug(f"Received scrape and analyze request for URL: {url}")
        
        # Get moderation service instance
        moderation_service = ModerationService()
        
        # Scrape and analyze
        content, result = await moderation_service.scrape_and_analyze(url, options)
        
        logger.info(f"Successfully scraped and analyzed content from URL: {url}")
        return APIResponse(
            data=ModerationResponse(
                result=result,
                request_id=None,
                original_length=len(content)
            ),
            message="URL content scraped and analyzed successfully"
        )
    except Exception as e:
        logger.error(f"Error scraping and analyzing URL {url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scraping and analyzing URL: {str(e)}"
        )