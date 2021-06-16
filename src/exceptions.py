class ComplianceAlertingException(Exception):
    pass


class ClientFactoryException(ComplianceAlertingException):
    pass


class FilterConfigException(ComplianceAlertingException):
    pass


class MissingConfigException(ComplianceAlertingException):
    pass


class NotificationMappingException(ComplianceAlertingException):
    pass
