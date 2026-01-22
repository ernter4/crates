from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
load_dotenv()

from app.accounting.routers.router import router as accounting_router
app = FastAPI()

app.include_router(accounting_router, prefix="/accounting", tags=["accounting"])
if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)