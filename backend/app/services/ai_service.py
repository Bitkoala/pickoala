
import random
import json
import logging
import asyncio
from typing import List, Optional, Dict, Any
import google.generativeai as genai
from app.config import get_settings

logger = logging.getLogger(__name__)

class KeyManager:
    """Manages rotation of multiple API keys."""
    def __init__(self, keys_str: Optional[str]):
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()] if keys_str else []
        self._current_index = 0

    def get_key(self) -> Optional[str]:
        if not self.keys:
            return None
        # Simple round-robin
        key = self.keys[self._current_index]
        self._current_index = (self._current_index + 1) % len(self.keys)
        return key
    
    def get_random_key(self) -> Optional[str]:
         if not self.keys:
            return None
         return random.choice(self.keys)

from app.services import settings as settings_service

class GeminiService:
    def __init__(self):
        # We don't load keys in init anymore to allow dynamic updates
        # Keys will be fetched per request or cached with short TTL
        self.model_name = "gemini-1.5-flash"
        
    async def _configure_genai(self) -> bool:
        keys_str = await settings_service.get_gemini_api_keys()
        if not keys_str:
            # Fallback to config if needed (env vars)
            settings = get_settings()
            keys_str = settings.gemini_api_keys
            
        key_manager = KeyManager(keys_str)
        api_key = key_manager.get_key()
        
        if not api_key:
            logger.warning("No Gemini API keys configured.")
            return False
            
        genai.configure(api_key=api_key)
        return True

    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyzes an image using Gemini Vision to generate tags and a description.
        Returns a dict with 'tags' (list) and 'description' (str).
        """
        if not await self._configure_genai():
             return {"error": "AI not configured"}

        try:
             # Load image data
             # Check if it's a local path or needs downloading
             # For now assume local file path from upload
             if not image_path:
                 return {"error": "Invalid image path"}
             
             # Upload file to Gemini (File API) or use inline data if small enough
             # For simplicity and speed with flash model, we'll use inline data for now if supported by SDK,
             # else we use the File API. 
             # Ref: https://ai.google.dev/gemini-api/docs/vision
             
             # Note: Python SDK often supports passing PIL Image or path directly to generate_content
             
             model = genai.GenerativeModel(self.model_name)
             
             # Uploading the file is safer for larger images
             uploaded_file = genai.upload_file(image_path)
             
             prompt = """
             Analyze this image. 
             1. detailed_description: A 2-sentence detailed description of the image content for search indexing.
             2. tags: A list of 5-10 relevant keywords/tags (e.g., 'landscape', 'cat', 'cyberpunk').
             
             Return the result as a valid JSON object with keys 'description' and 'tags'.
             """
             
             # Retry logic could be added here for 429 errors
             response = await model.generate_content_async([prompt, uploaded_file], generation_config={"response_mime_type": "application/json"})
             
             # Clean up
             # try:
             #    uploaded_file.delete()
             # except:
             #    pass
             
             if response.text:
                 try:
                     result = json.loads(response.text)
                     return {
                         "tags": result.get("tags", []),
                         "description": result.get("description", "")
                     }
                 except json.JSONDecodeError:
                     logger.error(f"Failed to parse Gemini response: {response.text}")
                     return {"error": "Invalid JSON response from AI"}
             
             return {"error": "Empty response from AI"}

        except Exception as e:
            logger.error(f"Gemini analysis failed: {str(e)}")
            # If 429, ideally we should retry with another key.
            # Simplified for now.
            return {"error": str(e)}

gemini_service = GeminiService()
