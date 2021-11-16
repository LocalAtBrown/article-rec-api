# article-rec-api

Serves recommended articles for news sites. 

# API Usage

## Error Codes
- 200: OK
- 400: VALIDATION ERROR
- 500: INTERNAL SERVER ERROR

## Endpoints 

### `GET /recs`

#### PARAMS
**site** (required)

The site to pull recommendations for.

**source_entity_id** (required) 

The article for which you want recommendations, specified by the id from your news site's data store.

**model_type** (optional)

The type of model for which you want recommendations. This should always be `article` in production contexts.

If a model_id is provided, it overrides this input.

**model_id** (optional)

The specific model for which you want recommendations. This is useful in testing environments.

If a model_id is provided, it overrides the model_type.

**exclude** (optional)

A comma-separated list of article id's from your news site's data store to exclude from the results.

**sort_by** (optional)

The field to sort results by. This can be any top-level attribute of a recommendation.

**order_by** (optional)

Either asc for ascending or desc for descending. This value defaults to desc.

### `GET /models`

#### PARAMS
**status** (optional)
The status of the model. This can be `current`, `pending`, `stale`, or `failed`.

**type** (optional)
The type of the model. This can be `article` or `popularity`.

# Development 
## Directory Layout
```
.
├── cdk       # infrastructure as code for this service
├── db        # object-relational mappings to interact with the database
├── handlers  # logic to handle api requests
├── lib       # helpers to interact with lnl's aws resources
└── tests     # unit tests
```

## Local Usage
1. Build the container
```
kar build
```

2. Run the api
```
kar run
```

## Running Tests
1. Build the container
```
kar build
```

2. Run unit tests
```
kar test
```

## Deploying
For dev deployment, run:

```
kar cdk deploy DevArticleRecAPI
```

Each pull request to main will trigger a new prod deployment when merged.

## Monitoring

### Logs
- [Dev](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/DevArticleRecAPI-DevArticleRecAPIServiceTaskDefwebLogGroupF7CBBE61-aj8kV8MTSYXW/log-events$3Fstart$3D-3600000)
- [Prod](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/ArticleRecAPI-ArticleRecAPIServiceTaskDefwebLogGroup4ADC2B59-QUdq30I9QQvt/log-events$3Fstart$3D-3600000)

### Dashboards
- [Dev](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=dev-article-rec-api;start=PT24H)
- [Prod](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=article-rec-api;start=PT24H)

## Other Resources

### Misc Documentation
* [Monitoring Guide](https://www.notion.so/article-rec-backend-monitoring-30915f77759c4350b1b8588582c9ea04)

### Related Repositories
* [`infrastructure`](https://github.com/LocalAtBrown/infrastructure): The database and ECS clusters are created here.
* [`article-rec-db`](https://github.com/LocalAtBrown/article-rec-db): The relevant database migrations are defined and applied here.
* [`article-rec-training-job`](https://github.com/LocalAtBrown/article-rec-training-job): The job that runs on a regular interval, training the recommendation model and saving the predictions that are served by this API to the database.
* [`snowplow-analytics`](https://github.com/LocalAtBrown/snowplow-analytics): The analytics pipeline used to collect user clickstream data into s3 is defined in this repository.
* [`article-recommendations`](https://github.com/LocalAtBrown/article-recommendations): The PHP widget that makes requests to this API, displaying recommendations WordPress [NewsPack](https://newspack.pub/) sites.

### Architecture Diagram
![architecture diagram](docs/images/arch-diagram.png)
