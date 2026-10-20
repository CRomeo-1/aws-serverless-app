# URL Shortener (AWS Serverless)

A simple URL shortener I built to practice serverless on AWS. Everything is deployed with Terraform.

## Architecture

```
Client -> API Gateway -> Lambda (Python) -> DynamoDB
```

- **API Gateway (HTTP API)**: public endpoint and routing
- **Lambda**: handles the requests
- **DynamoDB**: stores the links and number of clicks
- **IAM**: Lambda only has access to the table it needs

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | /links | create a short link, body: `{"url": "https://..."}` |
| GET | /{code} | redirect to the original url |
| GET | /stats/{code} | show the url and click count |

## How to deploy

You need an AWS account, AWS CLI and Terraform.

```bash
cd terraform
terraform init
terraform apply
```

Test it:
```bash
curl -X POST <api_url>/links -d '{"url":"https://google.com"}'
```

To delete everything: `terraform destroy`

## Run the test

```bash
pip install boto3 moto pytest
pytest
```

## What I learned
- How API Gateway passes requests to Lambda
- Designing a DynamoDB table around a partition key
- Writing IAM policies with only the needed permissions
- Managing infrastructure with Terraform instead of the console

## Next
- link expiration with DynamoDB TTL
- simple frontend on S3
