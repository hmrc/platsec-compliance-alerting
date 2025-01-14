# platsec-compliance-alerting

PlatSec Compliance Alerting analyses audit reports produced by [PlatSec AWS Scanner][scanner] and raises alerts on
non-compliant resources.

## Configuration

This Python program is meant to run as an AWS Lambda function that requires the following environment variables:

* `AWS_ACCOUNT`: identifier for the AWS account the lambda function is running in
* `CONFIG_BUCKET`: name of the bucket that contains config files for alert mapping and alert filtering
* `CONFIG_BUCKET_READ_ROLE`: name of an IAM role that can read config files from the config bucket
* `LOG_LEVEL`: how much/little logs the lambda function should print (accepted values are official Python log levels)
* `REPORT_BUCKET_READ_ROLE`: name of an IAM role that can read audit reports
* `S3_AUDIT_REPORT_KEY`: name of audit reports that should trigger an S3 compliance check
* `GITHUB_AUDIT_REPORT_KEY`: name of audit reports that should trigger a Github compliance check
* `GITHUB_WEBHOOK_REPORT_KEY`: name of webhook reports that should trigger a Github webhook compliance check
* `SLACK_API_URL`: PlatApps Slack API URL
* `SLACK_V2_API_KEY`: name of the SSM parameter that contains PlatApps Slack v2 endpoint API key
* `SSM_READ_ROLE`: name of an IAM role that can read SSM parameters
* `VPC_AUDIT_REPORT_KEY`: name of audit reports that should trigger a VPC compliance check

### Alert mapping

```json
[
  {
    "channel": "all-notifications-channel"
  },
  {
    "channel": "team-abc",
    "accounts": ["111222333444"]
  },
  {
    "channel": "team-xyz",
    "items": ["bucket-a", "bucket-b"]
  },
  {
    "channel": "aws-violations-channel",
    "compliance_item_types": ["s3_bucket", "iam_access_key"]
  },
  {
    "channel": "object-infrastructure-team",
    "accounts": ["222222222222", "333333333333", "444444444444"],
    "compliance_item_types": ["s3_bucket"]
  },
  {
    "channel": "object-infrastructure-team",
    "accounts": ["444444444444"],
    "compliance_item_types": ["iam_access_key"]
  }
]
```

* `channel`: name of a Slack channel where alerts will be sent to (should not begin with `#`)
* `accounts`: alerts for resources in these accounts will be sent to the specified channel
* `items`: alerts for these resources will be sent to the specified channel
* `compliance_item_types`: alerts for these resource types will be sent to the specified channel

`accounts`, `items` and `compliance_item_types` are all optional, but if specified they must all match for that
channel to receive a notification. The same channel can appear in multiple mappings

Alert mapping config files should be saved in the config bucket and prefixed with `mappings/`.

### Alert filtering

Alerts can be filtered out for resources that are known to be non-compliant, as long as the non-compliance state has
been signed-off and documented:

```json
[
  {
    "item": "bucket-a",
    "reason": "needs public access"
  },
  {
    "item": "bucket-b",
    "reason": "some reason"
  }
]
```

* `item`: alerts for this item won't be sent
* `reason`: explains why this item should not be alerted on, ideally links to a document illustrating the decision

Alert filtering config files should be saved in the config bucket and prefixed with `filters/`.

## CI/CD pipeline

### Where can I find a CI/CD pipeline for this code base?

* [PR build job](https://build.tax.service.gov.uk/job/platform-security/job/platsec-compliance-alerting-pr-builder)
* [Deployment pipeline](https://eu-west-2.console.aws.amazon.com/codesuite/codepipeline/pipelines/compliance-alerting/view?region=eu-west-2)

### How is the CI/CD pipeline configured?

* PR build job is configured on [Jenkins](https://build.tax.service.gov.uk/job/platform-security/job/platsec-compliance-alerting-pr-builder)
* Codepipeline pipeline config for deployment can be found in [platsec-ci-terraform repo](https://github.com/hmrc/platsec-ci-terraform/blob/main/pipelines.tf#L21).

## Licence

This code is open source software licensed under the [Apache 2.0 Licence][licence].

[scanner]: https://github.com/hmrc/platsec-aws-scanner

[licence]: http://www.apache.org/licenses/LICENSE-2.0.html
