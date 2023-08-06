from datetime import datetime

from pydantic import BaseModel


class PullRequest(BaseModel):
    pullRequestName: str
    component: str = None
    pullRequestNumber: str
    pullLink: str
    sourceBranch: str = None
    targetBranch: str = None
    commit: str = None
    status: str = None
    prCreatedTime: datetime = None
    prCreatedBy: str = None
    prUpdatedTime: datetime = None
    prUpdatedBy: str = None
    prEndedTime: datetime = None
    prEndedBy: str = None
    updatedTime: datetime = None


class UpdatePullRequest(PullRequest):
    status: str
    pullLink: str
    updatedTime: datetime = None
