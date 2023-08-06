from pydantic import BaseModel
from typing import Optional

class AddServerReportServerResponse(BaseModel):
    mods: Optional[list[str]] = []
    version: Optional[str] = None

class AddServerReportResponse(BaseModel):
    times: Optional[AddServerReportServerResponse]

class AddServerResponse(BaseModel):
    title: Optional[str] = ''
    description: Optional[str] = ''
    content: Optional[str] = None
    new: Optional[int] = 0
    report: Optional[AddServerReportResponse]
    id: Optional[int]
    status: Optional[str]