"""Optional stdio MCP transport; tools can only read the token owner's records."""
from mcp.server.mcpserver import MCPServer
from .client import AnalyzerClient
from .agents import run_pipeline

mcp = MCPServer('Local Student Analyzer')

@mcp.tool()
def list_students(page: int = 1, page_size: int = 25) -> dict:
    """Read one page of owned student records; no modification tools are exposed."""
    if not 1 <= page <= 100000 or not 1 <= page_size <= 100:
        raise ValueError('Use a positive page and page_size between 1 and 100.')
    return AnalyzerClient().get('/api/students/', page=page, page_size=page_size)

@mcp.tool()
def list_subjects() -> dict:
    """List the available subject codes."""
    return AnalyzerClient().get('/api/subjects/')

@mcp.tool()
def summarize_first_page() -> dict:
    """Return a labelled sample summary through the two local agent adapters."""
    return run_pipeline()

if __name__ == '__main__': mcp.run(transport='stdio')
