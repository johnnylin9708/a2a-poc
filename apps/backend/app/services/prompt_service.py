"""
Prompt Template Service for managing agent prompt templates
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import re
import logging

from app.database import get_agents_collection

logger = logging.getLogger(__name__)


class PromptTemplateService:
    """Service for managing prompt templates"""

    def __init__(self):
        self._templates_collection = None
        self._agents_collection = None
        logger.info("✅ Prompt Template Service initialized")

    @property
    def templates_collection(self):
        """Lazy loading of templates collection"""
        if self._templates_collection is None:
            from app.database import get_database
            self._templates_collection = get_database().prompt_templates
        return self._templates_collection

    @property
    def agents_collection(self):
        """Lazy loading of agents collection"""
        if self._agents_collection is None:
            self._agents_collection = get_agents_collection()
        return self._agents_collection

    async def create_template(
        self,
        agent_id: int,
        name: str,
        description: str,
        category: str,
        template_content: str,
        variables: List[str],
        examples: Optional[List[Dict]] = None,
        is_public: bool = False,
        tags: List[str] = None,
        created_by: str = None
    ) -> Dict[str, Any]:
        """
        Create a new prompt template

        Args:
            agent_id: Agent token ID
            name: Template name
            description: Template description
            category: Template category
            template_content: Prompt template with {variable} placeholders
            variables: List of variable names
            examples: Example inputs/outputs
            is_public: Whether template is publicly visible
            tags: Tags for categorization
            created_by: Creator's address

        Returns:
            Created template document
        """
        try:
            # Verify agent exists
            agent = await self.agents_collection.find_one({"token_id": agent_id})
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            # Extract variables from template if not provided
            if not variables:
                variables = self._extract_variables(template_content)

            template_id = str(uuid.uuid4())

            template_doc = {
                "template_id": template_id,
                "name": name,
                "description": description,
                "agent_id": agent_id,
                "agent_name": agent.get("name", f"Agent #{agent_id}"),
                "category": category,
                "template_content": template_content,
                "variables": variables,
                "examples": examples or [],
                "is_public": is_public,
                "is_active": True,
                "tags": tags or [],
                "usage_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": created_by or "unknown"
            }

            await self.templates_collection.insert_one(template_doc)

            logger.info(f"✅ Prompt template {template_id} created for agent {agent_id}")

            # Remove MongoDB _id
            template_doc.pop("_id", None)

            return template_doc

        except Exception as e:
            logger.error(f"❌ Failed to create prompt template: {e}")
            raise

    def _extract_variables(self, template_content: str) -> List[str]:
        """
        Extract variable names from template content

        Variables are defined as {variable_name}

        Args:
            template_content: Template string with {variables}

        Returns:
            List of variable names
        """
        pattern = r'\{(\w+)\}'
        matches = re.findall(pattern, template_content)
        return list(set(matches))  # Remove duplicates

    async def get_template(self, template_id: str) -> Optional[Dict]:
        """Get template by ID"""
        try:
            template = await self.templates_collection.find_one({"template_id": template_id})

            if template:
                template.pop("_id", None)

            return template

        except Exception as e:
            logger.error(f"❌ Failed to get template: {e}")
            return None

    async def list_templates(
        self,
        agent_id: Optional[int] = None,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List prompt templates with filters

        Args:
            agent_id: Filter by agent ID
            category: Filter by category
            is_public: Filter by public/private
            tags: Filter by tags
            limit: Max results
            offset: Results offset

        Returns:
            Dict with templates and pagination info
        """
        try:
            query = {"is_active": True}

            if agent_id is not None:
                query["agent_id"] = agent_id

            if category is not None:
                query["category"] = category

            if is_public is not None:
                query["is_public"] = is_public

            if tags:
                query["tags"] = {"$in": tags}

            total = await self.templates_collection.count_documents(query)

            cursor = self.templates_collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
            templates = await cursor.to_list(length=limit)

            # Remove MongoDB _id
            for template in templates:
                template.pop("_id", None)

            return {
                "templates": templates,
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"❌ Failed to list templates: {e}")
            raise

    async def update_template(
        self,
        template_id: str,
        update_data: Dict[str, Any]
    ) -> bool:
        """
        Update prompt template

        Args:
            template_id: Template ID
            update_data: Fields to update

        Returns:
            True if updated successfully
        """
        try:
            # If template_content is updated, re-extract variables
            if "template_content" in update_data and "variables" not in update_data:
                update_data["variables"] = self._extract_variables(update_data["template_content"])

            update_data["updated_at"] = datetime.utcnow()

            result = await self.templates_collection.update_one(
                {"template_id": template_id},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"✅ Template {template_id} updated")
                return True
            else:
                logger.warning(f"⚠️ Template {template_id} not found or not updated")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to update template: {e}")
            raise

    async def delete_template(self, template_id: str) -> bool:
        """
        Soft delete a template (set is_active to False)

        Args:
            template_id: Template ID

        Returns:
            True if deleted successfully
        """
        try:
            result = await self.templates_collection.update_one(
                {"template_id": template_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                logger.info(f"✅ Template {template_id} deleted")
                return True
            else:
                logger.warning(f"⚠️ Template {template_id} not found")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to delete template: {e}")
            raise

    async def render_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> Optional[str]:
        """
        Render a prompt template with provided variables

        Args:
            template_id: Template ID
            variables: Variable name -> value mapping

        Returns:
            Rendered prompt string
        """
        try:
            template = await self.get_template(template_id)

            if not template:
                raise ValueError(f"Template {template_id} not found")

            template_content = template["template_content"]
            template_vars = template["variables"]

            # Check if all required variables are provided
            missing_vars = set(template_vars) - set(variables.keys())
            if missing_vars:
                raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

            # Render template
            rendered = template_content
            for var_name, var_value in variables.items():
                rendered = rendered.replace(f"{{{var_name}}}", var_value)

            # Increment usage count
            await self.templates_collection.update_one(
                {"template_id": template_id},
                {"$inc": {"usage_count": 1}}
            )

            logger.info(f"✅ Template {template_id} rendered")

            return rendered

        except Exception as e:
            logger.error(f"❌ Failed to render template: {e}")
            raise

    async def get_categories(self) -> List[str]:
        """Get all unique template categories"""
        try:
            categories = await self.templates_collection.distinct("category", {"is_active": True})
            return sorted(categories)
        except Exception as e:
            logger.error(f"❌ Failed to get categories: {e}")
            return []

    async def get_popular_templates(self, limit: int = 10) -> List[Dict]:
        """Get most used templates"""
        try:
            cursor = self.templates_collection.find(
                {"is_public": True, "is_active": True}
            ).sort("usage_count", -1).limit(limit)

            templates = await cursor.to_list(length=limit)

            for template in templates:
                template.pop("_id", None)

            return templates

        except Exception as e:
            logger.error(f"❌ Failed to get popular templates: {e}")
            return []


# Create singleton instance
prompt_service = PromptTemplateService()

