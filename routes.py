import json
import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from adapters.elephant_adapter import ElephantAdapter
from models import models_list

PROXY = os.getenv("PROXY")

adapter = ElephantAdapter(proxy=PROXY)

api_router = APIRouter()


@api_router.api_route("/v1/chat/completions", methods=["POST", "OPTIONS"])
@api_router.api_route("/hf/v1/chat/completions", methods=["POST", "OPTIONS"])
async def chat(request: Request):
    openai_params = await request.json()
    if openai_params.get("stream", False):

        async def generate():
            async for response in adapter.chat(request):
                if response == "[DONE]":
                    yield "data: [DONE]"
                    break
                yield f"data: {json.dumps(response)}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = adapter.chat(request)
        openai_response = await response.__anext__()
        return JSONResponse(content=openai_response)


@api_router.get("/v1/models")
@api_router.get("/hf/v1/models")
async def models(request: Request):
    # return a dict with key "object" and "data", "object" value is "list", "data" values is models list
    return JSONResponse(content={"object": "list", "data": models_list})
