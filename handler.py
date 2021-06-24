from logging import ERROR, getLogger

from src import compliance_alerter

getLogger("botocore").setLevel(ERROR)
getLogger("requests").setLevel(ERROR)
getLogger("urllib3").setLevel(ERROR)


def handler(event, context):
    compliance_alerter.main(event)
