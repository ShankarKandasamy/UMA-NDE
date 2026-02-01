"""
Test Script: VLM Chart Data Extraction

Tests Vision Language Models for accurate chart data extraction.
Supports multiple cloud providers and local deployment options.

================================================================================
RECOMMENDED MODELS (Based on December 2024 benchmarking)
================================================================================

Production Use:
    - Claude Opus 4.5 (Anthropic) - Best overall accuracy
    - Qwen3-VL-235B (Fireworks) - Best open-source, matches Claude
    - Qwen3-VL-32B (Together/Fireworks) - Good balance of cost/accuracy

Development/Testing:
    - GPT-4o-mini (OpenAI) - Cheapest, but lower accuracy

NOT Recommended for chart extraction:
    - DeepSeek-VL2 - Hallucinated data
    - LLaMA 3.2 Vision - Hallucinated data
    - Gemma 3 (4B/27B) - Misassigns values
    - Ministral 3 14B - Too small, generates micro-deflections

================================================================================
USAGE EXAMPLES
================================================================================

    # OpenAI models (requires OPENAI_API_KEY)
    python test_deflection_extraction.py <image_path> gpt-4o-mini
    python test_deflection_extraction.py <image_path> gpt-4o
    
    # Anthropic models (requires ANTHROPIC_API_KEY)
    python test_deflection_extraction.py <image_path> claude-opus-4-5-20251101
    
    # Together AI (requires TOGETHER_API_KEY) - RECOMMENDED
    python test_deflection_extraction.py <image_path> llama-4-maverick together
    python test_deflection_extraction.py <image_path> "Qwen/Qwen3-VL-32B-Instruct" together
    python test_deflection_extraction.py <image_path> gemma-3-4b together
    
    # Fireworks AI (requires FIREWORKS_API_KEY) - RECOMMENDED
    python test_deflection_extraction.py <image_path> qwen3-vl-235b fireworks
    python test_deflection_extraction.py <image_path> qwen3-vl-30b fireworks
    
    # Replicate (requires REPLICATE_API_KEY) - Has cold start delays
    python test_deflection_extraction.py <image_path> deepseek-vl2 replicate
    python test_deflection_extraction.py <image_path> llama-3.2-vision-90b replicate

================================================================================
KNOWN ISSUES AND FIXES
================================================================================

1. TOGETHER AI - API Key Loading
   Issue: Script couldn't find TOGETHER_API_KEY when run from subdirectory
   Fix: Load .env from project root, not current directory
   
   The script now searches for .env in parent directories:
   ```python
   load_dotenv(Path(__file__).parent.parent.parent.parent.parent / ".env")
   ```

2. REPLICATE - Cold Start Timeouts
   Issue: "Server disconnected without sending a response"
   Cause: Models on Replicate need to boot up on GPU hardware (1-3 min)
   Fix: Use predictions API with polling instead of synchronous run()
   
   ```python
   prediction = replicate.predictions.create(version=..., input=...)
   while prediction.status not in ["succeeded", "failed"]:
       time.sleep(5)
       prediction.reload()
   ```

3. REPLICATE - API Key Naming
   Issue: Script looked for REPLICATE_API_KEY but SDK uses REPLICATE_API_TOKEN
   Fix: Check both environment variable names:
   
   ```python
   api_key = os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY")
   ```

4. REPLICATE - Image Input Format
   Issue: Data URIs not accepted, only URLs or file handles
   Fix: Pass file handle directly, Replicate uploads automatically:
   
   ```python
   with open(image_path, "rb") as f:
       output = replicate.run(model, input={"image": f, ...})
   ```

5. FIREWORKS - Model ID Format
   Issue: Model IDs changed from short names to full paths
   Fix: Use full model paths like "accounts/fireworks/models/qwen3-vl-235b-a22b-instruct"

6. LLAMA 4 MAVERICK - Not Available on Replicate/Fireworks Serverless
   Issue: Model exists but requires dedicated deployment
   Fix: Use Together AI which has it in serverless:
   
   ```python
   model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
   ```

================================================================================
CLOUD PROVIDERS
================================================================================

Provider     | Best Models Available              | Pricing (approx)
-------------|-----------------------------------|------------------
Together AI  | Llama 4 Maverick, Qwen3-VL-32B    | $0.15-1.50/M tokens
Fireworks    | Qwen3-VL-235B, Qwen3-VL-30B       | $0.90/M tokens
Replicate    | DeepSeek-VL2, LLaMA 3.2 Vision    | ~$0.02-0.05/run
OpenAI       | GPT-4o, GPT-4o-mini               | $0.15-5.00/M tokens
Anthropic    | Claude Opus 4.5                   | $15-75/M tokens

================================================================================
"""

import sys
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("[WARNING] OpenAI library not found. Install with: pip install openai")
    OpenAI = None

# Anthropic
try:
    import anthropic
except ImportError:
    print("[WARNING] Anthropic library not found. Install with: pip install anthropic")
    anthropic = None

# Replicate
try:
    import replicate
except ImportError:
    print("[WARNING] Replicate library not found. Install with: pip install replicate")
    replicate = None


# The specific prompt for deflection point extraction
DEFLECTION_PROMPT = """You are analyzing a line chart showing two data series over time.

## YOUR TASK
Extract EVERY deflection point (turning point) for BOTH series in this chart.

A deflection point is ANY point where the line changes direction:
- From going UP to going DOWN (local peak)
- From going DOWN to going UP (local trough)  
- From steep slope to gentler slope
- From gentler slope to steep slope

## CRITICAL INSTRUCTIONS
1. **Extract EVERY visible deflection** - Do NOT skip any. Even small wiggles count.
2. **Estimate X and Y values carefully** using the gridlines as reference
3. **For the X-axis**: The chart shows years. Estimate the year for each deflection (e.g., 2001, 2002, 2007.5 for mid-year)
4. **For the Y-axis**: The scale goes from 0.00 to about 0.20 (these are percentages like 0.05 = 5%). Use gridlines at 0.00, 0.05, 0.10, 0.15, 0.20 as reference.

## WHAT TO EXTRACT FOR EACH SERIES
For each series (gray "Total CPI % Change" and green "Farm Land % Value Change"):
- List ALL deflection points from left to right
- For each point: {"year": approximate_year, "value": approximate_y_value, "type": "peak" | "trough" | "slope_change"}

## ESTIMATION TECHNIQUE
- Identify which two gridlines the point falls between
- Estimate the position (e.g., "60% of the way between 0.05 and 0.10 = ~0.08")
- For years between labeled ticks (2000, 2005, 2010, 2015, 2020), interpolate (e.g., 3/5 of the way from 2000 to 2005 = ~2003)

## OUTPUT FORMAT
Return ONLY valid JSON in this exact format:

```json
{
  "chart_info": {
    "title": "Chart title",
    "x_axis": {"label": "Year", "range": [start_year, end_year]},
    "y_axis": {"label": "Y-axis label", "range": [min, max]}
  },
  "series": [
    {
      "name": "Series name from legend",
      "color": "color description",
      "deflection_points": [
        {"year": 2000, "value": 0.01, "type": "start"},
        {"year": 2001, "value": 0.02, "type": "trough"},
        {"year": 2002, "value": 0.05, "type": "peak"},
        ...more points...
      ],
      "total_deflections": number
    }
  ],
  "extraction_notes": "Any notes about estimation difficulty, overlapping areas, etc."
}
```

Remember: Extract EVERY deflection, not just the major ones. A 20+ year chart should have many deflection points per series."""


def encode_image(image_path: Path) -> str:
    """Encode image to base64 string for OpenAI API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_deflection_points_anthropic(image_path: Path, model: str = "claude-opus-4-5-20251101") -> dict:
    """
    Send image to Anthropic Claude and extract deflection points.
    
    Args:
        image_path: Path to the chart image
        model: Model to use (default: claude-opus-4-5-20251101)
    
    Returns:
        Dict with extraction results
    """
    if anthropic is None:
        raise ImportError("Anthropic library not installed. Run: pip install anthropic")
    
    client = anthropic.Anthropic()
    
    # Encode image
    base64_image = encode_image(image_path)
    
    # Determine media type
    suffix = image_path.suffix.lower()
    media_type = "image/png" if suffix == ".png" else "image/jpeg"
    
    print(f"\n[INFO] Sending image to {model} (Anthropic)...")
    print(f"[INFO] Image: {image_path.name}")
    
    # Call Anthropic API
    response = client.messages.create(
        model=model,
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": DEFLECTION_PROMPT
                    }
                ]
            }
        ]
    )
    
    # Get response
    raw_output = response.content[0].text.strip()
    
    # Token usage
    usage = {
        "prompt_tokens": response.usage.input_tokens,
        "completion_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens
    }
    
    print(f"[INFO] Tokens used: {usage['total_tokens']:,}")
    
    # Try to parse JSON
    result = None
    
    # Remove markdown code blocks if present
    if "```json" in raw_output:
        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_output:
        raw_output = raw_output.split("```")[1].split("```")[0].strip()
    
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        result = {"raw_output": raw_output, "parse_error": str(e)}
    
    return {
        "model": model,
        "provider": "anthropic",
        "timestamp": datetime.now().isoformat(),
        "usage": usage,
        "result": result
    }


def extract_deflection_points_openai(image_path: Path, model: str = "gpt-4o-mini") -> dict:
    """
    Send image to OpenAI and extract deflection points.
    
    Args:
        image_path: Path to the chart image
        model: Model to use (default: gpt-4o-mini)
    
    Returns:
        Dict with extraction results
    """
    if OpenAI is None:
        raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    client = OpenAI()
    
    # Encode image
    base64_image = encode_image(image_path)
    
    print(f"\n[INFO] Sending image to {model} (OpenAI)...")
    print(f"[INFO] Image: {image_path.name}")
    
    # Build request parameters
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": DEFLECTION_PROMPT
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]
    
    # o3 and gpt-5.2 models use different parameters
    if model.startswith("o3") or model.startswith("gpt-5"):
        print("[INFO] Using reasoning model configuration (reasoning_effort=high)")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=4000,
            reasoning_effort="high"
        )
    else:
        # Standard GPT models
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=3000,
            temperature=0.1
        )
    
    # Get response
    raw_output = response.choices[0].message.content.strip()
    
    # Token usage
    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens
    }
    
    print(f"[INFO] Tokens used: {usage['total_tokens']:,}")
    
    # Try to parse JSON
    result = None
    
    # Remove markdown code blocks if present
    if "```json" in raw_output:
        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_output:
        raw_output = raw_output.split("```")[1].split("```")[0].strip()
    
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        result = {"raw_output": raw_output, "parse_error": str(e)}
    
    return {
        "model": model,
        "provider": "openai",
        "timestamp": datetime.now().isoformat(),
        "usage": usage,
        "result": result
    }


def extract_deflection_points_local(image_path: Path, model: str, base_url: str) -> dict:
    """
    Send image to a local OpenAI-compatible server (Ollama, vLLM, LM Studio).
    
    Args:
        image_path: Path to the chart image
        model: Model name as registered in the local server
        base_url: Base URL of the local server (e.g., http://localhost:11434/v1)
    
    Returns:
        Dict with extraction results
    """
    if OpenAI is None:
        raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    # Create client pointing to local server
    client = OpenAI(
        base_url=base_url,
        api_key="not-needed"  # Local servers typically don't require API key
    )
    
    # Encode image
    base64_image = encode_image(image_path)
    
    print(f"\n[INFO] Sending image to {model} (Local: {base_url})...")
    print(f"[INFO] Image: {image_path.name}")
    
    # Build request - format varies by server
    # Ollama uses same format as OpenAI for vision
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": DEFLECTION_PROMPT
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=3000,
        temperature=0.1
    )
    
    # Get response
    raw_output = response.choices[0].message.content.strip()
    
    # Token usage (may not be available for all local servers)
    usage = {
        "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0,
        "completion_tokens": getattr(response.usage, 'completion_tokens', 0) if response.usage else 0,
        "total_tokens": getattr(response.usage, 'total_tokens', 0) if response.usage else 0
    }
    
    print(f"[INFO] Tokens used: {usage['total_tokens']:,}")
    
    # Try to parse JSON
    result = None
    
    # Remove markdown code blocks if present
    if "```json" in raw_output:
        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_output:
        raw_output = raw_output.split("```")[1].split("```")[0].strip()
    
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        result = {"raw_output": raw_output, "parse_error": str(e)}
    
    return {
        "model": model,
        "provider": "local",
        "base_url": base_url,
        "timestamp": datetime.now().isoformat(),
        "usage": usage,
        "result": result
    }


# Common local server endpoints
LOCAL_SERVERS = {
    "ollama": "http://localhost:11434/v1",
    "vllm": "http://localhost:8000/v1",
    "lmstudio": "http://localhost:1234/v1",
}

# Cloud API providers for open-source models
CLOUD_PROVIDERS = {
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "env_key": "TOGETHER_API_KEY",
        "models": {
            "gemma-3-4b": "google/gemma-3n-E4B-it",
            "llama-4-maverick": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "llama-4-scout": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
            "ministral-3-14b": "mistralai/Ministral-3-14B-Instruct-2512",
            "llama-3.2-vision-11b": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            "llama-3.2-vision-90b": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            "qwen2.5-vl-72b": "Qwen/Qwen2.5-VL-72B-Instruct",
        }
    },
    "hyperbolic": {
        "base_url": "https://api.hyperbolic.xyz/v1",
        "env_key": "HYPERBOLIC_API_KEY",
        "models": {
            "qwen2.5-vl-72b": "Qwen/Qwen2-VL-72B-Instruct",
            "qwen2.5-vl-7b": "Qwen/Qwen2-VL-7B-Instruct",
        }
    },
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "env_key": "FIREWORKS_API_KEY",
        "models": {
            "qwen3-vl-235b": "accounts/fireworks/models/qwen3-vl-235b-a22b-instruct",
            "qwen3-vl-30b": "accounts/fireworks/models/qwen3-vl-30b-a3b-instruct",
            "qwen2.5-vl-32b": "accounts/fireworks/models/qwen2p5-vl-32b-instruct",
        }
    },
    "novita": {
        "base_url": "https://api.novita.ai/v3/openai",
        "env_key": "NOVITA_API_KEY",
        "models": {
            "qwen2.5-vl-72b": "qwen/qwen-2.5-vl-72b-instruct",
            "qwen2.5-vl-7b": "qwen/qwen-2.5-vl-7b-instruct",
        }
    },
}

# Replicate models (different API pattern) - using explicit versions for reliability
REPLICATE_MODELS = {
    "deepseek-vl2": "deepseek-ai/deepseek-vl2:e5caf557dd9e5dcee46442e1315291ef1867f027991ede8ff95e304d4f734200",
    "llama-3.2-vision-90b": "lucataco/ollama-llama3.2-vision-90b:54202b223d5351c5afe5c0c9dba2b3042293b839d022e76f53d66ab30b9dc814",
    "llava-13b": "yorickvp/llava-13b:80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb",
}


def extract_deflection_points_replicate(image_path: Path, model: str) -> dict:
    """
    Send image to Replicate and extract deflection points.
    
    Args:
        image_path: Path to the chart image
        model: Model shortname (e.g., 'deepseek-vl2')
    
    Returns:
        Dict with extraction results
    """
    if replicate is None:
        raise ImportError("Replicate library not installed. Run: pip install replicate")
    
    # Get API key from environment (check both common names)
    api_key = os.getenv("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Set REPLICATE_API_TOKEN or REPLICATE_API_KEY in your .env file or environment.")
    
    # Set the API token
    os.environ["REPLICATE_API_TOKEN"] = api_key
    
    # Resolve model name
    if model in REPLICATE_MODELS:
        full_model_name = REPLICATE_MODELS[model]
    else:
        full_model_name = model
    
    print(f"\n[INFO] Sending image to {full_model_name.split(':')[0]} via Replicate...")
    print(f"[INFO] Image: {image_path.name}")
    
    # Replicate requires a URL or file handle, not data URI
    try:
        import time
        
        # Open file handle - Replicate will upload it
        image_file = open(image_path, "rb")
        
        # Different models have different parameter names
        if "ollama" in full_model_name or "llama" in full_model_name.lower():
            # Ollama-wrapped models use max_tokens
            input_params = {
                "image": image_file,
                "prompt": DEFLECTION_PROMPT,
                "max_tokens": 4096,
                "temperature": 0.1
            }
        else:
            # DeepSeek and others use max_length_tokens
            input_params = {
                "image": image_file,
                "prompt": DEFLECTION_PROMPT,
                "max_length_tokens": 4096,
                "temperature": 0.1
            }
        
        # Use predictions API with polling for cold start models
        print(f"[INFO] Creating prediction (may take 1-2 min for cold start)...")
        
        # Replicate requires either version OR model, not both
        if ':' in full_model_name:
            # Full version string provided
            prediction = replicate.predictions.create(
                version=full_model_name.split(':')[1],
                input=input_params
            )
        else:
            # Just model name - use latest version
            prediction = replicate.predictions.create(
                model=full_model_name,
                input=input_params
            )
        
        # Poll for completion with timeout
        max_wait = 180  # 3 minutes for cold starts
        poll_interval = 5
        elapsed = 0
        
        while prediction.status not in ["succeeded", "failed", "canceled"]:
            time.sleep(poll_interval)
            elapsed += poll_interval
            prediction.reload()
            print(f"[INFO] Status: {prediction.status} ({elapsed}s elapsed)")
            
            if elapsed >= max_wait:
                return {
                    "model": full_model_name.split(':')[0],
                    "provider": "replicate",
                    "timestamp": datetime.now().isoformat(),
                    "usage": {"total_tokens": 0},
                    "result": {"error": f"Timeout after {max_wait}s - model may need dedicated hardware"}
                }
        
        if prediction.status == "failed":
            return {
                "model": full_model_name.split(':')[0],
                "provider": "replicate",
                "timestamp": datetime.now().isoformat(),
                "usage": {"total_tokens": 0},
                "result": {"error": f"Prediction failed: {prediction.error}"}
            }
        
        output = prediction.output
        
        # Replicate returns a generator for some models, collect the output
        if hasattr(output, '__iter__') and not isinstance(output, (str, dict)):
            raw_output = "".join(str(item) for item in output)
        else:
            raw_output = str(output)
        
    except Exception as e:
        return {
            "model": full_model_name.split(':')[0],
            "provider": "replicate",
            "timestamp": datetime.now().isoformat(),
            "usage": {"total_tokens": 0},
            "result": {"error": str(e)}
        }
    
    print(f"[INFO] Response received")
    
    # Try to parse JSON
    result = None
    
    # Remove markdown code blocks if present
    if "```json" in raw_output:
        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_output:
        raw_output = raw_output.split("```")[1].split("```")[0].strip()
    
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        result = {"raw_output": raw_output, "parse_error": str(e)}
    
    return {
        "model": full_model_name.split(':')[0],
        "provider": "replicate",
        "timestamp": datetime.now().isoformat(),
        "usage": {"total_tokens": 0},  # Replicate doesn't report tokens
        "result": result
    }


def extract_deflection_points_cloud(image_path: Path, model: str, provider: str) -> dict:
    """
    Send image to a cloud API provider hosting open-source models.
    
    Args:
        image_path: Path to the chart image
        model: Model shortname (e.g., 'qwen2.5-vl-72b', 'llama-3.2-vision-11b')
        provider: Cloud provider name (together, hyperbolic, fireworks, novita)
    
    Returns:
        Dict with extraction results
    """
    if OpenAI is None:
        raise ImportError("OpenAI library not installed. Run: pip install openai")
    
    if provider not in CLOUD_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(CLOUD_PROVIDERS.keys())}")
    
    config = CLOUD_PROVIDERS[provider]
    
    # Get API key from environment
    api_key = os.getenv(config["env_key"])
    if not api_key:
        raise ValueError(f"API key not found. Set {config['env_key']} in your .env file or environment.")
    
    # Resolve model name
    if model in config["models"]:
        full_model_name = config["models"][model]
    else:
        full_model_name = model  # Use as-is if not in shortcuts
    
    # Create client
    client = OpenAI(
        base_url=config["base_url"],
        api_key=api_key
    )
    
    # Encode image
    base64_image = encode_image(image_path)
    
    print(f"\n[INFO] Sending image to {full_model_name} via {provider}...")
    print(f"[INFO] Image: {image_path.name}")
    
    # Build request
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": DEFLECTION_PROMPT
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    response = client.chat.completions.create(
        model=full_model_name,
        messages=messages,
        max_tokens=3000,
        temperature=0.1
    )
    
    # Get response
    raw_output = response.choices[0].message.content.strip()
    
    # Token usage
    usage = {
        "prompt_tokens": getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0,
        "completion_tokens": getattr(response.usage, 'completion_tokens', 0) if response.usage else 0,
        "total_tokens": getattr(response.usage, 'total_tokens', 0) if response.usage else 0
    }
    
    print(f"[INFO] Tokens used: {usage['total_tokens']:,}")
    
    # Try to parse JSON
    result = None
    
    # Remove markdown code blocks if present
    if "```json" in raw_output:
        raw_output = raw_output.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_output:
        raw_output = raw_output.split("```")[1].split("```")[0].strip()
    
    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"[WARNING] JSON parsing failed: {e}")
        result = {"raw_output": raw_output, "parse_error": str(e)}
    
    return {
        "model": full_model_name,
        "provider": provider,
        "timestamp": datetime.now().isoformat(),
        "usage": usage,
        "result": result
    }


def extract_deflection_points(image_path: Path, model: str = "gpt-4o-mini", base_url: str = None) -> dict:
    """
    Route to appropriate API based on model name.
    
    Args:
        image_path: Path to the chart image
        model: Model to use
        base_url: For local/cloud models:
                  - Local shortcuts: ollama, vllm, lmstudio
                  - Cloud providers: together, hyperbolic, fireworks, novita, replicate
                  - Custom URL: http://...
    
    Returns:
        Dict with extraction results
    """
    # Replicate (special case - different API)
    if base_url == "replicate":
        return extract_deflection_points_replicate(image_path, model)
    
    # Cloud providers (OpenAI-compatible)
    if base_url in CLOUD_PROVIDERS:
        return extract_deflection_points_cloud(image_path, model, base_url)
    
    # Local servers (shortcuts or custom URL)
    if base_url:
        if base_url in LOCAL_SERVERS:
            base_url = LOCAL_SERVERS[base_url]
        return extract_deflection_points_local(image_path, model, base_url)
    
    # Anthropic models
    if model.startswith("claude"):
        return extract_deflection_points_anthropic(image_path, model)
    
    # OpenAI models
    else:
        return extract_deflection_points_openai(image_path, model)


def print_results(data: dict):
    """Pretty print the extraction results."""
    result = data.get("result", {})
    
    if "parse_error" in result:
        print("\n[ERROR] Failed to parse JSON response:")
        print(result.get("raw_output", "No output"))
        return
    
    print("\n" + "=" * 80)
    print("DEFLECTION POINT EXTRACTION RESULTS")
    print("=" * 80)
    
    # Chart info
    chart_info = result.get("chart_info", {})
    print(f"\nChart: {chart_info.get('title', 'Unknown')}")
    x_axis = chart_info.get("x_axis", {})
    y_axis = chart_info.get("y_axis", {})
    print(f"X-axis: {x_axis.get('label', 'N/A')} - Range: {x_axis.get('range', 'N/A')}")
    print(f"Y-axis: {y_axis.get('label', 'N/A')} - Range: {y_axis.get('range', 'N/A')}")
    
    # Each series
    for series in result.get("series", []):
        print(f"\n{'-' * 60}")
        print(f"Series: {series.get('name', 'Unknown')} ({series.get('color', 'N/A')})")
        print(f"Total deflection points: {series.get('total_deflections', len(series.get('deflection_points', [])))}")
        print(f"{'-' * 60}")
        
        deflections = series.get("deflection_points", [])
        
        # Print in table format
        print(f"{'Year':>8} | {'Value':>8} | {'Type':<15}")
        print(f"{'-'*8}-+-{'-'*8}-+-{'-'*15}")
        
        for dp in deflections:
            year = dp.get("year", "?")
            value = dp.get("value", "?")
            dp_type = dp.get("type", "?")
            
            if isinstance(value, (int, float)):
                print(f"{year:>8} | {value:>8.3f} | {dp_type:<15}")
            else:
                print(f"{year:>8} | {str(value):>8} | {dp_type:<15}")
    
    # Notes
    notes = result.get("extraction_notes", "")
    if notes:
        print(f"\nNotes: {notes}")
    
    print("\n" + "=" * 80)


def main():
    # Default image path
    default_image = Path("Farm Financial Health/stage_1_crop/Images/page_8_image_0.png")
    
    # Allow command line override
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
    else:
        image_path = default_image
    
    # Check model argument
    model = "gpt-4o-mini"
    if len(sys.argv) > 2:
        model = sys.argv[2]
    
    # Check base_url argument (for local models)
    base_url = None
    if len(sys.argv) > 3:
        base_url = sys.argv[3]
    
    # Check if image exists
    if not image_path.exists():
        print(f"[ERROR] Image not found: {image_path}")
        print(f"[INFO] Current directory: {os.getcwd()}")
        sys.exit(1)
    
    print("=" * 80)
    print("DEFLECTION POINT EXTRACTION TEST")
    print("=" * 80)
    print(f"Image: {image_path}")
    print(f"Model: {model}")
    if base_url:
        print(f"Server: {base_url}")
    
    # Run extraction
    data = extract_deflection_points(image_path, model=model, base_url=base_url)
    
    # Print results
    print_results(data)
    
    # Save results to file
    model_safe = model.replace("-", "_").replace("/", "_").replace(":", "_")
    output_file = Path(f"test_deflection_results_{model_safe}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"\n[INFO] Results saved to: {output_file}")


if __name__ == "__main__":
    main()

