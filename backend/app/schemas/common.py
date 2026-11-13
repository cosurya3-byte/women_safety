from pydantic import BaseModel, ConfigDict
from typing import Any
class APIResponse(BaseModel): success: bool=True; data: Any=None; message: str=""
class ORMModel(BaseModel): model_config=ConfigDict(from_attributes=True)
