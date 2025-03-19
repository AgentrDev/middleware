from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agentr.server import Server
from mcp.server.sse import SseServerTransport
from starlette.routing import Route, Mount

mcp = Server(port=8000)
sse = SseServerTransport("/messages/")


async def handle_sse(request):
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        return await mcp._mcp_server.run(
            streams[0],
            streams[1],
            mcp._mcp_server.create_initialization_options(),
        )

app = FastAPI(
    title="AgentR API",
    description="API for AgentR platform",
    version="0.1.0",
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)



# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AgentR API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
