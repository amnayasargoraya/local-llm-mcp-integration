#!/usr/bin/env python3

import asyncio
import json
from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}

class ToolResponse(BaseModel):
    success: bool
    result: List[Dict[str, str]]
    error: str = None

class Tool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any]

class MCPDemoServer:
    def __init__(self):
        self.name = "demo-server"
        self.version = "1.0.0"
        logger.info(f"MCP Server '{self.name}' Version {self.version} initialisiert")

    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="ask_llm",
                description="Frage das lokale LLM (Ollama - mistral)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Eingabeaufforderung für das Sprachmodell"
                        }
                    },
                    "required": ["prompt"]
                }
            )
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
        logger.info(f"Tool aufgerufen: {name} mit Argumenten: {arguments}")
        if name == "ask_llm":
            import httpx
            prompt = arguments.get("prompt", "").strip()
            if not prompt:
                return [{"type": "text", "text": "❌ Kein Prompt angegeben."}]
            try:
                response = httpx.stream(
                    "POST",
                    "http://ollama-llm:11434/api/generate",
                    json={
                        "model": "mistral",
                        "prompt": prompt
                    },
                    timeout=120.0
                )

                chunks = []
                with response as r:
                    for line in r.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                chunks.append(data.get("response", ""))
                            except json.JSONDecodeError:
                                continue

                text = "".join(chunks).strip()
                if not text:
                    text = "[⚠️ Keine Antwort vom Modell]"

                return [{"type": "text", "text": f"🧠 LLM-Antwort: {text}"}]

            except Exception as e:
                return [{"type": "text", "text": f"❌ Fehler beim LLM-Aufruf: {str(e)}"}]
        else:
            return [{"type": "text", "text": f"❌ Unbekanntes Tool: {name}"}]

app = FastAPI(
    title="MCP Demo Server",
    version="1.0.0",
    description="Demo mit Ollama (mistral)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_instance = MCPDemoServer()

@app.get("/")
async def root():
    return {"message": "🎉 MCP Demo Server läuft", "tools": [t.name for t in server_instance.get_tools()]}

@app.get("/tools")
async def list_tools():
    return {"tools": [tool.dict() for tool in server_instance.get_tools()]}

@app.post("/call-tool", response_model=ToolResponse)
async def call_tool(request: ToolCallRequest):
    try:
        result = server_instance.execute_tool(request.name, request.arguments)
        return ToolResponse(success=True, result=result)
    except Exception as e:
        return ToolResponse(success=False, result=[], error=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    print("🚀 Starte MCP Demo Server mit mistral...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
