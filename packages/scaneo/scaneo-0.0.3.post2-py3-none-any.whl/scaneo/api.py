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
# get current directory
current_dir = os.getcwd()
print(current_dir)
app.mount("/", StaticFiles(directory=current_dir + "/build", html=True), name="ui")
