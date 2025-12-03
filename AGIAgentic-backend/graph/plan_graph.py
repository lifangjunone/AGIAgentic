
import time
import asyncio

from datetime import datetime

from langgraph.graph import StateGraph # type: ignore
from typing import Any, AsyncIterator, Dict, List
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent # type: ignore
from langgraph.graph.state import CompiledStateGraph # type: ignore


from common.logger import logger
from utils.json_util import json_match
from graph.base_graph import BaseGraph
from graph.states.plan_state import PlanExecutorState
from prompts.plan_executor_prompt import planning_prompt, react_prompt, summary_response_prompt



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

  def statistic_timing(self, start_time: float, operation_name: str) -> Dict[str, Any]:
    """ statistic timing info
    Args:
        start_time (float): start time
        operation_name (str): operation name
    Returns:
        Dict[str, Any]: timing info
    """
    duration = time.time() - start_time
    return {
        f"{operation_name}_duration": round(duration, 2),
        f"{operation_name}_timestamp": datetime.now().isoformat()
    }

  def _analyze_and_plan(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Analyze the task and generate plan"""

    logger.info("Starting Analyzing task and generating execution plan...")
    start_time = time.time()
    messages = [HumanMessage(content=planning_prompt.format(user_task=state.get("user_task", "")))]  # type: ignore
    plan = self.reason_llm.invoke(messages)
    json_plan = json_match(plan.content)  # type: ignore
    logger.debug(f"Generated execution plan: {json_plan}")

    if not json_plan or "execution_plans" not in json_plan:
      state["status"] = "failed"
      state["error"] = "Failed to generate valid execution plan."
      return state

    state["task_analysis"] = json_plan.get("task_analysis", "")
    state["execution_plans"] = json_plan.get("execution_plans", [])
    state["current_step"] = 0
    state["timing_info"] = self.statistic_timing(start_time, "analyze_and_plan")
    return state
  
  def _check_and_execute_node(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Check and execute task"""
    current_step = state.get("current_step")
    execution_plans = state.get("execution_plans", [])

    logger.info(f"current_step: {current_step}, total_steps: {len(execution_plans)}")
    if current_step >= len(execution_plans):
      state["status"] = "completed"
      return state
    
    current_node = execution_plans[current_step]
    logger.debug(f"Executing step {current_step + 1}: {current_node}")

    # Execute the current step
    execution_result = self._do_execute(current_node, current_step)
    state["step_results"].append(execution_result)
    state["current_step"] += 1

    return state
  
  def _summary_response(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ summary result"""

    start_time = time.time()
    task_analysis = state.get("task_analysis")
    execution_plan = state.get("execution_plan")
    step_results = state.get("step_results")

    messages = [HumanMessage(content=summary_response_prompt.format(
      user_task=state.get("user_task", ""),
      task_analysis=task_analysis,
      execution_plan=execution_plan,
      step_results=step_results
    ))]  # type: ignore

    summary = self.reason_llm.invoke(messages)
    state["timing_info"].update(self.statistic_timing(start_time, "response_generation"))
    state["status"] = "completed"

    # Calculate total duration
    total_duration = (
        state["timing_info"].get("analyze_and_plan_duration", 0) +
        state["timing_info"].get("response_generation_duration", 0)
    )

    state["streaming_chunks"].append({
        "step": "completed",
        "message": f"🎉 任务完成！总耗时: {total_duration:.2f}秒", # type: ignore
        "data": {
            "response": summary.content, # type: ignore
            "timing_info": state["timing_info"],
            "total_nodes": len(state.get("execution_plan", [])),
            "completed_nodes": len(state.get("step_results", [])),
            "step_results": state.get("step_results", []),
            "execution_plan": state.get("execution_plan", [])
        }
    })
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

  def _format_tools_list(self, tools: List[Any]) -> List[str]:
    """ format tools list
    Args:
        tools (List): tools list
    Returns:
        List[str]: formatted tools list"""
    tools_list: List[str] = []
    for t in tools:
        if hasattr(t, 'name') and hasattr(t, 'description'):
            tools_list.append(f"- {t.name}: {t.description}")
        else:
            tools_list.append(f"- {t.__name__ if hasattr(t, '__name__') else str(t)}")
    return tools_list

  def _extract_execution_result(self, result: Any, node_description: str = ""): # type: ignore
      """提取执行结果 - 公共方法"""
      execution_result = ""
      try:
          if result and isinstance(result, dict):
              if "messages" in result:
                  messages = result["messages"] # type: ignore
                  if messages: 
                      # 查找最后一个AI消息
                      for msg in reversed(messages): # type: ignore
                          if hasattr(msg, 'content'): # type: ignore
                              msg_type = str(type(msg)).lower() # type: ignore
                              if 'ai' in msg_type or 'assistant' in msg_type:
                                  execution_result = msg.content # type: ignore 
                                  break
                      else:
                          # 如果没有找到AI消息，使用最后一个消息
                          last_message = messages[-1] # type: ignore
                          if hasattr(last_message, 'content'): # type: ignore
                              execution_result = last_message.content # type: ignore  
                          else:
                              execution_result = str(last_message) # type: ignore
              elif "output" in result:
                  execution_result = str(result["output"]) # type: ignore
              else:
                  execution_result = str(result) # type: ignore
          elif result and hasattr(result, 'content'):
              # 如果result直接是消息对象（直接LLM调用）
              execution_result = result.content
          elif result:
              # 其他情况，转换为字符串
              execution_result = str(result)
          
          # 如果结果太短或包含错误信息，提供更详细的信息
          if len(execution_result) < 10 or "sorry" in execution_result.lower(): # type: ignore
              execution_result = f"任务描述: {node_description}\n执行状态: 已完成\n结果: {execution_result}"
              
      except Exception as e:
          self.logger.error(f"提取执行结果时出错: {str(e)}") # type: ignore
          execution_result = f"执行完成，但结果提取时出现错误: {str(e)}"
      
      return execution_result   # type: ignore
  

  def _do_execute(self, step: Dict[str, Any], current_step: int) -> Dict[str, Any]:
    """ do execute step
    Args:
        step (Dict[str, Any]): step info
        current_step (int): current step index      
    Returns:  
        Dict[str, Any]: execution result
    """
    logger.info(f"Executing step {current_step + 1}: {step}")
    
    start_time = time.time()

    all_tools = self.local_tools + self.mcp_tools
    agent = create_react_agent( # type: ignore
      model=self.simple_llm,
      tools=all_tools
    ) 

    all_tools_formatted = self._format_tools_list(all_tools)

    react_prompt_filled = react_prompt.format(
      description=step.get("description", ""),
      user_feedback="",
      expected_result=step.get("expected_result", ""),
      tools="\n".join(all_tools_formatted),
    )
    logger.debug(f"React prompt for step {current_step + 1}:\n{react_prompt_filled}")

    messages = {"messages": [{"role": "user", "content": react_prompt_filled}]}
    if hasattr(agent, 'ainvoke'): # type: ignore
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        result = new_loop.run_until_complete(agent.ainvoke(messages)) # type: ignore
    else:
        result = agent.invoke(messages) # type: ignore
    result = self._extract_execution_result(result) # type: ignore
    timing_info = self.statistic_timing(start_time, f"execute_step_{current_step + 1}")
    logger.debug(f"Step {current_step + 1} execution result: {result}")
        
    return {
        "step": current_step + 1,
        "execution_result": result,
        "status": "completed",
        "timing": timing_info
    }


  # Call to execute the graph
  async def chat_with_planning_stream(self, thread_id: str, user_task: str = "") -> AsyncIterator[Any]:
    """ chat with planning"""
    init_data = PlanExecutorState(
      user_id=thread_id,
      session_id=thread_id,
      request_id=thread_id,
      messages=[HumanMessage(content=user_task)],  # type: ignore
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
        # logger.debug(f"Graph event: {event}")
        if event["event"] == "on_chain_stream":
            chunk = event.get("data", {}).get("chunk", {})
            if isinstance(chunk, dict) and "streaming_chunks" in chunk:
                for streaming_chunk in chunk["streaming_chunks"]: # type: ignore
                    yield { 
                        "step": streaming_chunk.get("step"), # type: ignore
                        "message": streaming_chunk.get("message"), # type: ignore
                        "data": streaming_chunk.get("data"), # type: ignore   
                        "node": event.get("name", "unknown")
                    }
            if isinstance(chunk, dict) and "__interrupt__" in chunk:
                chunk_interrupt = chunk["__interrupt__"][0] # type: ignore
                yield {
                    "step": "interrupt",
                    "message": "需要用户确认",
                    "data": chunk_interrupt.value, # type: ignore
                    "node": "check_node_uncertainty"
                }
                return
        elif event["event"] == "on_chain_start":
            # Agent start run
            yield {
                "step": "agent_start",
                "message": f"🚀 开始执行 {event.get('name', '智能体')}",
                "data": {
                    "agent": event.get("name", "unknown")
                },
                "node": event.get("name", "unknown")
            }
        elif event["event"] == "on_chain_end":
            # Agent run end
            yield {
                "step": "agent_complete",
                "message": f"✅ {event.get('name', '智能体')} 执行完成",
                "data": {
                    "agent": event.get("name", "unknown")
                },
                "node": event.get("name", "unknown")
            }
        elif event["event"] == "on_tool_start":
            # Tool start run
            yield {
                "step": "tool_start",
                "message": f"🔧 使用工具: {event.get('name', 'unknown')}",
                "data": {
                    "tool": event.get("name", "unknown")
                },
                "node": "tool_execution"
            }
        elif event["event"] == "on_tool_end":
            # Tool run end
            yield {
                "step": "tool_complete",
                "message": f"✅ 工具 {event.get('name', 'unknown')} 执行完成",
                "data": {
                    "tool": event.get("name", "unknown")
                },
                "node": "tool_execution"
            }