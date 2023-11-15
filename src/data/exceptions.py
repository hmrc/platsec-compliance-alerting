class ComplianceAlertingException(Exception):
    pass


class AwsClientException(ComplianceAlertingException):
    pass


class ClientFactoryException(ComplianceAlertingException):
    pass


class FilterConfigException(ComplianceAlertingException):
    pass


class MissingConfigException(ComplianceAlertingException):
    pass


class InvalidConfigException(ComplianceAlertingException):
    pass


class NotificationMappingException(ComplianceAlertingException):
    pass


class UnsupportedAuditException(ComplianceAlertingException):
    pass


class UnsupportedEventException(ComplianceAlertingException):
    pass


class SlackNotifierException(Exception):
    pass


class PagerDutyNotifierException(Exception):
    pass
