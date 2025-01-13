workspace {

    model {
        snsEventGroup = group "SNS Event group" {
            codebuild = softwareSystem "Codebuild"
            codepipeline = softwareSystem "Codepipeline"
            guardduty = softwareSystem "Guard Duty"
            grantUserAccess = softwareSystem "grant-user-access-lambda"
            awsHealth = softwareSystem "AWS Health"
        }
        
        auditReportS3Bucket = softwareSystem "Audit Report S3 bucket" 
        
        user = person "User"
        complianceAlerting = softwareSystem "compliance-alerting" {
            sns = container "platsec-compliance-alerting-topic" {
                codebuild -> this "sends event"
                codepipeline -> this "sends event"
                guardduty -> this "sends event"
                grantUserAccess -> this "sends event"
                awsHealth -> this "sends event"
            }
            lambda = container "platsec-compliance-alerting-lambda" {
                sns -> this "sends sns event"
                auditReportS3Bucket -> this "sends s3 event notification"
            }
            container "mappings config S3 Bucket" {
                lambda -> this "Reads from"
            }
        }
        slack = softwareSystem "Slack" {
            lambda -> this "Sends notification to"
        }
        pagerDuty = softwareSystem "PagerDuty" {
            lambda -> this "Sends notification to"
        }
    }

    views {
        systemContext complianceAlerting {
            include *
            autolayout lr
        }

        container complianceAlerting {
            include *
            autolayout lr
        }

        theme default
    }

}