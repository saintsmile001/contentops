import asyncio
import ast
import json
import logging
from typing import Any

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def _make_strict_schema(schema: Any) -> Any:
    """Recursively enforce OpenAI strict schema requirements:
    - additionalProperties must be False on every object schema
    - required must list all property keys on every object schema
    """
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            schema["additionalProperties"] = False
            if "properties" in schema and isinstance(schema["properties"], dict):
                schema["required"] = list(schema["properties"].keys())
        for key, value in schema.items():
            schema[key] = _make_strict_schema(value)
    elif isinstance(schema, list):
        return [_make_strict_schema(item) for item in schema]
    return schema


def _extract_output_text(data: dict[str, Any]) -> str | None:
    """Extract structured output text from OpenAI Responses API or Chat Completions API response."""
    # Direct top-level output_text
    if data.get("output_text"):
        return str(data["output_text"])

    # Responses API: output[].content[].text
    for item in data.get("output", []):
        if isinstance(item, dict) and item.get("type") == "message":
            for content in item.get("content", []):
                if isinstance(content, dict) and content.get("type") == "output_text" and "text" in content:
                    return str(content["text"])

    # Chat Completions API fallback: choices[0].message.content
    choices = data.get("choices")
    if choices and isinstance(choices, list) and len(choices) > 0:
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            return first_choice.get("message", {}).get("content")

    return None


class AIClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_structured(self, instructions: str, source: str, response_model: type[BaseModel]) -> BaseModel:
        if self.settings.ai_mock_mode:
            return self._mock_dna(source, response_model)
        if not self.settings.openai_api_key:
            raise AppError("AI_NOT_CONFIGURED", "AI analysis is not configured on this server.", 503)

        api_key = self.settings.openai_api_key.strip()
        strict_schema = _make_strict_schema(response_model.model_json_schema())

        payload = {
            "model": self.settings.openai_model,
            "instructions": instructions,
            "input": source,
            "store": False,
            "temperature": 0.3,
            "max_output_tokens": 4096,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": strict_schema,
                }
            },
        }

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/responses",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )

                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < 2:
                        await asyncio.sleep(attempt + 1)
                        continue
                    raise AppError("AI_UNAVAILABLE", "AI analysis is temporarily unavailable. Please try again.", 503)

                if response.status_code >= 400:
                    err_msg = "We couldn't analyze this content right now."
                    try:
                        err_json = response.json()
                        detail = err_json.get("error", {}).get("message")
                        if detail:
                            logger.error("OpenAI error (HTTP %s): %s", response.status_code, detail)
                            err_msg = f"{err_msg} ({detail})"
                    except Exception:
                        logger.error("OpenAI raw error (HTTP %s): %s", response.status_code, response.text)
                    raise AppError("AI_ERROR", err_msg, 502)

                data = response.json()
                if data.get("status") == "incomplete":
                    reason = data.get("incomplete_details", {}).get("reason", "unknown")
                    raise AppError("AI_INCOMPLETE", f"AI response was incomplete ({reason}). Try shorter source text.", 422)

                text = _extract_output_text(data)
                if not text:
                    logger.error("Could not extract output text from OpenAI response: %s", data)
                    raise AppError("AI_EMPTY_RESPONSE", "AI returned an empty response. Please try again.", 502)

                return response_model.model_validate_json(text)

            except AppError:
                raise
            except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValueError) as exc:
                logger.warning("AI structured generation attempt %s failed: %s", attempt + 1, exc)
                if attempt == 2:
                    raise AppError("AI_INVALID_RESPONSE", f"We couldn't analyze this content right now. ({exc})", 502) from exc
                await asyncio.sleep(attempt + 1)

        raise AssertionError("unreachable")

    @staticmethod
    def _mock_dna(source: str, response_model: type[BaseModel]) -> BaseModel:
        if response_model.__name__ == "CampaignStrategy":
            try:
                selected = ast.literal_eval(source).get("platforms", [])
            except (SyntaxError, ValueError, AttributeError):
                selected = []
            selected = [platform for platform in selected if platform in {"linkedin", "x", "instagram", "threads"}] or ["linkedin", "x", "instagram"]
            platforms = [selected[index % len(selected)] for index in range(7)]
            type_by_platform = {"linkedin": "educational_post", "x": "thread", "instagram": "caption", "threads": "post"}
            types = [type_by_platform[platform] for platform in platforms]
            days = [
                {
                    "day": day,
                    "platform": platform,
                    "content_type": types[day - 1],
                    "angle": f"Source-grounded angle {day}",
                    "hook": f"A source-grounded insight for day {day}",
                    "objective": "engagement" if day % 2 == 0 else "awareness",
                }
                for day, platform in enumerate(platforms, 1)
            ]
            return response_model.model_validate({"duration": 7, "days": days})

        if response_model.__name__ == "SocialAsset":
            platform = next((item for item in ("linkedin", "instagram", "x", "threads") if f"'platform': '{item}'" in source), "linkedin")
            return response_model.model_validate({
                "platform": platform,
                "content_type": "educational_post",
                "title": "Source-grounded insight",
                "hook": "Start with the source.",
                "content": "This draft is generated from the approved Content DNA and should be reviewed before publishing.",
                "cta": "Review the source.",
                "hashtags": ["#ContentOps"],
            })

        if response_model.__name__ == "SEOAsset":
            return response_model.model_validate({
                "seo_title": "Source-grounded content workflow",
                "meta_description": "A source-grounded approach to content operations.",
                "primary_keyword": "content operations",
                "secondary_keywords": ["content workflow"],
                "search_intent": "informational",
                "content_angle": "source-grounded repurposing",
                "url_slug": "source-grounded-content-workflow",
            })

        if response_model.__name__ == "QAReport":
            return response_model.model_validate({
                "faithfulness_score": 90,
                "source_coverage_score": 82,
                "brand_alignment_score": 90,
                "unsupported_claims": [],
                "supported_claims": [],
                "issues": [],
                "recommendations": ["Review before publishing."],
                "status": "PASS",
            })

        sentences = [item.strip() for item in source.replace("\n", " ").split(".") if item.strip()]
        first = sentences[0] if sentences else source[:160]
        payload = {
            "title": first[:120],
            "main_thesis": first,
            "target_audience": "The audience described in the source",
            "content_pillars": [first],
            "key_points": sentences[:3] or [first],
            "stories": [],
            "claims": [],
            "statistics": [],
            "keywords": [],
            "entities": [],
            "tone": "Informative",
            "cta": "Review the original source",
            "summary": " ".join(sentences[:2]) or first,
        }
        return response_model.model_validate(payload)
