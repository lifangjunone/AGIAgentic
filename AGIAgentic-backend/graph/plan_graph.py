
import time
import asyncio
import traceback

from datetime import datetime

from langgraph.graph import StateGraph # type: ignore
from typing import Any, AsyncIterator, Dict, List
from langgraph.prebuilt import create_react_agent # type: ignore
from langgraph.graph.state import CompiledStateGraph # type: ignore
from langchain_core.messages import HumanMessage, AIMessage


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
  
  def _add_streaming_chunk(self, state: PlanExecutorState, step: str, message: str, data: Dict[str, Any] = {}) -> None: # type: ignore
    """ add streaming chunk
    Args:
        state (PlanExecutorState): current state
        step (str): step name
        message (str): message
        data (Dict[str, Any], optional): additional data. Defaults to {}.
    """

    if "streaming_chunks" not in state:
        state["streaming_chunks"] = []

    state["streaming_chunks"] = [{
        "step": step,
        "message": message,
        "data": data or {}
    }]

    

  def _analyze_and_plan(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Analyze the task and generate plan"""

    logger.info("Starting Analyzing task and generating execution plan...")
    start_time = time.time()
    try:
      # Generate execution plan
      messages = [HumanMessage(content=planning_prompt.format(user_task=state.get("user_task", "")))]  # type: ignore
      plan = self.reason_llm.invoke(messages)
      json_plan = json_match(plan.content)  # type: ignore
      logger.debug(f"Generated execution plan: {json_plan}")

      # Validate the generated plan
      if not json_plan or "execution_plans" not in json_plan:
        state["status"] = "failed"
        state["error"] = "Failed to generate valid execution plan."
        return state

      # Update state with analysis and plan
      state["task_analysis"] = json_plan.get("task_analysis", "")
      state["execution_plans"] = json_plan.get("execution_plans", [])
      state["current_step"] = 0
      state["timing_info"] = self.statistic_timing(start_time, "analyze_and_plan")

      # Add streaming chunk
      self._add_streaming_chunk(
        state=state,
        step="analyze_and_plan",
        message="✅ 任务分析和执行计划生成完成。",
        data={
            "task_analysis": state["task_analysis"],
            "execution_plans": state["execution_plans"]
        }
      )
    except Exception as e:
      logger.error(f"Error in _analyze_and_plan: {e}")
      state["status"] = "failed"
      state["error"] = str(e)
    return state
  
  def _check_and_execute_node(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ Check and execute task"""

    # Get current step and execution plans
    current_step = state.get("current_step")
    execution_plans = state.get("execution_plans", [])

    logger.info(f"current_step: {current_step}, total_steps: {len(execution_plans)}")

    # If all steps are completed 
    if current_step >= len(execution_plans):
      state["status"] = "completed"
      return state
    
    # Get the current node to execute
    current_node = execution_plans[current_step]
    logger.debug(f"Executing step {current_step + 1}: {current_node}")

    # Execute the current step
    execution_result = self._do_execute(current_node, current_step)

    state["step_results"].append(execution_result)
    # Modify state for next step
    state["current_step"] += 1

    return self._process_execution_result(state, execution_result, current_step)
  

  def _process_execution_result(self, state: PlanExecutorState, execution_result: Dict[str, Any], current_step: int) -> PlanExecutorState:
    """ process execution result
    Args:
        state (PlanExecutorState): current state
        execution_result (Dict[str, Any]): execution result
        current_step (int): current step index
    Returns:
        PlanExecutorState: updated state
    """

    # Add streaming chunk for execution result
    # Failed execution
    if execution_result.get("status") == "failed":
      self._add_streaming_chunk(
        state=state,
        step=f"step_{current_step + 1}",
        message=f"❌ 步骤 {current_step + 1} 执行失败，错误信息: {execution_result.get('execution_result')}",
        data={
            "execution_result": execution_result
        }
      )
      state["status"] = "failed"
      return state
    
    # Successful execution
    self._add_streaming_chunk(
      state=state,
      step=f"step_{current_step + 1}",
      message=f"✅ 步骤 {current_step + 1} 执行完成。",
      data={
          "execution_result": execution_result
      }
    )
    return state
    

  def _summary_response(self, state: PlanExecutorState) -> PlanExecutorState: # type: ignore
    """ summary result"""

    start_time = time.time()
    task_analysis = state.get("task_analysis")
    execution_plan = state.get("execution_plan")
    step_results = state.get("step_results")

    # assemble execution plan text
    plan_text = ""
    if execution_plan:
        for i, step in enumerate(execution_plan, 1):
            plan_text += f"步骤{i}: {step.get('description')}\n"

    # assemble step results text
    results_text = ""
    if step_results:
        for i, result in enumerate(step_results, 1):
            results_text += f"步骤{i}:{result.get('execution_result')}\n"


    # Generate summary response
    messages = [HumanMessage(content=summary_response_prompt.format(
      user_task=state.get("user_task", ""),
      task_analysis=task_analysis,
      execution_plan=plan_text,
      step_results=results_text
    ))]  # type: ignore

    try:
      logger.info("Start generating summary response...")
      summary = self.reason_llm.invoke(messages)
    except Exception as e:
      logger.error(f"Error in _summary_response: {e}")
      state["status"] = "failed"
      state["error"] = str(e)
      return state
    
    # Update state with summary response
    state["timing_info"].update(self.statistic_timing(start_time, "response_generation"))
    state["status"] = "completed"

    # Calculate total duration
    total_duration = (
        state["timing_info"].get("analyze_and_plan_duration", 0) +
        state["timing_info"].get("response_generation_duration", 0)
    )

    # Add final streaming chunk with summary
    state["streaming_chunks"].append({
        "step": "completed",
        "message": f"🎉 任务完成！总耗时: {total_duration:.2f}秒", # type: ignore
        "data": {
            "response": summary.content, # type: ignore
            "step": "summary_response",
            "message": f"🎉 任务完成！总耗时: {total_duration:.2f}秒",
            "timing_info": state["timing_info"],
            "total_nodes": len(state.get("execution_plan", [])),
            "completed_nodes": len(state.get("step_results", [])),
            "step_results": state.get("step_results", []),
            "execution_plan": state.get("execution_plan", [])
        }
    })
    logger.info(f"End generating summary response...")
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

  def _extract_execution_result(self, result: Any, node_description: str = "") -> str:
      """提取执行结果 - 公共方法"""
      execution_result = "No result returned."
      if not result: return execution_result
      try:
        # if result is str will try to convert json object
        if isinstance(result, str):
            try:
              _result = json_match(result)  # type: ignore
              if _result:
                  result = _result
            except Exception:
              pass
        
        # process different result formats
        if isinstance(result, dict) and result.get("messages"): # type: ignore
            messages = result.get("messages", []) # type: ignore
            if messages and isinstance(messages, list):
              # get the last assistant message content
              for message in reversed(messages): # type: ignore
                  if isinstance(message, AIMessage):
                    if hasattr(message, "content") and message.content: # type: ignore
                        execution_result = message.content # type: ignore
                        break
                    else:
                        last_message = messages[-1] # type: ignore
                        if hasattr(last_message, 'content'): # type: ignore
                            execution_result = last_message.content # type: ignore
                        else:
                            execution_result = str(last_message) # type: ignore
        elif isinstance(result, dict) and result.get("output"): # type: ignore
            execution_result = result.get("output") # type: ignore
        else:
          execution_result = str(result) # type: ignore
      except Exception as e:
        logger.error(f"Error extracting execution result for node '{node_description}': {e}")
        traceback.print_exc()
        execution_result = str(result) # type: ignore
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

    try:
      # Combine all tools
      all_tools = self.local_tools + self.mcp_tools

      # Create React agent
      agent = create_react_agent( # type: ignore
        model=self.simple_llm,
        tools=all_tools
      ) 

      all_tools_formatted = self._format_tools_list(all_tools)

      # Prepare React prompt
      react_prompt_filled = react_prompt.format(
        description=step.get("description", ""),
        user_feedback="",
        expected_result=step.get("expected_result", ""),
        tools="\n".join(all_tools_formatted),
      )
      logger.debug(f"React prompt for step {current_step + 1}")

      # Execute with agent
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
    except Exception as e:
      logger.error(f"Error executing step {current_step + 1}: {e}")
      timing_info = self.statistic_timing(start_time, f"execute_step_{current_step + 1}")
      return {
          "step": current_step + 1,
          "execution_result": str(e),
          "status": "failed",
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
        # Event types to handle:
          # 'on_chain_start'
          # 'on_tool_end' 
          # 'on_chat_model_start'
          # 'on_chat_model_end'
          # 'on_chain_end'
          # 'on_tool_start'
          # 'on_chat_model_stream'
          # 'on_chain_stream'

        ## on_chat_model event is not necessary to handle, as the Autonomy plan focuses on tool and chain execution.
        ## Model-related events are intermediate processing steps.

        if event["event"] == "on_chain_stream":
            chunk = event.get("data", {}).get("chunk", {})
            if isinstance(chunk, dict) and "streaming_chunks" in chunk:
                for streaming_chunk in chunk["streaming_chunks"]: # type: ignore
                    yield {
                        "data": { 
                          "step": streaming_chunk.get("step"), # type: ignore
                          "message": streaming_chunk.get("message"), # type: ignore
                          "data": streaming_chunk.get("data"), # type: ignore   
                          "node": event.get("name", "unknown")
                      },
                      "event": "on_chain_stream"
                    }
                    
            if isinstance(chunk, dict) and "__interrupt__" in chunk:
                chunk_interrupt = chunk["__interrupt__"][0] # type: ignore
                yield {
                    "data": {
                      "step": "interrupt",
                      "message": "需要用户确认",
                      "data": chunk_interrupt.value, # type: ignore
                      "node": "check_node_uncertainty"
                  },
                  "event": "on_chain_stream"
                }
                return
        elif event["event"] == "on_chain_start":
            # Agent start run
            yield {
                "data": {
                  "step": "agent_start",
                  "message": f"🚀 开始执行 {event.get('name', '智能体')}",
                  "data": {
                      "agent": event.get("name", "unknown")
                  },
                  "node": event.get("name", "unknown")
                },
                "event": "on_chain_start"
            }
        elif event["event"] == "on_chain_end":
            # Agent run end
            yield {
                "data":{
                  "step": "agent_complete",
                  "message": f"✅ {event.get('name', '智能体')} 执行完成",
                  "data": {
                      "agent": event.get("name", "unknown")
                  },
                  "node": event.get("name", "unknown")
                },
                "event": "on_chain_end"
              }
        elif event["event"] == "on_tool_start":
            # Tool start run
            yield {
                "data":{
                  "step": "tool_start",
                  "message": f"🔧 使用工具: {event.get('name', 'unknown')}",
                  "data": {
                      "tool": event.get("name", "unknown")
                  },
                  "node": "tool_execution"
                },
                "event": "on_tool_start"
              }
        elif event["event"] == "on_tool_end":
            # Tool run end
            yield {
                "data": {
                  "step": "tool_complete",
                  "message": f"✅ 工具 {event.get('name', 'unknown')} 执行完成",
                  "data": {
                      "tool": event.get("name", "unknown")
                  },
                  "node": "tool_execution"
                },
                "event": "on_tool_end"
              }

