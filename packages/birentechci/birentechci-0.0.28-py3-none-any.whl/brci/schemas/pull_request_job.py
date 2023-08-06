from . import jenkins


class PullRequestJob(jenkins.BuildResult):
    isDebug: bool = False
    component: str = None
    pullLink: str = None
