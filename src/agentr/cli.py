import typer
from loguru import logger
from agentr.server import Server
from typing import Literal

app = typer.Typer(
    name="agentr",
    help="CLI for AgentR platform",
    add_completion=False,
)


@app.command()
def run(transport: str = "stdio", port: int = 8000):
    logger.info("Running AgentR MCP Server")
    server = Server(port=port)
    server.run(transport=transport)

@app.command()
def install(client_name: str):
    logger.info(f"Installing AgentR App for client: {client_name}")
    user_id = typer.prompt("Enter your user ID")
    api_key = typer.prompt("Enter your API key", hide_input=True)
    logger.info(f"Done. Please restart the {client_name} to use AgentR")

def main():
    try:
        app()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    main()
