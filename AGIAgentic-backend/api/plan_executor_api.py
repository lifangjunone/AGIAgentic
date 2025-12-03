

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse


from api.schemas.plan_executor import PlanExecutorReqSchema

from graph.plan_graph import PlanExecutionGraph


router = APIRouter(prefix="/plan_executor", tags=["plan_executor"])



@router.post("/stream")
async def stream_plan_execution(req: PlanExecutorReqSchema):
    """ Endpoint to stream plan execution steps.
    Returns:
        dict: A message indicating the endpoint is working.
    """

    async def generate_astream():
        async for event in plan_executor_graph.chat_with_planning_stream(thread_id=req.user_id, user_task=req.user_task):
          yield event

    # Create plan execution graph and execute steps here

    plan_executor_graph = PlanExecutionGraph()
    plan_executor_graph.user_id = req.user_id
    return EventSourceResponse(
        generate_astream()
    )
