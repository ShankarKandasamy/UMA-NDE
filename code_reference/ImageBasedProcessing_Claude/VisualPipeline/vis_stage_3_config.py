"""
Visual Pipeline Stage 3 Configuration
======================================
Routing logic, skip rules, and prompt/schema definitions for Stage 3 visual analysis.

This config maps categories and subcategories from Stage 2 to:
- Prompt files (with version selection for diagrams/graphs/other)
- JSON schemas for structured output
- Model selection and parameters
- Skip rules for low-value images
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

# Directory containing prompts
PROMPTS_DIR = Path(__file__).parent / "vis_stage_3_prompts"

# =============================================================================
# SKIP RULES: Images that won't be sent to VLM
# =============================================================================

SKIP_RULES = {
    "other": {
        "confidence_threshold": 0.5,  # Skip if Stage 2 confidence < 0.5
        "subcategories_always_skip": ["Logo", "Icon", "Decorative", "Page Furniture"]
    },
    "photograph": {
        "subcategories_always_skip": ["Decoration"]
    }
}

def should_skip_image(main_category: str, subcategory: str, confidence: float) -> Tuple[bool, str]:
    """
    Determine if image should be skipped based on category rules.

    Returns:
        (should_skip: bool, reason: str)
    """
    if main_category in SKIP_RULES:
        rules = SKIP_RULES[main_category]

        # Check confidence threshold
        if "confidence_threshold" in rules and confidence < rules["confidence_threshold"]:
            return True, f"Confidence {confidence} below threshold {rules['confidence_threshold']}"

        # Check subcategory skip list
        if "subcategories_always_skip" in rules and subcategory in rules["subcategories_always_skip"]:
            return True, f"Subcategory '{subcategory}' is in skip list"

    return False, ""

# =============================================================================
# PROMPT VERSION SELECTION (for categories with multiple versions)
# =============================================================================

# Set which version to use: "gpt", "claude", or "gemini"
# This affects graph/chart, diagram, and other categories
PROMPT_VERSION = "claude"  # Change this to switch between versions

# =============================================================================
# PROMPT FILE MAPPING
# =============================================================================

# Mapping from Stage 2 subcategory names to normalized filename components
# Handles cases where Stage 2 uses full names but files use simplified names
SUBCATEGORY_MAPPING = {
    "photograph": {
        "Equipment / Asset Visualization": "equipment_asset",
        "Condition / Anomaly Evidence": "condition_anomaly",
        "Comparative / Before-After": "comparative_before_after",
        "Spatial / Locational Reference": "spatial_locational",
    }
}

def normalize_subcategory(main_category: str, subcategory: str) -> str:
    """
    Normalize subcategory name to match prompt filename.
    
    Handles special cases where Stage 2 subcategory names don't directly
    match the simplified filenames.
    """
    if not subcategory:
        return ""
    
    main_cat = main_category.lower().replace("/", "_")
    
    # Check for special mappings first (case-insensitive)
    if main_cat in SUBCATEGORY_MAPPING:
        # Try exact match first
        if subcategory in SUBCATEGORY_MAPPING[main_cat]:
            return SUBCATEGORY_MAPPING[main_cat][subcategory]
        # Try case-insensitive match
        subcat_lower = subcategory.lower()
        for key, value in SUBCATEGORY_MAPPING[main_cat].items():
            if key.lower() == subcat_lower:
                return value
    
    # General normalization: lowercase, replace spaces and slashes with underscores
    # Handle " / " specially to avoid triple underscores
    normalized = subcategory.lower()
    normalized = normalized.replace(" / ", "_")  # Handle " / " first
    normalized = normalized.replace("/", "_")    # Then handle remaining slashes
    normalized = normalized.replace(" ", "_")    # Then handle remaining spaces
    normalized = normalized.replace("-", "_")    # Handle hyphens
    
    # Clean up multiple consecutive underscores
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    
    # Remove leading/trailing underscores
    normalized = normalized.strip("_")
    
    return normalized

def get_prompt_file(main_category: str, subcategory: str) -> Optional[str]:
    """
    Get the prompt filename for a given category/subcategory.

    Args:
        main_category: Main category (table, graph/chart, photograph, diagram, other)
        subcategory: Subcategory (e.g., "Continuous", "Technical", "Screenshot")

    Returns:
        Filename (e.g., "graph_chart_continuous.md") or None if not found
    """
    main_cat = main_category.lower().replace("/", "_")

    # Categories with version variants (graph/chart, diagram, other)
    versioned_categories = ["graph_chart", "diagram", "other"]

    # Table has only one version
    if main_cat == "table":
        return "table.md"

    # Photographs have one version per subcategory
    if main_cat == "photograph":
        subcat_normalized = normalize_subcategory(main_category, subcategory)
        if not subcat_normalized:
            return None
        return f"photograph_{subcat_normalized}.md"

    # Versioned categories: graph/chart, diagram, other
    if main_cat in versioned_categories:
        subcat_normalized = normalize_subcategory(main_category, subcategory)
        if not subcat_normalized:
            return None
        return f"{main_cat}_{subcat_normalized}.md"

    return None

# =============================================================================
# MODEL AND PARAMETER CONFIGURATION
# =============================================================================

MODEL_CONFIG = {
    "table": {
        "model": "gpt-4o",
        "max_tokens": 2000,
        "temperature": 0.1,
        "detail": "high"
    },
    "graph_chart": {
        "model": "gpt-4o-mini",
        "max_tokens": 1500,
        "temperature": 0.1,
        "detail": "high"
    },
    "diagram": {
        "model": "gpt-4o-mini",
        "max_tokens": 1500,
        "temperature": 0.1,
        "detail": "high"
    },
    "photograph": {
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "temperature": 0.1,
        "detail": "high"
    },
    "other": {
        # Default for high-value subcategories
        "Screenshot": {"model": "gpt-4o-mini", "max_tokens": 1500, "temperature": 0.1, "detail": "high"},
        "Infographic": {"model": "gpt-4o-mini", "max_tokens": 1500, "temperature": 0.1, "detail": "high"},
        "Mixed Content": {"model": "gpt-4o-mini", "max_tokens": 1500, "temperature": 0.1, "detail": "high"},
        "Text Block": {"model": "gpt-4o-mini", "max_tokens": 800, "temperature": 0.1, "detail": "low"},
        "Unclassifiable": {"model": "gpt-4o-mini", "max_tokens": 800, "temperature": 0.1, "detail": "low"},
        "Watermark": {"model": "gpt-4o-mini", "max_tokens": 300, "temperature": 0.1, "detail": "low"},
        "Fragment": {"model": "gpt-4o-mini", "max_tokens": 500, "temperature": 0.1, "detail": "low"},
    }
}

def get_model_config(main_category: str, subcategory: str = None) -> Dict:
    """Get model configuration for a category/subcategory."""
    main_cat = main_category.lower().replace("/", "_")

    if main_cat == "other" and subcategory:
        return MODEL_CONFIG["other"].get(subcategory, MODEL_CONFIG["other"]["Unclassifiable"])

    return MODEL_CONFIG.get(main_cat, MODEL_CONFIG["other"]["Unclassifiable"])

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_prompt(prompt_file: str) -> str:
    """Load prompt from markdown file."""
    prompt_path = PROMPTS_DIR / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_analysis_config(main_category: str, subcategory: str, confidence: float = 1.0) -> Optional[Dict]:
    """
    Get complete analysis configuration for a category/subcategory.

    Returns None if image should be skipped.
    Returns dict with 'prompt', 'model', 'max_tokens', 'temperature', 'detail' otherwise.
    """
    # Check skip rules
    should_skip, reason = should_skip_image(main_category, subcategory, confidence)
    if should_skip:
        return None

    # Get prompt file
    prompt_file = get_prompt_file(main_category, subcategory)
    if not prompt_file:
        return None

    # Load prompt
    try:
        prompt = load_prompt(prompt_file)
    except FileNotFoundError:
        return None

    # Get model config
    model_config = get_model_config(main_category, subcategory)

    return {
        "prompt": prompt,
        "prompt_file": prompt_file,
        **model_config
    }

# =============================================================================
# SCHEMA MAPPING (for future use - actual schemas would be defined here)
# =============================================================================

# Note: Full JSON schemas are large. In practice, these would either be:
# 1. Included in the prompt itself (current approach)
# 2. Stored in separate schema files and loaded dynamically
# 3. Defined as Python dicts here for validation

# For now, schemas are embedded in the prompt files themselves.
# Future enhancement: separate schema files for validation after extraction.
