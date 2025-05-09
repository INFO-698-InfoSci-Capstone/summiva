"""
Moderation Service
=================
Core implementation of content moderation services.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
import asyncio
import logging
import re
from pydantic import HttpUrl
from datetime import datetime
import os
import json
from functools import lru_cache
import numpy as np

from backend.core.imports import setup_imports
setup_imports()

from config.logs.logging import setup_logging
from config.settings import settings
from backend.moderation.schemas.moderation import (
    ModerationResult,
    ModerationCategoryResult,
    ModerationOptions,
    ContentSource,
    ModerationCategory
)

# Configure logger
logger = setup_logging("moderation.service")

# Global variables for model and processor instances
profanity_filter = None
toxicity_model = None
toxicity_tokenizer = None
scraper = None
safe_scraper = None

class ModerationService:
    """
    Service for content moderation using multiple tools:
    - better-profanity for profanity detection and filtering
    - Jigsaw Toxicity BERT for toxicity detection
    - trafilatura for web scraping
    - Safe-Scraper for safe content extraction from web
    """

    # Class-level cache for model instances
    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(ModerationService, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls):
        """Initialize all moderation models and components."""
        if cls._initialized:
            logger.info("Moderation service already initialized")
            return

        logger.info("Initializing moderation service...")

        # Import libraries here to delay loading until needed
        try:
            # Initialize better-profanity
            from better_profanity import profanity
            global profanity_filter
            profanity_filter = profanity
            profanity_filter.load_censor_words()
            logger.info("Successfully loaded better-profanity filter")

            # Initialize Jigsaw Toxicity BERT if requested
            if getattr(settings, "ENABLE_TOXICITY_MODEL", True):
                try:
                    from transformers import AutoTokenizer, AutoModelForSequenceClassification
                    import torch
                    
                    global toxicity_model, toxicity_tokenizer
                    
                    model_path = getattr(settings, "TOXICITY_MODEL_PATH", "unitary/toxic-bert")
                    
                    # Load the model and tokenizer with optimizations
                    logger.info(f"Loading toxicity model from {model_path}...")
                    
                    toxicity_tokenizer = AutoTokenizer.from_pretrained(model_path)
                    
                    # Use INT4 quantization if available with optimum library
                    try:
                        from optimum.bettertransformer import BetterTransformer
                        
                        # Load the model with FP16 precision for better performance
                        toxicity_model = AutoModelForSequenceClassification.from_pretrained(
                            model_path, 
                            torch_dtype=torch.float16
                        )
                        
                        # Convert to better transformer for additional optimizations
                        toxicity_model = BetterTransformer.transform(toxicity_model)
                        logger.info("Using optimized BetterTransformer for toxicity model")
                    except ImportError:
                        # Fall back to standard loading
                        toxicity_model = AutoModelForSequenceClassification.from_pretrained(model_path)
                        logger.info("Using standard transformer for toxicity model")
                    
                    # Move to GPU if available
                    if torch.cuda.is_available():
                        toxicity_model.to("cuda")
                        logger.info("Toxicity model loaded on GPU")
                    else:
                        logger.info("Toxicity model loaded on CPU")
                        
                    logger.info("Successfully loaded Jigsaw Toxicity BERT model")
                except Exception as e:
                    logger.error(f"Error loading toxicity model: {str(e)}")
                    logger.warning("Will fall back to profanity filter only")
            else:
                logger.info("Toxicity model disabled in settings")
                
            # Initialize trafilatura for web scraping
            try:
                import trafilatura
                global scraper
                scraper = trafilatura
                logger.info("Successfully loaded trafilatura scraper")
            except ImportError as e:
                logger.error(f"Error loading trafilatura: {str(e)}")
                logger.warning("Web scraping functionality will be limited")
                
            # Initialize Safe-Scraper for safe content extraction
            try:
                from safe_scraper import SafeScraper
                global safe_scraper
                
                safe_scraper_config = {
                    "content_filters": ["adult", "spam", "malicious"],
                    "safety_level": getattr(settings, "SAFE_SCRAPER_SAFETY_LEVEL", "strict"),
                    "timeout": getattr(settings, "SAFE_SCRAPER_TIMEOUT", 30),
                    "max_content_size": getattr(settings, "SAFE_SCRAPER_MAX_SIZE", 5 * 1024 * 1024),  # 5MB default
                    "user_agent": getattr(settings, "SAFE_SCRAPER_USER_AGENT", 
                                         "Summiva/1.0.0 (+https://summiva.com/bot)"),
                }
                
                safe_scraper = SafeScraper(**safe_scraper_config)
                logger.info("Successfully initialized Safe-Scraper")
            except ImportError as e:
                logger.error(f"Error loading Safe-Scraper: {str(e)}")
                logger.warning("Safe web content extraction will be limited")

            cls._initialized = True
            logger.info("Moderation service initialization completed")
        
        except Exception as e:
            logger.error(f"Error during moderation service initialization: {str(e)}")
            raise RuntimeError(f"Failed to initialize moderation service: {str(e)}")

    @classmethod
    async def cleanup(cls):
        """Clean up resources used by moderation service."""
        global profanity_filter, toxicity_model, toxicity_tokenizer, scraper, safe_scraper
        
        logger.info("Cleaning up moderation service resources...")
        
        # Clean up toxicity model
        if toxicity_model is not None:
            import torch
            
            # Release GPU memory if possible
            if hasattr(toxicity_model, "to"):
                toxicity_model.to("cpu")
                
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            toxicity_model = None
            toxicity_tokenizer = None
            logger.info("Toxicity model resources released")
            
        # Reset other components
        profanity_filter = None
        scraper = None
        safe_scraper = None
        
        cls._initialized = False
        logger.info("Moderation service cleanup completed")

    async def get_health(self) -> Dict[str, Any]:
        """
        Check health of all moderation components.
        
        Returns:
            Dict containing health information for each component
        """
        health_info = {
            "status": "healthy",
            "components": {
                "profanity_filter": "not_loaded",
                "toxicity_model": "not_loaded",
                "web_scraper": "not_loaded",
                "safe_scraper": "not_loaded"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check profanity filter
        if profanity_filter is not None:
            try:
                profanity_filter.contains_profanity("test")
                health_info["components"]["profanity_filter"] = "healthy"
            except Exception as e:
                health_info["components"]["profanity_filter"] = f"error: {str(e)}"
                health_info["status"] = "degraded"
                
        # Check toxicity model
        if toxicity_model is not None and toxicity_tokenizer is not None:
            try:
                # Light check - just verify the model exists and has expected methods
                if hasattr(toxicity_model, "forward") and hasattr(toxicity_tokenizer, "encode"):
                    health_info["components"]["toxicity_model"] = "healthy"
                else:
                    health_info["components"]["toxicity_model"] = "error: incomplete model"
                    health_info["status"] = "degraded"
            except Exception as e:
                health_info["components"]["toxicity_model"] = f"error: {str(e)}"
                health_info["status"] = "degraded"
        elif getattr(settings, "ENABLE_TOXICITY_MODEL", True):
            health_info["components"]["toxicity_model"] = "not_initialized"
            health_info["status"] = "degraded"
        else:
            health_info["components"]["toxicity_model"] = "disabled"
            
        # Check web scraper
        if scraper is not None:
            try:
                # Just check if the module has the expected function
                if hasattr(scraper, "fetch_url"):
                    health_info["components"]["web_scraper"] = "healthy"
                else:
                    health_info["components"]["web_scraper"] = "error: missing fetch_url"
                    health_info["status"] = "degraded"
            except Exception as e:
                health_info["components"]["web_scraper"] = f"error: {str(e)}"
                health_info["status"] = "degraded"
                
        # Check safe scraper
        if safe_scraper is not None:
            try:
                # Check if the instance has the expected methods
                if hasattr(safe_scraper, "scrape") and hasattr(safe_scraper, "is_safe_url"):
                    health_info["components"]["safe_scraper"] = "healthy"
                else:
                    health_info["components"]["safe_scraper"] = "error: missing methods"
                    health_info["status"] = "degraded"
            except Exception as e:
                health_info["components"]["safe_scraper"] = f"error: {str(e)}"
                health_info["status"] = "degraded"
                
        return health_info

    async def analyze_content(
        self,
        content: str,
        options: Optional[ModerationOptions] = None,
        source: ContentSource = ContentSource.OTHER
    ) -> ModerationResult:
        """
        Analyze content for moderation issues.
        
        Args:
            content: Text content to analyze
            options: Moderation options
            source: Source of the content
            
        Returns:
            ModerationResult with analysis results
        """
        if not self._initialized:
            await self.initialize()
            
        options = options or ModerationOptions()
        
        logger.debug(f"Analyzing content (length: {len(content)}, source: {source})")
        
        # Results by category
        results = {}
        any_flagged = False
        
        # Check profanity if enabled
        if options.check_profanity and profanity_filter is not None:
            try:
                # Update custom blocklist if provided
                if options.custom_blocklist:
                    profanity_filter.add_censor_words(options.custom_blocklist)
                    
                # Check profanity
                has_profanity = profanity_filter.contains_profanity(content)
                
                # Get spans where profanity was detected (if possible)
                spans = []
                try:
                    # This is a simplification; better-profanity doesn't directly provide spans
                    # but we can approximate by finding censored words
                    censored = profanity_filter.censor(content, '*')
                    
                    # Find censored spans by comparing original and censored strings
                    span_start = None
                    for i, (orig_char, censored_char) in enumerate(zip(content, censored)):
                        if orig_char != censored_char:
                            if span_start is None:
                                span_start = i
                        elif span_start is not None:
                            spans.append({"start": span_start, "end": i})
                            span_start = None
                    
                    # Handle case where profanity is at the end of the string
                    if span_start is not None:
                        spans.append({"start": span_start, "end": len(content)})
                        
                except Exception as span_error:
                    logger.warning(f"Error extracting profanity spans: {str(span_error)}")
                
                # Create category result
                results[ModerationCategory.PROFANITY] = ModerationCategoryResult(
                    detected=has_profanity,
                    confidence=1.0 if has_profanity else 0.0,  # better-profanity is rule-based
                    severity=0.7 if has_profanity else None,
                    spans=spans if has_profanity and spans else None
                )
                
                if has_profanity:
                    any_flagged = True
                    
            except Exception as e:
                logger.error(f"Error during profanity analysis: {str(e)}")
                results[ModerationCategory.PROFANITY] = ModerationCategoryResult(
                    detected=False,
                    confidence=0.0,
                    severity=None,
                    spans=None
                )
        
        # Check toxicity if enabled
        if options.check_toxicity and toxicity_model is not None and toxicity_tokenizer is not None:
            try:
                import torch
                
                # Tokenize and run inference
                inputs = toxicity_tokenizer(content, return_tensors="pt", truncation=True, max_length=512)
                
                # Move to same device as model
                device = next(toxicity_model.parameters()).device
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Run inference
                with torch.no_grad():
                    outputs = toxicity_model(**inputs)
                    
                # Convert logits to probabilities
                probabilities = torch.nn.functional.sigmoid(outputs.logits)
                
                # Determine if any category exceeds threshold
                confidence = probabilities.item()
                detected = confidence >= options.min_confidence_threshold
                
                results[ModerationCategory.TOXICITY] = ModerationCategoryResult(
                    detected=detected,
                    confidence=confidence,
                    severity=confidence if detected else None,
                    spans=None  # BERT models don't directly provide spans
                )
                
                if detected:
                    any_flagged = True
                    
                # Additional categories if using a multi-label toxicity model
                if probabilities.shape[1] > 1:
                    # Map model outputs to our categories based on common Jigsaw categories
                    category_mapping = {
                        0: ModerationCategory.TOXICITY,
                        1: ModerationCategory.THREAT,
                        2: ModerationCategory.IDENTITY_ATTACK,
                        3: ModerationCategory.INSULT,
                        4: ModerationCategory.SEXUAL_EXPLICIT,
                        5: ModerationCategory.HATE_SPEECH
                    }
                    
                    # Create results for each category
                    for idx, category_enum in category_mapping.items():
                        if idx < probabilities.shape[1]:
                            conf_value = probabilities[0, idx].item()
                            cat_detected = conf_value >= options.min_confidence_threshold
                            
                            results[category_enum] = ModerationCategoryResult(
                                detected=cat_detected,
                                confidence=conf_value,
                                severity=conf_value if cat_detected else None,
                                spans=None
                            )
                            
                            if cat_detected:
                                any_flagged = True
                
            except Exception as e:
                logger.error(f"Error during toxicity analysis: {str(e)}")
                results[ModerationCategory.TOXICITY] = ModerationCategoryResult(
                    detected=False,
                    confidence=0.0,
                    severity=None,
                    spans=None
                )
        
        # Create a summary
        summary = self._create_summary(results, any_flagged)
        
        # Determine which model was used
        model_used = []
        if profanity_filter is not None and options.check_profanity:
            model_used.append("better-profanity")
        if toxicity_model is not None and options.check_toxicity:
            model_used.append("jigsaw-toxicity-bert")
        
        # Create final result
        return ModerationResult(
            flagged=any_flagged,
            categories=results,
            summary=summary,
            model_used=", ".join(model_used) if model_used else "none",
            processed_at=datetime.utcnow()
        )

    async def filter_content(
        self,
        content: str,
        placeholder: str = "***",
        options: Optional[ModerationOptions] = None
    ) -> str:
        """
        Filter inappropriate content from text.
        
        Args:
            content: Text content to filter
            placeholder: String to use as replacement for inappropriate content
            options: Moderation options
            
        Returns:
            Filtered text content
        """
        if not self._initialized:
            await self.initialize()
            
        options = options or ModerationOptions()
        
        # Initialize filtered content with original content
        filtered_content = content
        
        # Apply profanity filter if enabled
        if options.check_profanity and profanity_filter is not None:
            try:
                # Update custom blocklist if provided
                if options.custom_blocklist:
                    profanity_filter.add_censor_words(options.custom_blocklist)
                    
                # Filter profanity
                filtered_content = profanity_filter.censor(content, placeholder)
            except Exception as e:
                logger.error(f"Error during profanity filtering: {str(e)}")
        
        # For toxicity filtering, we would need to identify toxic spans
        # which is more complex - for now, we rely on profanity filtering
        
        return filtered_content

    async def scrape_and_analyze(
        self,
        url: HttpUrl,
        options: Optional[ModerationOptions] = None
    ) -> Tuple[str, ModerationResult]:
        """
        Scrape content from URL and analyze it.
        
        Args:
            url: URL to scrape
            options: Moderation options
            
        Returns:
            Tuple of (scraped_content, moderation_result)
        """
        if not self._initialized:
            await self.initialize()
            
        # Use Safe-Scraper if available, otherwise fall back to trafilatura
        if safe_scraper is not None:
            return await self._safe_scrape_and_analyze(url, options)
        elif scraper is not None:
            return await self._trafilatura_scrape_and_analyze(url, options)
        else:
            raise RuntimeError("No web scraper (trafilatura or Safe-Scraper) is available")

    async def _safe_scrape_and_analyze(
        self,
        url: HttpUrl,
        options: Optional[ModerationOptions] = None
    ) -> Tuple[str, ModerationResult]:
        """
        Scrape content from URL using Safe-Scraper and analyze it.
        
        Args:
            url: URL to scrape
            options: Moderation options
            
        Returns:
            Tuple of (scraped_content, moderation_result)
        """
        logger.info(f"Safely scraping content from URL using Safe-Scraper: {url}")
        
        try:
            # First check if URL is safe to scrape
            is_safe = await asyncio.to_thread(safe_scraper.is_safe_url, str(url))
            if not is_safe:
                raise ValueError(f"URL failed safety check: {url}")
                
            # Scrape content safely
            result = await asyncio.to_thread(safe_scraper.scrape, str(url))
            
            if not result.content:
                raise ValueError(f"No content extracted from URL: {url}")
                
            content = result.content
            
            # Check if there were safety issues detected
            if result.safety_issues:
                logger.warning(f"Safety issues detected for URL {url}: {result.safety_issues}")
                
                # Auto-create a moderation result based on safety issues
                categories = {}
                
                for issue in result.safety_issues:
                    if "adult" in issue.lower() or "sexual" in issue.lower():
                        categories[ModerationCategory.SEXUAL_EXPLICIT] = ModerationCategoryResult(
                            detected=True,
                            confidence=0.95,
                            severity=0.9,
                            spans=None
                        )
                    elif "malicious" in issue.lower():
                        categories[ModerationCategory.OTHER] = ModerationCategoryResult(
                            detected=True,
                            confidence=0.95,
                            severity=0.9,
                            spans=None
                        )
                
                # Create result with safety issues
                safety_result = ModerationResult(
                    flagged=True,
                    categories=categories,
                    summary=f"Content flagged by Safe-Scraper: {', '.join(result.safety_issues)}",
                    model_used="safe-scraper",
                    processed_at=datetime.utcnow()
                )
                
                return content, safety_result
            
            logger.info(f"Successfully scraped content from URL: {url} (length: {len(content)})")
            
            # Perform regular content moderation
            moderation_result = await self.analyze_content(
                content=content,
                options=options,
                source=ContentSource.WEBSITE
            )
            
            return content, moderation_result
            
        except Exception as e:
            logger.error(f"Error safely scraping URL {url}: {str(e)}")
            raise RuntimeError(f"Error safely scraping URL: {str(e)}")

    async def _trafilatura_scrape_and_analyze(
        self,
        url: HttpUrl,
        options: Optional[ModerationOptions] = None
    ) -> Tuple[str, ModerationResult]:
        """
        Scrape content from URL using trafilatura and analyze it.
        
        Args:
            url: URL to scrape
            options: Moderation options
            
        Returns:
            Tuple of (scraped_content, moderation_result)
        """
        logger.info(f"Scraping content from URL using trafilatura: {url}")
        
        try:
            # Use trafilatura to safely scrape content
            downloaded = scraper.fetch_url(str(url))
            if downloaded is None:
                raise ValueError(f"Failed to fetch URL: {url}")
                
            # Extract main text content
            content = scraper.extract(downloaded)
            
            if not content:
                raise ValueError(f"No content extracted from URL: {url}")
                
            logger.info(f"Successfully scraped content from URL: {url} (length: {len(content)})")
            
            # Analyze the scraped content
            result = await self.analyze_content(
                content=content,
                options=options,
                source=ContentSource.WEBSITE
            )
            
            return content, result
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise RuntimeError(f"Error scraping URL: {str(e)}")

    def _create_summary(self, results: Dict[str, ModerationCategoryResult], any_flagged: bool) -> str:
        """Create a human-readable summary of moderation results."""
        if not any_flagged:
            return "No moderation issues detected."
            
        detected_issues = [
            category.split(".")[-1].replace("_", " ").capitalize()
            for category, result in results.items()
            if result.detected
        ]
        
        if detected_issues:
            return f"Content flagged for: {', '.join(detected_issues)}."
        else:
            return "Content flagged for moderation review."