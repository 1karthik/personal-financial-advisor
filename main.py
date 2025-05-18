from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.schema import AgentFinish
from agent import agent_executor
import shutil
import os
import asyncio

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    filename: Optional[str] = None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"filename": file.filename, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.post("/query")
async def query_file(request: QueryRequest):
    if request.filename:
        file_path = os.path.join(UPLOAD_DIR, request.filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        final_query = f"{request.query} in {file_path}"
    else:
        # No filename: just plain query
        final_query = request.query

    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(None, lambda: agent_executor.invoke({"input": final_query}))
        
        # Handle response as before...
        if isinstance(result, AgentFinish):
            return {"response": result.return_values.get("output", "No output")}
        if "intermediate_steps" in result:
            steps = result["intermediate_steps"]
            if steps:
                last_step = steps[-1]
                if isinstance(last_step, tuple) and len(last_step) > 1:
                    return {"response": str(last_step[1])}
        return {"response": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
