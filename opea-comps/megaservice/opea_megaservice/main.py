import os
from enum import Enum
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from comps.cores.mega.micro_service import MicroService
from comps.cores.mega.constants import ServiceType, ServiceRoleType
from comps.cores.mega.orchestrator import ServiceOrchestrator
import uvicorn

# Environment variables for service configuration
EMBEDDING_SERVICE_HOST_IP = os.getenv("EMBEDDING_SERVICE_HOST_IP", "0.0.0.0")
EMBEDDING_SERVICE_PORT = int(os.getenv("EMBEDDING_SERVICE_PORT", 6000))
LLM_SERVICE_HOST_IP = os.getenv("LLM_SERVICE_HOST_IP", "0.0.0.0")
LLM_SERVICE_PORT = int(os.getenv("LLM_SERVICE_PORT", 9000))


class ChatRequest(BaseModel):
    messages: List[dict]

class EmbeddingRequest(BaseModel):
    text: str

class MegaService(MicroService):
    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__(
            name="mega",
            host=host,
            port=port,
            endpoint="/",
            service_role=ServiceRoleType.MICROSERVICE,
            service_type=ServiceType.UNDEFINED,
            description="OPEA Mega Service - Orchestrates LLM and Embedding services",
            use_remote_service=False
        )
        self.service_orchestrator = ServiceOrchestrator()
        self.setup_routes()
        self.setup_services()

    def setup_services(self):
        # Create embedding service
        embedding = MicroService(
            name="embedding",
            host=EMBEDDING_SERVICE_HOST_IP,
            port=EMBEDDING_SERVICE_PORT,
            endpoint="/v1/embeddings",
            use_remote_service=True,
            service_type=ServiceType.EMBEDDING,
        )

        # Create LLM service
        llm = MicroService(
            name="llm",
            host=LLM_SERVICE_HOST_IP,
            port=LLM_SERVICE_PORT,
            endpoint="/v1/chat/completions",
            use_remote_service=True,
            service_type=ServiceType.LLM,
        )

        # Add services to orchestrator and define flow
        self.service_orchestrator.add(embedding).add(llm)
        self.service_orchestrator.flow_to(embedding, llm)

    def setup_routes(self):
        @self.app.post("/v1/chat/completions")
        async def chat_completion(request: ChatRequest):
            try:
                llm_service = self.service_orchestrator.get_service("llm")
                response = await llm_service.process(request.messages)
                return response
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/v1/embeddings")
        async def create_embedding(request: EmbeddingRequest):
            try:
                embedding_service = self.service_orchestrator.get_service("embedding")
                response = await embedding_service.process(request.text)
                return response
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    service = MegaService()
    service.start()  # Use the start() method from HTTPService base class
