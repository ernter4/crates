from sqlmodel import SQLModel


class ImageResponse(SQLModel):
    image:str
