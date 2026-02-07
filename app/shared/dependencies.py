from typing import Annotated

from fastapi import Depends
from sqlmodel import Session
from .models import User
from .models import User
from app.shared.auth import get_current_user
from app.shared.database import get_session

SessionDep = Annotated[Session, Depends(get_session)]



CurrentUserDep = Annotated[User,Depends(get_current_user)]