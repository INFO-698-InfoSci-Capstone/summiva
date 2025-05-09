import json
import uuid
import os
import requests
from typing import List, Optional, Literal

from models.summary import SummaryItem
from services.auth_service import get_auth_headers
from config.settings import (
    SUMMARY_SERVICE_URL, TAGGING_SERVICE_URL, 
    GROUPING_SERVICE_URL, SEARCH_SERVICE_URL, 
    DB_FILE, logger
)

# Global state for summaries
summary_list: List[SummaryItem] = []

def load_summaries() -> List[SummaryItem]:
    """Load summaries from local storage or backend"""
    global summary_list
    
    # Try to load from backend first if authenticated
    auth_headers = get_auth_headers()
    if auth_headers:
        try:
            response = requests.get(
                f"{SUMMARY_SERVICE_URL}/summaries", 
                headers=auth_headers
            )
            if response.status_code == 200:
                data = response.json()
                summary_list = [SummaryItem.from_dict(item) for item in data]
                logger.info(f"Loaded {len(summary_list)} summaries from backend")
                return summary_list
        except Exception as e:
            logger.error(f"Failed to load summaries from backend: {e}")
    
    # Fall back to local file
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                summary_list = [SummaryItem.from_dict(item) for item in data]
                logger.info(f"Loaded {len(summary_list)} summaries from local file")
                return summary_list
        except Exception as e:
            logger.error(f"Failed to load summaries from local file: {e}")
    
    return []

def save_summaries() -> bool:
    """Save summaries to local storage and sync with backend if authenticated"""
    global summary_list
    
    # Save to local file
    success = True
    try:
        with open(DB_FILE, 'w') as f:
            json.dump([item.to_dict() for item in summary_list], f, indent=2)
            logger.info(f"Saved {len(summary_list)} summaries to local file")
    except Exception as e:
        logger.error(f"Failed to save summaries to local file: {e}")
        success = False
    
    # Sync with backend if authenticated
    auth_headers = get_auth_headers()
    if auth_headers:
        try:
            for item in summary_list:
                response = requests.post(
                    f"{SUMMARY_SERVICE_URL}/summaries", 
                    json=item.to_dict(),
                    headers=auth_headers
                )
                if response.status_code not in (200, 201):
                    logger.warning(f"Failed to sync summary {item.id}: {response.status_code}")
                    success = False
        except Exception as e:
            logger.error(f"Failed to sync summaries with backend: {e}")
            success = False
    
    return success

def generate_summary(url: str) -> Optional[SummaryItem]:
    """Generate summary using backend summarization service"""
    try:
        # Request summary from backend
        summary_response = requests.post(
            f"{SUMMARY_SERVICE_URL}/generate", 
            json={"url": url},
            headers=get_auth_headers()
        )
        
        if summary_response.status_code != 200:
            logger.warning(f"Failed to generate summary: {summary_response.status_code}")
            return None
            
        summary_data = summary_response.json()
        
        # Request tags from tagging service
        tags_response = requests.post(
            f"{TAGGING_SERVICE_URL}/extract", 
            json={"text": summary_data["full_summary"]},
            headers=get_auth_headers()
        )
        
        tags = ["untagged"]
        if tags_response.status_code == 200:
            tags = tags_response.json().get("tags", ["untagged"])
        
        # Request grouping from grouping service
        group_response = requests.post(
            f"{GROUPING_SERVICE_URL}/classify", 
            json={"text": summary_data["full_summary"]},
            headers=get_auth_headers()
        )
        
        group = "Uncategorized"
        if group_response.status_code == 200:
            group = group_response.json().get("group", "Uncategorized")
        
        # Create new summary item
        return SummaryItem(
            id=str(uuid.uuid4()),
            title=summary_data.get("title", f"Summary of {url}"),
            url=url,
            group=group,
            tags=tags,
            short_summary=summary_data.get("short_summary", "No short summary available"),
            full_summary=summary_data.get("full_summary", "No full summary available")
        )
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None

def add_summary(url: str) -> Optional[SummaryItem]:
    """Add a new summary either via API or fallback to dummy data"""
    global summary_list
    try:
        # Try to generate via API
        summary_item = generate_summary(url)
        if not summary_item:
            # Fallback to dummy data if API fails
            summary_item = SummaryItem(
                id=str(uuid.uuid4()),
                title=f"Summary of {url}",
                url=url,
                group="AI",
                tags=["NLP", "ML"],
                short_summary="Short summary of the document...",
                full_summary="Full generated summary from the input URL."
            )
        
        summary_list.append(summary_item)
        save_summaries()
        return summary_item
    except Exception as e:
        logger.error(f"Error adding summary: {e}")
        return None

def search_summaries(query: str, field: Literal["title", "content", "tags", "group"]) -> List[SummaryItem]:
    """Search summaries locally or via backend search service"""
    auth_headers = get_auth_headers()
    if auth_headers:
        try:
            # Use backend search service if authenticated
            response = requests.post(
                f"{SEARCH_SERVICE_URL}/search", 
                json={"query": query, "field": field},
                headers=auth_headers
            )
            
            if response.status_code == 200:
                results = response.json()
                return [SummaryItem.from_dict(item) for item in results]
        except Exception as e:
            logger.error(f"Search API error: {e}")
    
    # Fall back to local search
    results = []
    q = query.lower()
    for item in summary_list:
        if field == "title" and q in item.title.lower():
            results.append(item)
        elif field == "content" and q in item.full_summary.lower():
            results.append(item)
        elif field == "tags" and any(q in t.lower() for t in item.tags):
            results.append(item)
        elif field == "group" and q in item.group.lower():
            results.append(item)
    return results

def get_all_tags() -> List[str]:
    """Get all unique tags across all summaries"""
    return sorted(list(set(tag for s in summary_list for tag in s.tags)))

def get_all_groups() -> List[str]:
    """Get all unique groups across all summaries"""
    return sorted(list(set(s.group for s in summary_list)))

def get_summary_by_id(summary_id: str) -> Optional[SummaryItem]:
    """Find a summary by ID"""
    for item in summary_list:
        if item.id == summary_id:
            return item
    return None