class ComplianceAlertingException(Exception):
    pass


class FilterConfigException(ComplianceAlertingException):
    pass


class NotificationMappingException(ComplianceAlertingException):
    pass


class MissingConfigException(ComplianceAlertingException):
    pass
