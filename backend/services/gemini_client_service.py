import os
import time
import asyncio
import re
from pathlib import Path

class GeminiKeyPoolManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiKeyPoolManager, cls).__new__(cls)
            cls._instance.keys = cls._instance._load_keys()
            cls._instance.current_index = 0
            cls._instance.cooldown_until = 0.0
            if cls._instance.keys:
                os.environ["GEMINI_API_KEY"] = cls._instance.keys[0]
                print(f"[KeyPool] Loaded {len(cls._instance.keys)} API keys from .env. Active key index: 0.")
            else:
                print("[KeyPool] No API keys found in pool. Using environment default.")
        return cls._instance

    def set_cooldown(self, duration_seconds):
        self.cooldown_until = time.time() + duration_seconds
        
    def get_remaining_cooldown(self):
        rem = self.cooldown_until - time.time()
        return max(0.0, rem)
        
    def _load_keys(self):
        pool_str = os.environ.get("GEMINI_API_KEY_POOL", "")
        if pool_str:
            return [k.strip() for k in pool_str.split(",") if k.strip()]
            
        keys = []
        # Find .env file up the directory chain
        current_dir = Path(__file__).resolve().parent
        env_path = None
        for parent in [current_dir, current_dir.parent, current_dir.parent.parent]:
            candidate = parent / ".env"
            if candidate.exists():
                env_path = candidate
                break
                
        if env_path:
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        match = re.search(r"(?:#\s*#?\s*)?GEMINI_API_KEY\s*=\s*(AQ\.[a-zA-Z0-9_-]+|AIzaSy[a-zA-Z0-9_-]+)", line)
                        if match:
                            key = match.group(1).strip()
                            # Skip standard placeholders
                            if len(key) > 25 and "aizasyabqgnntorbqlifphaojkygp" not in key.lower() and key not in keys:
                                keys.append(key)
            except Exception as e:
                print(f"[KeyPool] Failed to parse .env file: {e}")
        return keys
        
    def get_active_key(self):
        if not self.keys:
            return os.environ.get("GEMINI_API_KEY")
        return self.keys[self.current_index]
        
    def rotate_key(self):
        if not self.keys or len(self.keys) <= 1:
            return self.get_active_key()
            
        self.current_index = (self.current_index + 1) % len(self.keys)
        new_key = self.keys[self.current_index]
        os.environ["GEMINI_API_KEY"] = new_key
        print(f"[KeyPool] 🔄 Rotated API key to index {self.current_index}: ...{new_key[-8:]}")
        
        # Clear ADK agent client caches to force re-initialization with new key
        try:
            from backend.agents.security.security_agent import security_agent
            from backend.agents.evaluation.evaluation_agent import evaluation_agent
            from backend.agents.revenue.revenue_agent import revenue_agent
            from backend.agents.customer.customer_agent import customer_agent
            from backend.agents.risk.risk_agent import risk_agent
            from backend.agents.report.report_agent import report_agent
            from backend.agents.forecast.forecast_agent import forecast_agent
            from backend.agents.orchestrator.executive_orchestrator import executive_orchestrator, executive_orchestrator_fallback
            
            agents = [
                security_agent, evaluation_agent, revenue_agent, customer_agent,
                risk_agent, report_agent, forecast_agent, executive_orchestrator,
                executive_orchestrator_fallback
            ]
            for agent in agents:
                if hasattr(agent, 'canonical_model') and agent.canonical_model:
                    for attr in ['api_client', '_live_api_client', '_api_backend']:
                        if attr in agent.canonical_model.__dict__:
                            del agent.canonical_model.__dict__[attr]
        except Exception as cache_err:
            print(f"[KeyPool] Failed to clear agent client caches: {cache_err}")
            
        return new_key

key_pool = GeminiKeyPoolManager()

def update_client_api_key(client, api_key):
    """
    Updates the API key headers in google.genai Client, APIClient, and AsyncClient.
    """
    if not client:
        return
    if hasattr(client, 'api_key'):
        client.api_key = api_key
    # Update Client._api_client
    if hasattr(client, '_api_client') and client._api_client:
        client._api_client.api_key = api_key
        api_client = client._api_client
        if hasattr(api_client, '_http_options') and api_client._http_options:
            if hasattr(api_client._http_options, 'headers') and api_client._http_options.headers:
                api_client._http_options.headers['x-goog-api-key'] = api_key
    # Update Client.aio._api_client
    if hasattr(client, 'aio') and client.aio:
        if hasattr(client.aio, '_api_client') and client.aio._api_client:
            client.aio._api_client.api_key = api_key
            aio_api_client = client.aio._api_client
            if hasattr(aio_api_client, '_http_options') and aio_api_client._http_options:
                if hasattr(aio_api_client._http_options, 'headers') and aio_api_client._http_options.headers:
                    aio_api_client._http_options.headers['x-goog-api-key'] = api_key

async def execute_with_retry(func, *args, **kwargs):
    """
    Executes an async Gemini API function with automatic API key rotation and exponential backoff.
    """
    import re
    max_attempts = len(key_pool.keys) * 2 if key_pool.keys else 3
    delay = 2.0
    
    for attempt in range(max_attempts):
        # Wait for global cooldown if any
        cooldown = key_pool.get_remaining_cooldown()
        if cooldown > 0:
            print(f"[KeyPool] Waiting for global cooldown of {cooldown:.1f}s before request...")
            await asyncio.sleep(cooldown)

        try:
            if 'client' in kwargs:
                client = kwargs['client']
                active_key = key_pool.get_active_key()
                update_client_api_key(client, active_key)
            call_kwargs = {k: v for k, v in kwargs.items() if k != 'client'}
            return await func(*args, **call_kwargs)
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg
            is_daily_exhausted = "limit: 0" in err_msg or '"limit": 0' in err_msg or '"quotaValue": "0"' in err_msg or '"quotaValue": 0' in err_msg
            
            if is_daily_exhausted:
                print(f"[KeyPool] Daily quota exhausted for this model/key (limit: 0). Failing immediately to trigger fallback...")
                raise e

            if is_rate_limit and attempt < max_attempts - 1:
                # Parse retry delay
                sleep_seconds = delay
                match = re.search(r"Please retry in ([0-9.]+)\s*s", err_msg)
                if match:
                    sleep_seconds = float(match.group(1)) + 1.0
                else:
                    match_sec = re.search(r"'retryDelay':\s*'(\d+)\s*s'", err_msg)
                    if match_sec:
                        sleep_seconds = float(match_sec.group(1)) + 1.0

                print(f"[KeyPool] Rate limit hit: {err_msg}. Rotating key and retrying (attempt {attempt + 1}/{max_attempts})...")
                key_pool.rotate_key()
                if key_pool.keys and (attempt + 1) % len(key_pool.keys) == 0:
                    print(f"[KeyPool] All keys rate-limited. Setting global cooldown and sleeping for {sleep_seconds:.1f}s...")
                    key_pool.set_cooldown(sleep_seconds)
                    await asyncio.sleep(sleep_seconds)
                    delay *= 2
            else:
                raise e

def execute_with_retry_sync(func, *args, **kwargs):
    """
    Executes a synchronous Gemini API function with automatic API key rotation and exponential backoff.
    """
    import re
    max_attempts = len(key_pool.keys) * 2 if key_pool.keys else 3
    delay = 2.0
    
    for attempt in range(max_attempts):
        # Wait for global cooldown if any
        cooldown = key_pool.get_remaining_cooldown()
        if cooldown > 0:
            print(f"[KeyPool] Waiting for global cooldown of {cooldown:.1f}s before sync request...")
            time.sleep(cooldown)

        try:
            if 'client' in kwargs:
                client = kwargs['client']
                active_key = key_pool.get_active_key()
                update_client_api_key(client, active_key)
            call_kwargs = {k: v for k, v in kwargs.items() if k != 'client'}
            return func(*args, **call_kwargs)
        except Exception as e:
            err_msg = str(e)
            is_rate_limit = "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "503" in err_msg or "UNAVAILABLE" in err_msg
            is_daily_exhausted = "limit: 0" in err_msg or '"limit": 0' in err_msg or '"quotaValue": "0"' in err_msg or '"quotaValue": 0' in err_msg
            
            if is_daily_exhausted:
                print(f"[KeyPool] Daily quota exhausted for this model/key (limit: 0) (sync). Failing immediately to trigger fallback...")
                raise e

            if is_rate_limit and attempt < max_attempts - 1:
                # Parse retry delay
                sleep_seconds = delay
                match = re.search(r"Please retry in ([0-9.]+)\s*s", err_msg)
                if match:
                    sleep_seconds = float(match.group(1)) + 1.0
                else:
                    match_sec = re.search(r"'retryDelay':\s*'(\d+)\s*s'", err_msg)
                    if match_sec:
                        sleep_seconds = float(match_sec.group(1)) + 1.0

                print(f"[KeyPool] Rate limit hit (sync): {err_msg}. Rotating key and retrying (attempt {attempt + 1}/{max_attempts})...")
                key_pool.rotate_key()
                if key_pool.keys and (attempt + 1) % len(key_pool.keys) == 0:
                    print(f"[KeyPool] All keys rate-limited (sync). Setting global cooldown and sleeping for {sleep_seconds:.1f}s...")
                    key_pool.set_cooldown(sleep_seconds)
                    time.sleep(sleep_seconds)
                    delay *= 2
            else:
                raise e

# Monkeypatch google.adk's Gemini model async generation to perform on-the-fly key rotation
try:
    from google.adk.models.google_llm import Gemini, _ResourceExhaustedError
    from google.genai.errors import ClientError
    import re

    original_generate_content_async = Gemini.generate_content_async

    async def patched_generate_content_async(self, llm_request, stream=False):
        max_attempts = len(key_pool.keys) * 2 if key_pool.keys else 3
        delay = 2.0
        
        for attempt in range(max_attempts):
            # Wait for global cooldown if any
            cooldown = key_pool.get_remaining_cooldown()
            if cooldown > 0:
                print(f"[KeyPoolPatch] Waiting for global cooldown of {cooldown:.1f}s before agent request...")
                await asyncio.sleep(cooldown)

            try:
                active_key = key_pool.get_active_key()
                update_client_api_key(self.api_client, active_key)
                
                yielded_any = False
                async for res in original_generate_content_async(self, llm_request, stream):
                    yielded_any = True
                    yield res
                return
            except Exception as e:
                err_msg = str(e)
                is_rate_limit = (
                    "429" in err_msg or 
                    "RESOURCE_EXHAUSTED" in err_msg or 
                    "503" in err_msg or 
                    "UNAVAILABLE" in err_msg or
                    isinstance(e, _ResourceExhaustedError) or
                    (isinstance(e, ClientError) and e.code in (429, 503))
                )
                is_daily_exhausted = "limit: 0" in err_msg or '"limit": 0' in err_msg or '"quotaValue": "0"' in err_msg or '"quotaValue": 0' in err_msg
                
                if is_daily_exhausted:
                    print(f"[KeyPoolPatch] Daily quota exhausted for this model/key (limit: 0). Failing step immediately to trigger fallback...")
                    raise e

                if is_rate_limit and not yielded_any and attempt < max_attempts - 1:
                    # Parse retry delay
                    sleep_seconds = delay
                    match = re.search(r"Please retry in ([0-9.]+)\s*s", err_msg)
                    if match:
                        sleep_seconds = float(match.group(1)) + 1.0
                    else:
                        match_sec = re.search(r"'retryDelay':\s*'(\d+)\s*s'", err_msg)
                        if match_sec:
                            sleep_seconds = float(match_sec.group(1)) + 1.0

                    print(f"[KeyPoolPatch] Rate limit hit during Agent LLM call: {err_msg}. Rotating key and retrying step (attempt {attempt + 1}/{max_attempts})...")
                    key_pool.rotate_key()
                    if key_pool.keys and (attempt + 1) % len(key_pool.keys) == 0:
                        print(f"[KeyPoolPatch] All keys rate-limited. Setting global cooldown and sleeping for {sleep_seconds:.1f}s...")
                        key_pool.set_cooldown(sleep_seconds)
                        await asyncio.sleep(sleep_seconds)
                        delay *= 2
                else:
                    raise e

    Gemini.generate_content_async = patched_generate_content_async
    print("[KeyPoolPatch] Successfully monkeypatched Gemini.generate_content_async for on-the-fly ADK key rotation.")
except Exception as patch_err:
    print(f"[KeyPoolPatch] Failed to patch Gemini.generate_content_async: {patch_err}")

