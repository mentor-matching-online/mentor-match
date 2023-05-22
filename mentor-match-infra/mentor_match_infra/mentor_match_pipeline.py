import jsii
from aws_cdk import Stack, Environment
from aws_cdk.aws_codepipeline import IStage
from aws_cdk.pipelines import CodePipeline, ShellStep, CodePipelineSource, ManualApprovalStep, \
    ICodePipelineActionFactory, Step, CodePipelineActionFactoryResult, StackOutputsMap
from constructs import Construct
from aws_cdk.aws_codepipeline_actions import CloudFormationDeleteStackAction
from .mentor_match_stage import MentorMatchAppStage


@jsii.implements(ICodePipelineActionFactory)
class DeleteStack(Step):

    def __init__(self, stack: Stack):
        super().__init__("DeleteStack")
        self._discover_referenced_outputs({
            "env": {}
        })
        self._stack = stack

    def produce_action(self, stage: IStage, *, scope, action_name, run_order, variables_namespace=None, artifacts, fallbackArtifact=None, pipeline: CodePipeline, codeBuildDefaults=None, beforeSelfMutation=None, stack_outputs_map: StackOutputsMap):
        stage.add_action(
            CloudFormationDeleteStackAction(
                admin_permissions=True,
                action_name=action_name,
                stack_name=f'MentorMatch/{self._stack.stack_name.replace("-", "/")}',
                run_order=run_order,
                variables_namespace=variables_namespace
            )
        )
        return CodePipelineActionFactoryResult(run_orders_consumed=1)


class MentorMatchPipeline(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        pipeline = CodePipeline(self, "MentorMatchPipeline",
                                pipeline_name="Pipeline",
                                synth=ShellStep("Synth",
                                                input=CodePipelineSource.git_hub("mentor-matching-online/mentor-match", "main"),
                                                commands=["npm install -g aws-cdk",
                                                          "cd mentor-match-infra",
                                                          "python -m pip install -r requirements.txt",
                                                          "cdk synth"],
                                                primary_output_directory="mentor-match-infra/cdk.out"
                                                )
                                )
        testing_stage = MentorMatchAppStage(self, "testing", env=Environment(account="712310211354", region="eu-west-2"))
        pipeline.add_stage(testing_stage, post=[DeleteStack(testing_stage.web_stack)])

        production_stage = pipeline.add_stage(
            MentorMatchAppStage(self, "production", env=Environment(account="712310211354", region="eu-west-2"))
        )
        production_stage.add_pre(
            ManualApprovalStep('approval')
        )
