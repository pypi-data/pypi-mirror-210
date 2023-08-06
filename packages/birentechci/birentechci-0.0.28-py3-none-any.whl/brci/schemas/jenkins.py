from datetime import datetime

from pydantic import BaseModel


class BuildResult(BaseModel):
    jobName: str
    jobBaseName: str
    buildID: str
    buildNum: str
    buildURL: str
    jenkinsURL: str
    extraInfo: dict = None
    status: str = None
    duration: str = None
    result: dict = None
    baseResult: dict = None


class QueryBuildResult(BaseModel):
    page: int = 1
    size: int = 10
    buildID: str = None
    buildNum: str = None
    buildURL: str = None
    status: str = None
    jobName: str = None
