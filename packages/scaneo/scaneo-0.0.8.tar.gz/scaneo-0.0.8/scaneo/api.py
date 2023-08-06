from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

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
    return "hello"


# this needs to be last
# get current script path
current_dir = os.path.dirname(os.path.realpath(__file__))
print(current_dir)
app.mount("/", StaticFiles(directory=current_dir + "/ui", html=True), name="ui")
