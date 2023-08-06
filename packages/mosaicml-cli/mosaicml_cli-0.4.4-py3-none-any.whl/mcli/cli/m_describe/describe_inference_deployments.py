"""Implementation of mcli describe deployment"""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Tuple

from rich.table import Table

from mcli.api.exceptions import MAPIException
from mcli.api.inference_deployments.api_get_inference_deployments import get_inference_deployment
from mcli.cli.m_get.display import MCLIDisplayItem, MCLIGetDisplay, OutputDisplay, create_vertical_display_table
from mcli.sdk import InferenceDeployment
from mcli.utils.utils_logging import FAIL, FormatString, format_string

logger = logging.getLogger(__name__)


class DescribeDeployMetadataColumns(Enum):
    NAME = 'name'
    ADDRESS = 'address'
    IMAGE = 'image'
    DEPLOYMENT_ID = 'deployment_uid'
    CLUSTER = 'cluster'
    GPU_NUM = 'gpu_num'
    GPU_TYPE = 'gpu_type'
    REPLICAS = 'replicas'
    METADATA = 'metadata'


DEPLOYMENT_METADATA_DISPLAY_NAMES = [
    'Inference Deployment Name', 'Address', 'Image', 'Cluster', 'GPU Num', 'GPU Type', 'Replicas', 'Metadata'
]


@dataclass
class DescribeDeployMetadataDisplayItem(MCLIDisplayItem):
    """Tuple that extracts detailed inference deployment data for display purposes"""
    name: str
    address: str
    image: str
    replicas: str
    metadata: Dict[str, Any]
    cluster: str
    gpu_num: str
    gpu_type: Optional[str] = None

    @classmethod
    def from_deployment(cls, deploy: InferenceDeployment):
        extracted: Dict[str, Any] = {
            DescribeDeployMetadataColumns.NAME.value: deploy.config.name,
            DescribeDeployMetadataColumns.ADDRESS.value: deploy.public_dns,
            DescribeDeployMetadataColumns.IMAGE.value: deploy.config.image,
            DescribeDeployMetadataColumns.CLUSTER.value: deploy.config.cluster,
            DescribeDeployMetadataColumns.GPU_TYPE.value: deploy.config.gpu_type,
            DescribeDeployMetadataColumns.GPU_NUM.value: deploy.config.gpu_num,
            DescribeDeployMetadataColumns.REPLICAS.value: deploy.config.replicas,
            DescribeDeployMetadataColumns.METADATA.value: deploy.config.metadata
        }

        return DescribeDeployMetadataDisplayItem(**extracted)


# Displays
class MCLIDescribeDeploymentMetadataDisplay(MCLIGetDisplay):
    """ Vertical table view of inference deployment metadata """

    def __init__(self, models: List[InferenceDeployment]):
        self.models = sorted(models, key=lambda x: x.created_at, reverse=True)

    @property
    def index_label(self) -> str:
        return ""

    @property
    def override_column_ordering(self) -> Optional[List[str]]:
        return [
            col.value for col in DescribeDeployMetadataColumns if col != DescribeDeployMetadataColumns.DEPLOYMENT_ID
        ]

    def create_custom_table(self, columns: List[str], data: List[Tuple[Any, ...]], names: List[str]) -> Optional[Table]:
        return create_vertical_display_table(data=data, columns=DEPLOYMENT_METADATA_DISPLAY_NAMES)

    def __iter__(self) -> Generator[DescribeDeployMetadataDisplayItem, None, None]:
        for model in self.models:
            item = DescribeDeployMetadataDisplayItem.from_deployment(model)
            yield item


def describe_deploy(deployment_name: str, output: OutputDisplay = OutputDisplay.TABLE, **kwargs):
    """
    Fetches more details of a Inference Deployment
    """
    del kwargs

    try:
        deployment = get_inference_deployment(deployment_name)
    except MAPIException as e:
        logger.error(f'{FAIL} {e}')
        return 1

    # Deployment metadata section
    print(format_string('Inference Deployment Metadata', FormatString.BOLD))
    metadata_display = MCLIDescribeDeploymentMetadataDisplay([deployment])
    metadata_display.print(output)
    print()

    # Deployment original input section
    print(format_string('Submitted YAML', FormatString.BOLD))
    print(deployment.submitted_config)
