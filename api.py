"""
AI Web Research Agent - FastAPI Web Interface
Vaixus Technologies | Built by VIJAYARAJAN S

Run with: uvicorn api:app --reload --port 8000
Docs at:  http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from agent.research_agent import ResearchAgent

app = FastAPI(
    title="Vaixus AI Research Agent API",
    description="Generate AI-powered intelligence reports on any company or topic.",
    version="1.0.0",
    contact={
        "name": "VIJAYARAJAN S",
        "url": "https://vaixus.tech",
        "email": "vijay.vaixus@gmail.com"
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (use Redis/Supabase in production)
jobs: dict = {}
executor = ThreadPoolExecutor(max_workers=3)


class ResearchRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
        max_length=200,
        example="Tesla Motors",
        description="Company name or topic to research"
    )


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    topic: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    topic: str
    report: Optional[str] = None
    file_path: Optional[str] = None
    sources_used: Optional[int] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


def run_research_job(job_id: str, topic: str):
    """Execute research in background thread."""
    try:
        jobs[job_id]["status"] = "running"
        agent = ResearchAgent()
        result = agent.run(topic)

        if result["success"]:
            jobs[job_id].update({
                "status": "completed",
                "report": result["report"],
                "file_path": result["file"],
                "sources_used": result["sources_used"],
                "completed_at": datetime.now().isoformat()
            })
        else:
            jobs[job_id].update({
                "status": "failed",
                "error": result["error"],
                "completed_at": datetime.now().isoformat()
            })

    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


@app.get("/")
def root():
    return {
        "service": "Vaixus AI Research Agent",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "built_by": "VIJAYARAJAN S | vaixus.tech"
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/research", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a research job on a company or topic.
    Returns a job_id to track progress.
    Research runs asynchronously — poll /research/{job_id} for results.
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "topic": request.topic,
        "report": None,
        "file_path": None,
        "sources_used": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }

    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, run_research_job, job_id, request.topic)

    return ResearchResponse(
        job_id=job_id,
        status="queued",
        topic=request.topic,
        message=f"Research started. Poll /research/{job_id} for results."
    )


@app.get("/research/{job_id}", response_model=JobStatusResponse)
def get_research_status(job_id: str):
    """
    Get the status and results of a research job.
    Status values: queued | running | completed | failed
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobStatusResponse(**job)


@app.get("/research")
def list_jobs():
    """List all research jobs with their status."""
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": j["job_id"],
                "topic": j["topic"],
                "status": j["status"],
                "created_at": j["created_at"]
            }
            for j in jobs.values()
        ]
    }


@app.delete("/research/{job_id}")
def delete_job(job_id: str):
    """Delete a completed job from memory."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs[job_id]
    return {"message": f"Job {job_id} deleted"}
