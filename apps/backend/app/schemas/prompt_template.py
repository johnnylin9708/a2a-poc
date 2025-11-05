"""
Prompt Template Pydantic schemas for request/response validation
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PromptTemplateCreateRequest(BaseModel):
    """Request body for creating a prompt template"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    agent_id: int = Field(..., description="Agent token ID")
    category: str = Field(..., description="Template category (e.g., coding, testing, analysis)")
    template_content: str = Field(..., description="The prompt template with placeholders")
    variables: List[str] = Field(default=[], description="List of variable names in the template")
    examples: Optional[List[Dict[str, str]]] = Field(default=None, description="Example inputs/outputs")
    is_public: bool = Field(default=False, description="Whether this template is publicly visible")
    tags: List[str] = Field(default=[], description="Tags for categorization")


class PromptTemplateUpdateRequest(BaseModel):
    """Request body for updating a prompt template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    template_content: Optional[str] = None
    variables: Optional[List[str]] = None
    examples: Optional[List[Dict[str, str]]] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(BaseModel):
    """Prompt template response"""
    template_id: str
    name: str
    description: str
    agent_id: int
    agent_name: str
    category: str
    template_content: str
    variables: List[str]
    examples: Optional[List[Dict[str, str]]]
    is_public: bool
    is_active: bool
    tags: List[str]
    usage_count: int
    created_at: datetime
    updated_at: datetime
    created_by: str


class PromptRenderRequest(BaseModel):
    """Request to render a prompt template with variables"""
    template_id: str
    variables: Dict[str, str] = Field(..., description="Variable name -> value mapping")


class PromptRenderResponse(BaseModel):
    """Rendered prompt response"""
    rendered_prompt: str
    template_id: str
    template_name: str

