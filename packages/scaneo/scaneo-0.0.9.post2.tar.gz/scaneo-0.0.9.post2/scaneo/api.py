from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
import argparse

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--reload", action="store_true", default=False)
    args = parser.parse_args()
    os.chdir(current_dir)
    uvicorn.run("api:app", host=args.host, port=args.port, reload=args.reload)
