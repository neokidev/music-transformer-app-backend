from examples import bach_format0
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/examples/bach_format0")
async def examples_bach_format0():
    return bach_format0
