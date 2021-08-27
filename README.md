# platsec-compliance-alerting

PlatSec Compliance Alerting analyses audit reports produced by [PlatSec AWS Scanner][scanner] and raises alerts on
non-compliant resources. 

## Configuration

This Python program is meant to run as an AWS Lambda function that requires the following environment variables:

- `AWS_ACCOUNT`: identifier for the AWS account the lambda function is running in
- `CENTRAL_CHANNEL`: name of the Slack channel where all alerts are sent to
- `CONFIG_BUCKET`: name of the bucket that contains config files for alert mapping and alert filtering
- `CONFIG_BUCKET_READ_ROLE`: name of an IAM role that can read config files from the config bucket
- `LOG_LEVEL`: how much/little logs the lambda function should print (accepted values are official Python log levels)
- `REPORT_BUCKET_READ_ROLE`: name of an IAM role that can read audit reports
- `S3_AUDIT_REPORT_KEY`: name of audit reports that should trigger an S3 compliance check
- `GITHUB_AUDIT_REPORT_KEY`: name of audit reports that should trigger an Github compliance check 
- `SLACK_API_URL`: PlatApps Slack API URL
- `SLACK_USERNAME_KEY`: name of the SSM parameter that contains PlatApps Slack API username
- `SLACK_TOKEN_KEY`: name of the SSM parameter that contains PlatApps Slack API token
- `SSM_READ_ROLE`: name of an IAM role that can read SSM parameters

### Alert mapping

Alerts are always sent to a central Slack channel. Additional Slack channels can be specified:

```json
[
  {
    "channel": "team-abc",
    "account": "111222333444"
  },
  {
    "channel": "team-xyz",
    "items": ["bucket-a", "bucket-b"]
  }
]
```

- `channel`: name of a Slack channel where alerts will be sent to (should not begin with `#`)
- `account`: alerts for resources in this account will be sent to the specified channel
- `items`: alerts for these resources will be sent to the specified channel

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

- `item`: alerts for this item won't be sent
- `reason`: explains why this item should not be alerted on, ideally links to a document illustrating the decision

Alert filtering config files should be saved in the config bucket and prefixed with `filters/`.

## Licence

This code is open source software licensed under the [Apache 2.0 Licence][licence].

[scanner]: https://github.com/hmrc/platsec-aws-scanner
[licence]: http://www.apache.org/licenses/LICENSE-2.0.html
