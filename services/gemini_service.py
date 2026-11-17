import os
import time
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

load_dotenv()


class GeminiService:
    """
    Centralized service for interacting with the Google Gen AI Python SDK (`google-genai`).
    Supports standard text generation, structured JSON generation, and function calling.
    Configured for Gemini 3.8 Flash by default with automatic retry and rate-limit handling.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        
        self.client = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            self.client = None
            raise RuntimeError(f"Failed to initialize Gemini Client: {str(e)}") from e

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()
        if self.api_key:
            self._init_client()

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        tools: Optional[list] = None,
        temperature: float = 0.2,
        response_schema=None,
        response_mime_type: Optional[str] = None,
        max_retries: int = 3,
    ):
        """
        Calls Gemini API using the official google-genai SDK.
        Audited for Gemini 3 compatibility:
        - Uses supported thinking_config (thinking_level='LOW' for flash models)
        - Removes legacy deprecated parameters (candidate_count, thinking_budget)
        - Handles temporary 503 high-demand spikes and 429 rate limits gracefully with retries.
        """
        if not self.is_configured():
            raise ValueError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file or UI."
            )

        config_args = {
            "temperature": temperature,
        }
        if system_instruction:
            config_args["system_instruction"] = system_instruction
        if tools:
            config_args["tools"] = tools
        if response_schema:
            config_args["response_schema"] = response_schema
            config_args["response_mime_type"] = "application/json"
        elif response_mime_type:
            config_args["response_mime_type"] = response_mime_type

        # Configure thinking_level for Gemini 3 models
        if "3." in self.model_name or "gemini-3" in self.model_name:
            config_args["thinking_config"] = types.ThinkingConfig(thinking_level="LOW")

        config = types.GenerateContentConfig(**config_args)
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                return response
            except (ServerError, ClientError) as e:
                last_error = e
                err_str = str(e)
                # If rate limited or 503 high demand, back off briefly if retries remain
                if ("503" in err_str or "429" in err_str) and attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise RuntimeError(f"Gemini API Error: {err_str}") from e
            except Exception as e:
                raise RuntimeError(f"Gemini API Error: {str(e)}") from e

        raise RuntimeError(f"Gemini API Error after {max_retries} attempts: {last_error}")
