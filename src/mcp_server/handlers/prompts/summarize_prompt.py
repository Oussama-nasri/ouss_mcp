"""
Prompt handlers expose reusable prompt templates to the LLM host.
They are not tools — they return a list of messages that the client
can inject into the conversation as context or instructions.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import (
    GetPromptResult,
    PromptMessage,
    TextContent,
)
import structlog

log = structlog.get_logger(__name__)


def register(mcp: FastMCP) -> None:

    @mcp.prompt(description="Generate a structured summarization prompt for any text or document.")
    async def summarize(
        text: str,
        style: str = "bullet",
        language: str = "english",
        max_words: int = 200,
    ) -> GetPromptResult:
        """
        Args:
            text:      The content to summarize (required)
            style:     Output style — 'bullet' | 'paragraph' | 'tldr' (default: bullet)
            language:  Language for the summary (default: english)
            max_words: Approximate word limit for the summary (default: 200)
        """
        valid_styles = {"bullet", "paragraph", "tldr"}
        if style not in valid_styles:
            style = "bullet"

        log.info("prompt.summarize.called", style=style, language=language, max_words=max_words)

        style_instructions = {
            "bullet": (
                f"Write a bulleted list of the {max_words} most important points. "
                "Use clear, concise language. Each bullet should be one sentence."
            ),
            "paragraph": (
                f"Write a coherent {max_words}-word summary in prose form. "
                "Include the main idea, key supporting points, and conclusion."
            ),
            "tldr": (
                "Write a single TL;DR sentence (max 30 words) capturing the core message."
            ),
        }[style]

        system_prompt = (
            f"You are an expert summarizer. Always respond in {language}. "
            "Be accurate, neutral, and concise. Do not include information not present in the source."
        )

        user_prompt = (
            f"Summarize the following content.\n\n"
            f"Style: {style}\n"
            f"Instructions: {style_instructions}\n\n"
            f"--- BEGIN CONTENT ---\n{text}\n--- END CONTENT ---"
        )

        return GetPromptResult(
            description=f"Summarize content in {style} style ({language}, ~{max_words} words)",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=system_prompt),
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=user_prompt),
                ),
            ],
        )

    @mcp.prompt(description="Generate a code review prompt for a given code snippet.")
    async def code_review(
        code: str,
        language: str = "python",
        focus: str = "all",
    ) -> GetPromptResult:
        """
        Args:
            code:     The code snippet to review (required)
            language: Programming language (default: python)
            focus:    Review focus — 'security' | 'performance' | 'style' | 'all' (default: all)
        """
        valid_focus = {"security", "performance", "style", "all"}
        if focus not in valid_focus:
            focus = "all"

        focus_instructions = {
            "security": "Focus specifically on security vulnerabilities, injection risks, and unsafe patterns.",
            "performance": "Focus on algorithmic complexity, memory usage, and performance bottlenecks.",
            "style": "Focus on readability, naming conventions, and adherence to language idioms.",
            "all": "Cover security, performance, readability, error handling, and overall design.",
        }[focus]

        user_prompt = (
            f"Review the following {language} code.\n\n"
            f"Focus: {focus_instructions}\n\n"
            "Provide:\n"
            "1. A brief overall assessment\n"
            "2. Specific issues found (with line references if possible)\n"
            "3. Concrete suggestions for improvement\n"
            "4. A revised snippet if changes are significant\n\n"
            f"```{language}\n{code}\n```"
        )

        log.info("prompt.code_review.called", language=language, focus=focus)

        return GetPromptResult(
            description=f"Code review for {language} — focus: {focus}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=user_prompt),
                )
            ],
        )