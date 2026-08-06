from app.mcp_server.registry import MCPTool, tool_registry
from fastapi import HTTPException, status


class ScopePermissionDeniedException(HTTPException):
    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class RBACGuard:
    def validate_tool_access(
        self,
        user_role: str,
        required_scope: str | None = None,
        tool_name: str | None = None,
    ) -> MCPTool | None:
        if tool_name:
            tool = tool_registry.get_tool(tool_name)
            if not tool:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"MCP Tool '{tool_name}' not found in catalog.",
                )
            required_scope = tool.required_scope
        else:
            tool = None

        if required_scope and not tool_registry._role_has_scope(user_role, required_scope):
            raise ScopePermissionDeniedException(
                detail=f"User role '{user_role}' lacks required scope '{required_scope}'."
            )

        return tool


class RBACScopeGuard:
    @staticmethod
    def validate_tool_access(tool_name: str, user_role: str) -> MCPTool:
        guard = RBACGuard()
        tool = guard.validate_tool_access(user_role=user_role, tool_name=tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP Tool '{tool_name}' not found in catalog.",
            )
        return tool

