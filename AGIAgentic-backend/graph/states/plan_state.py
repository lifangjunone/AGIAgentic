

from typing import Any, Dict, List


from graph.states.base_state import BaseState


class PlanExecutorState(BaseState):
    """ A graph structure to represent the execution plan of tasks. """

    # Task states
    # user task
    user_task: str 
    # task analysis
    task_analysis: str
    # execution plan
    execution_plans: List[Dict[str, Any]]
    # current step
    current_step: int
    # step result
    step_results: List[Dict[str, Any]]