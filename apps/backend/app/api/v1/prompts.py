"""
Prompt Template API endpoints
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
import logging

from app.schemas.prompt_template import (
    PromptTemplateCreateRequest,
    PromptTemplateUpdateRequest,
    PromptTemplateResponse,
    PromptRenderRequest,
    PromptRenderResponse
)
from app.services.prompt_service import prompt_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(request: PromptTemplateCreateRequest):
    """
    Create a new prompt template

    Prompt templates allow agents to have standardized, reusable prompts
    with variable placeholders for dynamic content
    """
    try:
        template = await prompt_service.create_template(
            agent_id=request.agent_id,
            name=request.name,
            description=request.description,
            category=request.category,
            template_content=request.template_content,
            variables=request.variables,
            examples=request.examples,
            is_public=request.is_public,
            tags=request.tags
        )

        return template

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create prompt template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create prompt template: {str(e)}"
        )


@router.get("/{template_id}", response_model=PromptTemplateResponse)
async def get_prompt_template(template_id: str):
    """Get prompt template by ID"""
    try:
        template = await prompt_service.get_template(template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )

        return template

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get prompt template: {str(e)}"
        )


@router.get("/", response_model=dict)
async def list_prompt_templates(
    agent_id: Optional[int] = Query(None, description="Filter by agent ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List prompt templates with optional filters"""
    try:
        tag_list = tags.split(",") if tags else None

        result = await prompt_service.list_templates(
            agent_id=agent_id,
            category=category,
            is_public=is_public,
            tags=tag_list,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        logger.error(f"Failed to list prompt templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list prompt templates: {str(e)}"
        )


@router.put("/{template_id}", response_model=dict)
async def update_prompt_template(
    template_id: str,
    request: PromptTemplateUpdateRequest
):
    """Update prompt template"""
    try:
        # Convert request to dict and remove None values
        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )

        success = await prompt_service.update_template(template_id, update_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )

        return {"message": "Template updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update prompt template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prompt template: {str(e)}"
        )


@router.delete("/{template_id}", response_model=dict)
async def delete_prompt_template(template_id: str):
    """Delete (deactivate) prompt template"""
    try:
        success = await prompt_service.delete_template(template_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )

        return {"message": "Template deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prompt template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prompt template: {str(e)}"
        )


@router.post("/render", response_model=PromptRenderResponse)
async def render_prompt_template(request: PromptRenderRequest):
    """
    Render a prompt template with provided variables

    This endpoint takes a template ID and variable values,
    and returns the rendered prompt ready to use
    """
    try:
        # Get template first
        template = await prompt_service.get_template(request.template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {request.template_id} not found"
            )

        # Render template
        rendered = await prompt_service.render_template(
            request.template_id,
            request.variables
        )

        return {
            "rendered_prompt": rendered,
            "template_id": request.template_id,
            "template_name": template["name"]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to render prompt template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to render prompt template: {str(e)}"
        )


@router.get("/categories/list", response_model=List[str])
async def get_template_categories():
    """Get all template categories"""
    try:
        categories = await prompt_service.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Failed to get categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/popular/list", response_model=List[PromptTemplateResponse])
async def get_popular_templates(limit: int = Query(10, ge=1, le=50)):
    """Get most popular (most used) templates"""
    try:
        templates = await prompt_service.get_popular_templates(limit)
        return templates
    except Exception as e:
        logger.error(f"Failed to get popular templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get popular templates: {str(e)}"
        )

