import logging
import sys
from time import sleep

from kumoai.client import KumoClient
from kumoai.datamodel.jobs import (JobStatus, MetadataField,
                                 PredictionArtifactType, PredictionStorageType,
                                 S3PredictionOutput)

logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

kumo_client = KumoClient.from_env()


def run_training_job(pquery_name: str, poll_interval_seconds: float = 10.0):
    """
    This example demonstrates how to start a query (re)training job, and wait
    until it finishes by polling the job status every `poll_interval_seconds`.
    """
    # Kick off a training job.
    training_job = kumo_client.create_training_job(pquery_id=pquery_name)

    # Poll job status every 10 seconds and log job status/progress.
    while training_job.job_status_report.status == JobStatus.RUNNING:
        logger.info('Job status: %s', training_job.job_status_report)
        sleep(poll_interval_seconds)
        training_job = kumo_client.get_training_job(training_job.job_id)

    # Check if job is successful.
    if training_job.job_status_report.status == JobStatus.DONE:
        logger.info('Query %s training job %s succeeded! Result:\n%s',
                    training_job.predictive_query_id, training_job.job_id,
                    training_job.result)
    else:
        raise RuntimeError(f'Training failed: {training_job}')


def run_prediction_job(s3_prediction_file_path: str,
                       poll_interval_seconds: float = 10.0):
    """
    This example demonstrates how to start a batch prediction job, and wait
    until it finishes by polling the job status every `poll_interval_seconds`.
    """
    # Kick off a batch prediction job.
    prediction_job = kumo_client.create_batch_prediction_job(
        pquery_id='my_predictive_query',
        outputs=[
            S3PredictionOutput(
                storage_type=PredictionStorageType.S3,
                artifact_type=PredictionArtifactType.PREDICTIONS,
                file_path=s3_prediction_file_path,
                extra_fields=[
                    MetadataField.JOB_TIMESTAMP, MetadataField.ANCHOR_TIMESTAMP
                ])
        ],
    )

    # Poll job status every 10 seconds and log job status/progress.
    while prediction_job.job_status_report.status == JobStatus.RUNNING:
        logger.info('Job status: %s', prediction_job.job_status_report)
        sleep(poll_interval_seconds)
        prediction_job = kumo_client.get_batch_prediction_job(
            prediction_job.job_id)

    # Check if job is successful.
    if prediction_job.job_status_report.status == JobStatus.DONE:
        logger.info(
            'Query %s batch prediction job=%s succeeded! Job summary:\n%s',
            prediction_job.predictive_query_id, prediction_job.job_id,
            prediction_job.result)
    else:
        raise RuntimeError(f'Batch prediction failed: {prediction_job}')
