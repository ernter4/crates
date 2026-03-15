import io
from typing import Annotated

from PIL import Image

from app.ordering.services.ocr.ocr import OCR
from fastapi import Depends, UploadFile

from app.shared.dependencies import SessionDep


async def get_ocr_client(session:SessionDep, file:UploadFile):
    contents = await file.read()
    img = Image.open(io.BytesIO(contents))
    ocr_client = OCR(session = session,image= img)
    return ocr_client
OcrClientDep = Annotated[OCR,Depends(get_ocr_client)]
