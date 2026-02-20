from typing import Annotated


from app.ordering.services.ocr.ocr import OCR
from fastapi import Depends




def get_ocr_client():
    ocr = OCR()
    return ocr
OcrClientDep = Annotated[OCR,Depends(get_ocr_client)]
