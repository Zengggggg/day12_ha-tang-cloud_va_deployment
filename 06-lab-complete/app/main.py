import os
import sys
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import enforce_daily_budget
from app.rate_limiter import enforce_rate_limit
from core.route_planner import resolve_location_coords
from services.agent_service import chat_with_agent
from services.tool_workflow import run_trip_planner_workflow
from utils.data_loader import list_station_names, load_stations

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    origin: str
    destination: str
    soc_current: float
    soc_comfort: float


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


@app.get("/health")
def health_check() -> dict:
    return {"ok": True, "env": settings.app_env}


@app.get("/api/stations")
def get_stations(_: None = Depends(verify_api_key)) -> dict:
    return {"stations": list_station_names()}


@app.get("/api/stations/all")
def get_all_stations(_: None = Depends(verify_api_key)) -> dict:
    stations = load_stations()
    return {"stations": [s.__dict__ for s in stations]}


@app.post("/api/plan")
def plan_route(
    req: PlanRequest,
    request: Request,
    _: None = Depends(verify_api_key),
) -> dict:
    try:
        enforce_rate_limit(request)
        enforce_daily_budget()
        workflow_result = run_trip_planner_workflow(
            origin=req.origin,
            destination=req.destination,
            soc_current=req.soc_current / 100.0,
            soc_comfort=req.soc_comfort / 100.0,
            include_geometry=True,
        )
        origin_coords = resolve_location_coords(req.origin)
        destination_coords = resolve_location_coords(req.destination)
        workflow_result["coords"] = {
            "origin": (
                {"lat": origin_coords[0], "lon": origin_coords[1]}
                if origin_coords
                else None
            ),
            "destination": (
                {"lat": destination_coords[0], "lon": destination_coords[1]}
                if destination_coords
                else None
            ),
        }
        return workflow_result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/chat")
def agent_chat(
    req: ChatRequest,
    request: Request,
    _: None = Depends(verify_api_key),
) -> dict:
    try:
        enforce_rate_limit(request)
        enforce_daily_budget()
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in req.messages]
        result = chat_with_agent(messages_dict)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
