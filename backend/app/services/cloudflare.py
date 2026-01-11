import httpx
import logging
from typing import List
from app.services.settings import get_setting, get_setting_bool

logger = logging.getLogger(__name__)

async def purge_cf_cache(urls: List[str]) -> bool:
    """
    Purge given URLs from Cloudflare cache.
    """
    if not urls:
        return True

    enabled = await get_setting_bool("cf_purge_enabled", False)
    if not enabled:
        return False
        
    token = await get_setting("cf_api_token")
    zone_id = await get_setting("cf_zone_id")
    
    if not token or not zone_id:
        logger.warning("Cloudflare purge enabled but token or zone_id missing.")
        return False
        
    endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {"files": urls}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                logger.info(f"Successfully purged {len(urls)} URLs from Cloudflare.")
                return True
            else:
                logger.error(f"Cloudflare purge failed: {result.get('errors')}")
                return False
    except Exception as e:
        logger.error(f"Error calling Cloudflare API: {e}")
        return False
