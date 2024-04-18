resource "aws_ssm_parameter" "platsec_alerts_slack_v2_api_key" {
 
  name        = "SLACK_V2_API_KEY"
  description = "API key for Slack v2 notifications"
  type        = "SecureString"
  value       = "InitialValueUpdatedViaAWSConsole"

  lifecycle {
    ignore_changes = [value]
  }
    tags = {
    environment = var.environment
  }
}