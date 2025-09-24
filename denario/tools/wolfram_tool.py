"""Wolfram Alpha tool for LangGraph/LangChain integration.

This module provides a tool wrapper that can be used by Denario agents
to perform mathematical computations, unit conversions, and symbolic reasoning.
"""
from typing import Dict, Any, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from ..utils import WolframAlphaClient


class WolframAlphaInput(BaseModel):
    """Input schema for Wolfram Alpha tool."""
    query: str = Field(
        description="Mathematical query, equation, or computation to perform")
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached results")
    require_hitl: bool = Field(
        default=False,
        description="Whether to require human review for ambiguous results")


class WolframAlphaTool(BaseTool):
    """LangChain tool wrapper for Wolfram Alpha computations."""

    name: str = "wolfram_compute"
    description: str = (
        "Perform mathematical computations, symbolic reasoning, unit conversions, "
        "and equation solving using Wolfram Alpha. Use for: integrals, derivatives, "
        "algebraic manipulation, unit conversions, physical constants, and exact solutions.")
    args_schema: type[BaseModel] = WolframAlphaInput

    def __init__(
            self,
            app_id: Optional[str] = None,
            enable_hitl: bool = False,
            **kwargs):
        super().__init__(**kwargs)
        self._client = WolframAlphaClient(
            app_id=app_id, enable_hitl=enable_hitl)

    def _run(
            self,
            query: str,
            use_cache: bool = True,
            require_hitl: bool = False) -> str:
        """Execute Wolfram Alpha query and return formatted result."""
        try:
            # Perform query
            result = self._client.query(query, use_cache=use_cache)

            # Check if query was successful
            if not result.get("queryresult", {}).get("success"):
                error_msg = result.get(
                    "queryresult", {}).get(
                    "error", "Unknown error")
                return f"Wolfram Alpha query failed: {error_msg}"

            # Check if HITL review is needed
            if (require_hitl or self._client.enable_hitl) and self._client.needs_hitl_review(
                    result):
                hitl_prompt = self._client.get_hitl_prompt(query, result)
                return f"HITL_REVIEW_NEEDED: {hitl_prompt}"

            # Extract structured results
            structured = WolframAlphaClient.extract_structured_results(result)
            primary_text = WolframAlphaClient.extract_primary_text(result)

            # Format response
            response_parts = []

            if primary_text:
                response_parts.append(f"Result: {primary_text}")

            if structured["latex"]:
                response_parts.append(f"LaTeX: {structured['latex'][0]}")

            if structured["assumptions"]:
                response_parts.append(
                    f"Assumptions: {', '.join(structured['assumptions'][:2])}")

            if structured["sources"]:
                response_parts.append(
                    f"Sources: {', '.join(structured['sources'][:2])}")

            return "\n".join(
                response_parts) if response_parts else "No results found"

        except Exception as e:
            return f"Wolfram Alpha tool error: {str(e)}"

    async def _arun(
            self,
            query: str,
            use_cache: bool = True,
            require_hitl: bool = False) -> str:
        """Async version of _run."""
        return self._run(query, use_cache, require_hitl)


def create_wolfram_tool(
        app_id: Optional[str] = None,
        enable_hitl: bool = False) -> WolframAlphaTool:
    """Factory function to create a Wolfram Alpha tool instance."""
    return WolframAlphaTool(app_id=app_id, enable_hitl=enable_hitl)


def get_wolfram_tools() -> list[WolframAlphaTool]:
    """Get list of Wolfram Alpha tools for agent integration."""
    return [
        create_wolfram_tool(enable_hitl=False),  # Standard tool
        create_wolfram_tool(enable_hitl=True),   # HITL-enabled tool
    ]
