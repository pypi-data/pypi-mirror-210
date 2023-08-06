from fastapi import APIRouter

from .settings import settings

router = APIRouter(prefix="/test", tags=["test"])


@router.get("")
def test():
    # save file in the same dir from where the cli was started
    with open("test.txt", "w") as f:
        f.write("hello")
    print(settings)
    return "hello"
