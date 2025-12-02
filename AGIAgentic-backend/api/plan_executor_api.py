

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse


from api.schemas.plan_executor import PlanExecutorReqSchema

from graph.plan_graph import PlanExecutionGraph
from utils.llm.llm_util import serializable_llm_result


router = APIRouter(prefix="/plan_executor", tags=["plan_executor"])



@router.post("/stream")
def stream_plan_execution(req: PlanExecutorReqSchema):
    """ Endpoint to stream plan execution steps.
    Returns:
        dict: A message indicating the endpoint is working.
    """

    async def generate_astream(plan_executor_graph: PlanExecutionGraph):
        async for event in plan_executor_graph.chat_with_planning_stream(thread_id=req.user_id, user_task=req.user_task):
          yield f"data: {serializable_llm_result(event)}\n\n"

    # Create plan execution graph and execute steps here

    plan_executor_graph = PlanExecutionGraph()
    plan_executor_graph.user_id = req.user_id
    return StreamingResponse(
        generate_astream(plan_executor_graph),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
