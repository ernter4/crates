from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
load_dotenv()

from app.accounting.routers.router import router as accounting_router
app = FastAPI()

app.include_router(accounting_router, prefix="/accounting", tags=["accounting"])
if __name__ == "__main__":

    # Use manual server startup for debugging compatibility
    import asyncio
    from uvicorn import Config, Server

    config = Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = Server(config)

    # Run without loop_factory parameter to avoid debugger conflicts
    asyncio.run(server.serve())
    #uvicorn.run(app, host="0.0.0.0", port=8000)