from typing import Annotated

from fastapi import Header, HTTPException, Depends

from app.shared.models import User


def get_current_user(    username:Annotated[str, Header( alias="Remote-User",include_in_schema=False) ],

                         groups:Annotated[str, Header(alias="Remote-Groups",include_in_schema=False)  ]) -> User:

    return User(
        username=username,
        groups=groups.split(",")
    )


def get_test_user():
    return User(
        username="test",
        groups=['admin'])

def authorize(
        authorized_groups: list[str],
        user:User
       ) -> None:
    if not any(group in authorized_groups for group in user.groups):
        raise HTTPException(403,"forbidden")


