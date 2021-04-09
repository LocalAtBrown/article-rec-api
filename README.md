## article-rec-api

Surfaces article recommendations populated by the [training job](https://github.com/LocalAtBrown/article-rec-training-job).

## API Docs

See [Postman](https://localnewslab.postman.co/workspace/LNL-Workspace~821d679c-4107-43a1-8788-a6685133dbe6/documentation/14469235-73d14eed-bdb9-4d8d-93fb-2b82086142f8).

## Dev Usage
1. Build the container
```
kar build
```

2. Run the api
```
kar run
```

## Monitoring

### Logs
- [Dev](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/DevArticleRecAPI-DevArticleRecAPIServiceTaskDefwebLogGroupF7CBBE61-aj8kV8MTSYXW/log-events$3Fstart$3D-3600000)
- [Prod](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/ArticleRecAPI-ArticleRecAPIServiceTaskDefwebLogGroup4ADC2B59-QUdq30I9QQvt/log-events$3Fstart$3D-3600000)

### Dashboards
- [Dev](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=dev-article-rec-api)
- [Prod](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=article-rec-api)
