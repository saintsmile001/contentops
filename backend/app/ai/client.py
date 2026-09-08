import asyncio
import ast
import json

import httpx
from pydantic import BaseModel

from app.core.config import Settings
from app.core.exceptions import AppError


class AIClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_structured(self, instructions: str, source: str, response_model: type[BaseModel]) -> BaseModel:
        if self.settings.ai_mock_mode:
            return self._mock_dna(source, response_model)
        if not self.settings.openai_api_key:
            raise AppError("AI_NOT_CONFIGURED", "AI analysis is not configured on this server.", 503)
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
                    "schema": response_model.model_json_schema(),
                }
            },
        }
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/responses",
                        headers={
                            "Authorization": f"Bearer {self.settings.openai_api_key}",
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
                    raise AppError("AI_ERROR", "We couldn't analyze this content right now. Please try again.", 502)
                data = response.json()
                # Check for refusal — the model may refuse if content violates policies
                if data.get("status") == "incomplete" or data.get("output_text") is None:
                    raise AppError("AI_REFUSED", "The content could not be processed. Please review your source material.", 422)
                return response_model.model_validate_json(data["output_text"])
            except (httpx.HTTPError, KeyError, json.JSONDecodeError, ValueError) as exc:
                if attempt == 2:
                    raise AppError("AI_INVALID_RESPONSE", "We couldn't analyze this content right now. Please try again.", 502) from exc
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
            days = [{"day": day, "platform": platform, "content_type": types[day - 1], "angle": f"Source-grounded angle {day}", "hook": f"A source-grounded insight for day {day}", "objective": "engagement" if day % 2 == 0 else "awareness"} for day, platform in enumerate(platforms, 1)]
            return response_model.model_validate({"duration": 7, "days": days})
        if response_model.__name__ == "SocialAsset":
            platform = next((item for item in ("linkedin", "instagram", "x", "threads") if f"'platform': '{item}'" in source), "linkedin")
            return response_model.model_validate({"platform":platform,"content_type":"educational_post","title":"Source-grounded insight","hook":"Start with the source.","content":"This draft is generated from the approved Content DNA and should be reviewed before publishing.","cta":"Review the source.","hashtags":["#ContentOps"]})
        if response_model.__name__ == "SEOAsset":
            return response_model.model_validate({"seo_title":"Source-grounded content workflow","meta_description":"A source-grounded approach to content operations.","primary_keyword":"content operations","secondary_keywords":["content workflow"],"search_intent":"informational","content_angle":"source-grounded repurposing","url_slug":"source-grounded-content-workflow"})
        if response_model.__name__ == "QAReport":
            return response_model.model_validate({"faithfulness_score":90,"source_coverage_score":82,"brand_alignment_score":90,"unsupported_claims":[],"supported_claims":[],"issues":[],"recommendations":["Review before publishing."],"status":"PASS"})
        sentences = [item.strip() for item in source.replace("\n", " ").split(".") if item.strip()]
        first = sentences[0] if sentences else source[:160]
        payload = {"title": first[:120], "main_thesis": first, "target_audience": "The audience described in the source", "content_pillars": [first], "key_points": sentences[:3] or [first], "stories": [], "claims": [], "statistics": [], "keywords": [], "entities": [], "tone": "Informative", "cta": "Review the original source", "summary": " ".join(sentences[:2]) or first}
        return response_model.model_validate(payload)
