

from pydantic import BaseModel
from typing import Optional


class PlanExecutorReqSchema(BaseModel):
  """ Schema for plan executor input and output. """

  user_task: str
  user_id: str
  session_id: Optional[str] = ""
  request_id: Optional[str] = ""

