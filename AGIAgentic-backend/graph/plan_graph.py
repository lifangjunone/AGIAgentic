

from typing import Any, AsyncIterator

from langgraph.graph import StateGraph # type: ignore
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph # type: ignore

from graph.base_graph import BaseGraph
from graph.states.plan_state import PlanExecutorState





class PlanExecutionGraph(BaseGraph):
  """ A class to represent the plan execution graph. """

  def __init__(self, provider_name: str = "zhipu") -> None:
    """ Init """
    super().__init__('PlanExecutionGraph', provider_name)
    self.graph = self.build_graph() # type: ignore

  # To build a Graph
  def build_graph(self) -> CompiledStateGraph: # type: ignore
    """ build a graph"""

    workflow = StateGraph(PlanExecutorState)

    # To add nodes
    # add analyze task and generate execution plan node
    workflow.add_node('analyze_and_plan', self._analyze_and_plan) # type: ignore

    # add check and execute node
    workflow.add_node('check_and_execute', self._check_and_execute_node) # type: ignore

    # add summary response node
    workflow.add_node('summary_response', self._summary_response) # type: ignore

    # To define entry point
    workflow.set_entry_point('analyze_and_plan')

    # To define fixed edges
    workflow.add_edge('analyze_and_plan', 'check_and_execute')

    # To define condictional edges
    workflow.add_conditional_edges(
      source="check_and_execute",
      path=self._jump_condictional,  # type: ignore
      path_map={
        "next_node": "check_and_execute",
        "completed": "summary_response",
      }
    )
    return workflow.compile() # type: ignore

  def _analyze_and_plan(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Analyze the task and generate plan"""
    state["status"] = "analyzed"
    state["user_task"] = state.get("user_task", "")
    state["task_analysis"] = "Detailed analysis of the user task."
    state["execution_plans"] = [{"step": "step1"}, {"step": "step2"}]
    return state
  
  def _check_and_execute_node(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Check and execute task"""
    current_step = state.get("current_step")
    if current_step >= len(state.get("execution_plans", [])):
      state["status"] = "completed"
      return state
    state["status"] = "in_progress"
    state["step_results"].append({"step": "step1", "result": "step1 result"})
    state["current_step"] += 1
    return state
  
  def _summary_response(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ summary result"""
    state["status"] = "completed"
    state["step_results"].append({"summary": "All steps completed successfully."})
    return state
  
  def _jump_condictional(self, state: PlanExecutorState) -> str: # type: ignore
    """ jump condictional"""
    status = state.get("status")
    match status:
      case "completed": 
        return "completed"
      case "failed":
        return "completed"
      case _:
        return "next_node"

  # Call to execute the graph
  async def chat_with_planning_stream(self, thread_id: str, user_task: str = "") -> AsyncIterator[Any]:
    """ chat with planning"""
    init_data = PlanExecutorState(
      user_id=thread_id,
      session_id=thread_id,
      request_id=thread_id,
      messages=HumanMessage(content=user_task),  # type: ignore
      streaming_chunks=[],
      status="initialized",
      error="",
      timing_info={},
      user_task=user_task,
      task_analysis="",
      execution_plans=[],
      current_step=0,
      step_results=[],
    )
    async for event in self.graph.astream_events(init_data):  # type: ignore
        yield event