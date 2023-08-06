from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
from spai.storage import Storage

app = FastAPI(title="analytics")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def analytics():
    try:
        storage = Storage("data")
        analytics = storage.read("stats.csv")
        return json.loads(analytics.to_json())
    except Exception as e:
        return {}


# need this to run in background
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
