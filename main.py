import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from app.shared.auth import get_current_user, get_test_user

load_dotenv()

from app.accounting.routers.router import router as accounting_router
from app.ordering.routers.router import router as ordering_router
app = FastAPI(root_path="/api")

origins = os.getenv("CRATES_CORS_ALLOWED_ORIGINS").strip().split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounting_router, prefix="/accounting", tags=["accounting"])
app.include_router(ordering_router, prefix="/ordering", tags=["ordering"])
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
if os.getenv("CRATES_DISABLE_AUTH") == "True":
    app.dependency_overrides[ get_current_user]= get_test_user


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