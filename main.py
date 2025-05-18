from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from agent import agent_executor
from langchain.schema import AgentFinish

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_finance(request: QueryRequest):
    loop = asyncio.get_running_loop()
    try:
        result = await loop.run_in_executor(
            None,
            lambda: agent_executor.invoke({"input": request.query})
        )
        
        if isinstance(result, AgentFinish):
            return {"response": result.return_values.get("output", "No output")}
        
        # If we have intermediate steps, get the last observation
        if "intermediate_steps" in result:
            steps = result["intermediate_steps"]
            if steps:
                last_step = steps[-1]
                if isinstance(last_step, tuple) and len(last_step) > 1:
                    return {"response": str(last_step[1])}
        
        return {"response": str(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
