import io
import os
from typing import Annotated

from PIL import Image,ImageColor
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import Response
from sqlmodel import Session

from app.ordering.dependencies import OcrClientDep
from app.shared.dependencies import SessionDep

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
TEST_IMAGE_PATH = os.path.join(BASE_DIR, "old", "test.jpeg")
TEST_IMAGE_PATH_2 = os.path.join(BASE_DIR, "old", "output.jpeg")


@router.post("/update")
async def update_inventory(file: UploadFile,session:SessionDep,ocr_client: OcrClientDep):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    ocr_client.set_image(img)
    ocr_client.set_session(session)
    ocr_client.process_image()
    for record in ocr_client.records:
        ocr_client.draw_record(record.crate_id, ImageColor.getrgb("Red"))
    # PNG-Format encodieren
    buffer = io.BytesIO()
    ocr_client.image.save(buffer, format='PNG')
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="image/png")
@router.post("/test", response_class=Response)
def test(session:SessionDep,ocr_client: OcrClientDep):
    pass
