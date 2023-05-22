import aws_cdk as cdk
from constructs import Construct
from .infrastructure import MentorMatchStack


class MentorMatchAppStage(cdk.Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._service = MentorMatchStack(self, "MentorMatchStack")

    @property
    def web_stack(self) -> MentorMatchStack:
        return self._service
