# models/schemas.py
# Pydantic schemas for all AI tab outputs.
# Every AI response MUST be validated against the appropriate schema before saving to Supabase.

from pydantic import BaseModel, Field
from typing import Optional


class SummaryOutput(BaseModel):
    title: str = Field(description="A short title for the content")
    bullets: list[str] = Field(min_length=3, max_length=7, description="Key points, each one sentence")
    key_terms: list[str] = Field(min_length=3, max_length=8, description="Important vocabulary words")


class ReadEasyOutput(BaseModel):
    intro: str = Field(description="One sentence plain-English introduction")
    paragraphs: list[str] = Field(min_length=2, max_length=6, description="Short simplified paragraphs, max 3 sentences each")
    summary_line: str = Field(description="One final sentence wrapping up the topic")


class FocusModeSection(BaseModel):
    title: str = Field(description="Short label for this section")
    content: str = Field(description="Section content, max 80 words")
    recap: str = Field(description="One-line recap of this section")


class FocusModeOutput(BaseModel):
    sections: list[FocusModeSection] = Field(min_length=3, max_length=6)


class StepItem(BaseModel):
    number: int
    title: str = Field(description="Short step label")
    explanation: str = Field(description="Clear explanation of this step, max 60 words")


class StepByStepOutput(BaseModel):
    steps: list[StepItem] = Field(min_length=3, max_length=10)
    closing: str = Field(description="One sentence summarising what was achieved")


class MindMapOutput(BaseModel):
    mermaid: str = Field(
        description="Valid Mermaid.js mindmap syntax only. No markdown fences. No backticks. Start with 'mindmap'."
    )
    fallback_used: bool = Field(default=False, description="True if this is a fallback diagram")


class QuizOption(BaseModel):
    text: str
    is_correct: bool


class QuizQuestion(BaseModel):
    question: str
    options: list[QuizOption] = Field(min_length=4, max_length=4, description="Exactly 4 options")
    explanation: str = Field(description="Why the correct answer is right")


class QuizOutput(BaseModel):
    questions: list[QuizQuestion] = Field(min_length=3, max_length=3, description="Exactly 3 questions")
