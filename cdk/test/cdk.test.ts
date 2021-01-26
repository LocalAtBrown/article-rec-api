import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { AppStack} from '../lib/app-stack';
import { STAGE } from "../lib/helpers";

const env = { account: "348955818350", region: "us-east-1" };


test('ProdAppStack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new AppStack(app, 'MyTestStack', {env, stage: STAGE.PRODUCTION});
    // THEN
    expectCDK(stack).to(haveResource("AWS::ECS::TaskDefinition"));
});

test('DevAppStack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new AppStack(app, 'MyTestStack', {env, stage: STAGE.DEVELOPMENT});
    // THEN
    expectCDK(stack).to(haveResource("AWS::ECS::TaskDefinition"));
});