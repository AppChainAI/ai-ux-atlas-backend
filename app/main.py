from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from routes.gen_map import generate_journey_map


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI UX Atlas",
    description="AI UX Atlas Backend",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info({
        "method": request.method,
        "path": request.url.path,
        "query_params": str(request.query_params),
        "client_host": request.client.host,
        "duration": f"{duration:.2f}s",
        "status_code": response.status_code,
        "user_agent": request.headers.get("user-agent")
    })
    
    return response

@app.get("/ping")
async def ping():
    """
    健康检查接口
    """
    return {
        "status": "ok",
        "message": "pong",
        "timestamp": time.time()
    }

@app.websocket("/ws/generate-map")
async def websocket_endpoint(websocket: WebSocket):
    await generate_journey_map(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
