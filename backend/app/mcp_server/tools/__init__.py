from app.mcp_server.tools.read_tools import register_read_tools
from app.mcp_server.tools.write_tools import register_write_tools


def init_tools() -> None:
    register_read_tools()
    register_write_tools()


init_tools()
