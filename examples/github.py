from mcp.server.fastmcp import FastMCP
import httpx
import os

mcp = FastMCP("GitHub", port=8003)

@mcp.tool()
def set_github_token(token: str) -> str:
    """Set the GitHub personal access token
    
    Args:
        token: The GitHub personal access token to set
    """
    os.environ["GITHUB_TOKEN"] = token
    return f"GitHub token set successfully"

@mcp.tool()
def star_repository(repo_full_name: str) -> str:
    """Star a GitHub repository
    
    Args:
        repo_full_name: The full name of the repository (e.g. 'owner/repo')
        
    Returns:
        A confirmation message
    """
    if "GITHUB_TOKEN" not in os.environ:
        return "GitHub token not set. Please set it using the set_github_token tool"
    
    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/user/starred/{repo_full_name}"
    response = httpx.put(url, headers=headers)
    
    if response.status_code == 204:
        return f"Successfully starred repository {repo_full_name}"
    elif response.status_code == 404:
        return f"Repository {repo_full_name} not found"
    else:
        return f"Error starring repository: {response.text}"

if __name__ == "__main__":
    mcp.run(transport='sse')
