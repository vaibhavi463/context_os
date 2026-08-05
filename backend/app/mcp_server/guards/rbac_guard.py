from fastapi import HTTPException, status
from app.mcp_server.registry import tool_registry, MCPTool


class RBACScopeGuard:
    @staticmethod
    def validate_tool_access(tool_name: str, user_role: str) -> MCPTool:
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP Tool '{tool_name}' not found in catalog."
            )

        if not tool_registry._role_has_scope(user_role, tool.required_scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role}' lacks required scope '{tool.required_scope}' for tool '{tool_name}'."
            )

        return tool
