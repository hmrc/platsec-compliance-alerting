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
- `SLACK_API_URL`: PlatApps Slack API URL
- `SLACK_USERNAME_KEY`: name of the SSM parameter that contains PlatApps Slack API username
- `SLACK_TOKEN_KEY`: name of the SSM parameter that contains PlatApps Slack API token
- `SSM_READ_ROLE`: name of an IAM role that can read SSM parameters

### Alert mapping

Alerts are always sent to a central Slack channel. On top of this, it's possible to map certain alerts with
additional Slack channels, so that teams can receive in their own Slack channels alerts that are relevant to their own
resources.

Instructing PlatSec Compliance Alerting to sent certain alerts to additional Slack channels can be done with a JSON
config file as such:

```json
[
  {
    "channel": "Slack channel where alerts should be sent to",
    "account": "AWS account identifier: alerts for any resource that belongs to this account will be sent in the above channel"
  },
  {
    "channel": "Slack channel where alerts should be sent to",
    "items": ["name of a resource for which alerts should go in the above Slack channel", "another resource", "..."]
  }
]
```

One or more alert mapping config files can be saved in the config bucket. These files are expected to have names
prefixed with `mappings/`.

### Alert filtering

Alerts can be filtered out for resources that are known to be non-compliant, as long as the non-compliance state has
been signed-off and documented.

Instructing PlatSec Compliance Alerting to ignore a resource can be done with a JSON config file as such:

```json
[
  {
    "item": "name of an item for which alerts should be ignored",
    "reason": "explains why this item should not be alerted on, possibly with a link to a document illustrating the decision"
  },
  {
    "item": "another item to be ignored",
    "reason": "why alerts for this item should be filtered out"
  }
]
```

One or more alert filtering config files can be saved in the config bucket. These files are expected to have names
prefixed with `filters/`.

## Licence

This code is open source software licensed under the [Apache 2.0 Licence][licence].

[scanner]: https://github.com/hmrc/platsec-aws-scanner
[licence]: http://www.apache.org/licenses/LICENSE-2.0.html
