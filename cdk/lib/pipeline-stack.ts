import * as cdk from "@aws-cdk/core";
import * as codebuild from "@aws-cdk/aws-codebuild";
import * as codepipeline from "@aws-cdk/aws-codepipeline";
import * as codepipeline_actions from "@aws-cdk/aws-codepipeline-actions";
import { makeCDKDeployProject } from "./helpers";

// https://github.com/aws-samples/aws-cdk-examples/blob/master/python/codepipeline-docker-build/Base.py
// https://docs.aws.amazon.com/cdk/latest/guide/codepipeline_example.html
// https://medium.com/swlh/github-codepipeline-with-aws-cdk-and-typescript-d37183463302
// https://docs.aws.amazon.com/cdk/api/latest/docs/aws-codestarconnections-readme.html

export interface PipelineStackProps extends cdk.StackProps {
  readonly appStackName: string;
  // TODO: revisit simplifying this structure to optimize for the usual usecase..
  // i.e. just specifying repoName
  readonly repo: {
    name: string,
    owner?: string, // defaults to "LocalAtBrown"
    branch?: string, // defaults to "main"
  }
}

export class PipelineStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props: PipelineStackProps) {
    super(scope, id, props);

    const sourceOutput = new codepipeline.Artifact();

    new codepipeline.Pipeline(this, "Pipeline", {
      crossAccountKeys: false,
      stages: [
        {
          stageName: "Source",
          actions: [
            // BitBucketSourceAction works for Github too
            // This is required to work with the CodeStar Connection
            // https://github.com/aws/aws-cdk/issues/10632
            new codepipeline_actions.BitBucketSourceAction({
              actionName: "Source",
              output: sourceOutput,
              owner: props.repo.owner || "LocalAtBrown",
              repo: props.repo.name,
              branch: props.repo.branch || "main",
              connectionArn:
                // manually created github connection ARN so that we don't need to pass around
                // github auth tokens via SSM
                "arn:aws:codestar-connections:us-east-1:348955818350:connection/a72199b3-f3c8-4300-ad3b-95ecad3b32cf",
            }),
          ],
        },
        {
          stageName: "Deploy",
          actions: [
            new codepipeline_actions.CodeBuildAction({
              actionName: "CDKDeploy",
              project: makeCDKDeployProject(this, props.appStackName),
              input: sourceOutput,
            }),
          ],
        },
      ],
    });
  }
}
