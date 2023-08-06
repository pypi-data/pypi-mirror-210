import logging
from dataclasses import field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import Field, validator
from pydantic.dataclasses import dataclass
from typing_extensions import Annotated

logger = logging.getLogger(__name__)


# Execution status of a Training or Batch Prediction job.
class JobStatus(Enum):
    # Job has been submitted and is currently running.
    RUNNING = 'RUNNING'

    # Terminal status:
    DONE = 'DONE'  # Job has completed successfully
    FAILED = 'FAILED'  # Job has failed due to error.
    CANCELLED = 'CANCELLED'  # Job has been aborted/cancelLed by the customer.


# Log entry to recorded detailed events throughout multi-step job execution.
@dataclass
class JobEventLogEntry:
    # Name of current stage (step).
    stage_name: str
    last_updated_at: datetime
    detail: Optional[str] = None


@dataclass
class JobStatusReport:
    status: JobStatus

    # URL to the Kumo web UI page that allows human to track and monitor job
    # progress, and also view the job summary after the job finishes.
    tracking_url: str

    start_time: datetime
    end_time: Optional[datetime] = None  # Present when status is not RUNNING

    # Informational job execution event log for logging/debugging purpose.
    event_log: List[JobEventLogEntry] = field(default_factory=list)


class MetricName(Enum):
    _UNKNOWN = "_UNKNOWN"

    # TaskType.CLASSIFICATION:
    ACCURACY = 'ACCURACY'

    # TaskType.BINARY_CLASSIFICATION
    AUPRC = 'AUPRC'
    AUROC = 'AUROC'

    # TaskType.MULTILABEL
    F1 = 'F1'
    HR1 = 'HR1'
    PRECISION = 'PRECISION'
    RECALL = 'RECALL'

    # TaskType.REGRESSION
    MAE = 'MAE'
    MSE = 'MSE'
    MAPE = 'MAPE'
    SMAPE = 'SMAPE'
    NORMALIZD_MAE = 'NORMALIZD_MAE'
    NORMALIZED_MSE = 'NORMALIZED_MSE'
    NORMALIZED_MAPE = 'NORMALIZED_MAPE'
    NORMALIZED_SMAPE = 'NORMALIZED_SMAPE'

    # TaskType.LINK_PREDICTION
    LINK_ACCURACY_NEGATIVES = 'LINK_ACCURACY_NEGATIVES'
    LINK_ACCURACY_POSITIVES = 'LINK_ACCURACY_POSITIVES'
    LP_AUROC = 'LP_AUROC'

    # Validation Loss
    LOSS = 'LOSS'

    @classmethod
    def _missing_(cls, value):
        logger.error(
            'MetricName %s is undefined, please upgrade the kumo SDK '
            'to the latest version: `pip install --upgrade kumo-ai` '
            'or contact Kumo if the problem still remains', value)
        return MetricName._UNKNOWN


@dataclass
class Metric:
    name: MetricName
    value: Optional[float]


@dataclass
class ModelEvaluationMetrics:
    # Eval metrics on the test(holdout) data split.
    test_metrics: List[Metric] = field(default_factory=list)

    # Eval metrics on the validation data split.
    validation_metrics: List[Metric] = field(default_factory=list)

    # Eval metrics on the training data split.
    training_metrics: List[Metric] = field(default_factory=list)

    @validator('test_metrics', 'validation_metrics', 'training_metrics')
    def _skip_unknown_metrics(cls, metrics: List[Metric]) -> List[Metric]:
        return [
            metric for metric in metrics if metric.name != MetricName._UNKNOWN
        ]


@dataclass
class TrainingJobSummary:
    """Summary report of a successful query training job."""
    # Model eval metrics are available when job status is DONE.
    eval_metrics: ModelEvaluationMetrics

    # TODO(siyang): other stats/info such as cost (GPU hours), etc.
    total_elapsed_time: timedelta
    automl_experiments_completed: int


@dataclass
class TrainingJobResource:
    job_id: str

    predictive_query_id: str

    job_status_report: JobStatusReport

    # Present if job status is DONE.
    result: Optional[TrainingJobSummary] = None

    advanced_options_yaml: Optional[str] = None


@dataclass
class BatchPredictionOptions:
    # Required if prediction task is to perform binary classification.
    binary_classification_threshold: Optional[float] = None

    # On classification tasks, for each entity, we will only return predictions
    # for the K classes with the highest predicted values for the entity.
    # If empty, predict all class. This field is ignored for regression tasks.
    num_classes_to_return: Optional[int] = None


class PredictionArtifactType(Enum):
    """Specifies what kind of batch predictions should be generated.
    The user may specify multiple types of predictions to be computed, and
    each one will be output to a separate file.
    """
    PREDICTIONS = "PREDICTIONS"
    EMBEDDINGS = "EMBEDDINGS"


class PredictionStorageType(Enum):
    S3 = "S3"
    SNOWFLAKE = "SNOWFLAKE"


# Metadata fields that can be optionally selected and included as additional
# columns in the output table.
class MetadataField(Enum):
    ANCHOR_TIMESTAMP = 'ANCHOR_TIMESTAMP'
    JOB_TIMESTAMP = 'JOB_TIMESTAMP'


@dataclass
class SnowflakePredictionOutput:
    storage_type: Literal[PredictionStorageType.SNOWFLAKE]
    artifact_type: PredictionArtifactType
    connector_id: str
    table_name: str
    # Select additional metadata fields to be included as columns in data.
    extra_fields: List[MetadataField] = field(default_factory=list)


@dataclass
class S3PredictionOutput:
    storage_type: Literal[PredictionStorageType.S3]
    artifact_type: PredictionArtifactType
    file_path: str
    # Select additional metadata fields to be included as columns in data.
    extra_fields: List[MetadataField] = field(default_factory=list)


PredictionOutputConfig = Annotated[Union[SnowflakePredictionOutput,
                                         S3PredictionOutput],
                                   Field(discriminator='storage_type')]


# Request body to create a Batch Prediction job.
@dataclass
class BatchPredictionRequest:
    predict_options: BatchPredictionOptions
    outputs: List[PredictionOutputConfig] = field(default_factory=list)


@dataclass
class BatchPredictionJobSummary:
    """Summary of a successful batch prediction job."""
    num_entities_predicted: int
    # TODO: Add more stats


@dataclass
class BatchPredictionJobResource:
    job_id: str
    predictive_query_id: str
    outputs: List[PredictionOutputConfig]
    predict_options: BatchPredictionOptions

    job_status_report: JobStatusReport

    # Present if job status is DONE.
    result: Optional[BatchPredictionJobSummary] = None
