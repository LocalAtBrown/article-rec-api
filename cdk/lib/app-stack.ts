import * as cdk from "@aws-cdk/core";
import * as ecs from "@aws-cdk/aws-ecs";
import * as ec2 from "@aws-cdk/aws-ec2";
import * as iam from "@aws-cdk/aws-iam";
import * as acm from "@aws-cdk/aws-certificatemanager";
import * as route53 from "@aws-cdk/aws-route53";
import * as helpers from "./helpers";
import { ApplicationLoadBalancedEc2Service } from "@aws-cdk/aws-ecs-patterns";

// TODO this needs to be propagated to the tags
export interface AppStackProps extends cdk.StackProps {
  stage: helpers.STAGE;
}

export class AppStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props: AppStackProps) {
    super(scope, id, props);

    const taskRole = new iam.Role(this, `${id}Role`, {
      assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
      inlinePolicies: {
        SecretsManagerAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              sid: `SecretsManagerAccess`,
              actions: ["secretsmanager:Get*"],
              resources: ["*"],
            }),
          ],
        }),
        SSMAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              sid: `SSMAccess`,
              actions: ["ssm:*"],
              resources: ["*"],
            }),
          ],
        }),
        CloudwatchPutAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              sid: `CloudwatchPutAccess`,
              actions: ["cloudwatch:Put*"],
              resources: ["*"],
            }),
          ],
        }),
      },
    });

    // const bucketName = helpers.makeBucketName("change-this-bucket-name", props.stage);
    // const bucket = helpers.makeBucket(this, bucketName, taskRole, props.stage);

    const { cluster } = helpers.getECSCluster(this, props.stage);

    const image = ecs.ContainerImage.fromAsset("../", {
      extraHash: Date.now().toString(),
    });

    const domainZone = route53.HostedZone.fromLookup(this, `${id}HostedZone`, {
      domainName: 'localnewslab.io'
    });

    let domainName = "article-rec-api";
    if (props.stage == helpers.STAGE.DEVELOPMENT) {
      domainName = 'dev-' + domainName;
    }

    const certificate = acm.Certificate.fromCertificateArn(this, `${id}Certificate`, cdk.Fn.importValue("LocalNewsLab-certificate-arn"));

    new ApplicationLoadBalancedEc2Service(this, `${id}Service`, {
      cluster,
      cpu: 128,
      memoryLimitMiB: 128,
      desiredCount: 1,
      domainName,
      domainZone,
      certificate,
      taskImageOptions: {
        image,
        containerPort: 5000,
        taskRole,
        environment: {
          STAGE: props.stage,
        }
      }
    })

  }
}
