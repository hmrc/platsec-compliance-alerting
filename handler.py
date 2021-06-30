from logging import ERROR, basicConfig, getLogger

from src import compliance_alerter
from src.config.config import Config

basicConfig(
    level=Config.get_log_level(), datefmt="%Y-%m-%dT%H:%M:%S", format="%(asctime)s %(levelname)s %(module)s %(message)s"
)
getLogger("botocore").setLevel(ERROR)
getLogger("requests").setLevel(ERROR)
getLogger("urllib3").setLevel(ERROR)


def handler(event, context):
    compliance_alerter.main(event)
