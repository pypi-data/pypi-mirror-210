""" MCLI Package """

from mcli.api.cluster import get_clusters
from mcli.api.exceptions import MAPIException
from mcli.api.inference_deployments import (InferenceDeployment, InferenceDeploymentConfig, create_inference_deployment,
                                            delete_inference_deployment, delete_inference_deployments,
                                            get_inference_deployment, get_inference_deployment_logs,
                                            get_inference_deployments, ping, predict)
from mcli.api.runs import (FinalRunConfig, Run, RunConfig, RunStatus, create_run, delete_run, delete_runs,
                           follow_run_logs, get_run, get_run_logs, get_runs, start_run, start_runs, stop_run, stop_runs,
                           update_run_metadata, wait_for_run_status, watch_run_status)
from mcli.api.secrets import create_secret, delete_secrets, get_secrets
from mcli.cli.m_init.m_init import initialize
from mcli.cli.m_set_unset.api_key import set_api_key
from mcli.config import FeatureFlag, MCLIConfig

from .version import __version__

__all__ = [
    'create_inference_deployment',
    'create_run',
    'create_secret',
    'delete_inference_deployment',
    'delete_inference_deployments',
    'delete_run',
    'delete_runs',
    'delete_secrets',
    'FeatureFlag',
    'FinalRunConfig',
    'follow_run_logs',
    'get_clusters',
    'get_inference_deployment_logs',
    'get_inference_deployment',
    'get_inference_deployments',
    'get_run_logs',
    'get_run',
    'get_runs',
    'get_secrets',
    'InferenceDeployment',
    'InferenceDeploymentConfig',
    'initialize',
    'MAPIException',
    'MCLIConfig',
    'ping',
    'predict',
    'Run',
    'RunConfig',
    'RunStatus',
    'set_api_key',
    'start_run',
    'start_runs',
    'stop_run',
    'stop_runs',
    'update_run_metadata',
    'wait_for_run_status',
    'watch_run_status',
]
