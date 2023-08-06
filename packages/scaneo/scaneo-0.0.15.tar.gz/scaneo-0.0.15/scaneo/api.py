from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseSettings


# pydantic will parse the environment variables in a case sensitive way
class Settings(BaseSettings):
    data: str = "data"


settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/test")
def test():
    # save file in the same dir from where the cli was started
    with open("test.txt", "w") as f:
        f.write("hello")
    print(settings)
    return "hello"


# this needs to be last in order to not override other routes
# ui is in same directory as this file
app.mount(
    "/",
    StaticFiles(
        directory=os.path.dirname(os.path.realpath(__file__)) + "/ui", html=True
    ),
    name="ui",
)
