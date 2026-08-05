from dataclasses import dataclass, field
from typing import Callable, Any
from pydantic import BaseModel


@dataclass
class MCPTool:
    name: str
    description: str
    required_scope: str
    requires_approval: bool
    input_schema: type[BaseModel]
    executor: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> MCPTool | None:
        return self._tools.get(name)

    def list_tools(self, user_role: str) -> list[dict[str, Any]]:
        allowed_tools: list[dict[str, Any]] = []
        for tool in self._tools.values():
            if self._role_has_scope(user_role, tool.required_scope):
                allowed_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "requires_approval": tool.requires_approval,
                    "parameters": tool.input_schema.model_json_schema()
                })
        return allowed_tools

    @staticmethod
    def _role_has_scope(role: str, scope: str) -> bool:
        if role == "admin":
            return True
        role_scopes_map = {
            "ops_engineer": ["ops:read", "ops:write", "support:read"],
            "support_engineer": ["ops:read", "support:read", "support:write"],
            "read_only": ["ops:read", "support:read"]
        }
        user_scopes = role_scopes_map.get(role, [])
        return scope in user_scopes


tool_registry = ToolRegistry()
