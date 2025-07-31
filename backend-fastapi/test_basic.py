"""
基本FastAPI测试
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="基本测试")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    return {"status": "ok"}

if __name__ == "__main__":
    print("启动基本测试服务...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
