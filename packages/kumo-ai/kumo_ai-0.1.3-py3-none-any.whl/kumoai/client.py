import os
from http import HTTPStatus
from typing import List, Optional

from requests import Response, Session

from kumoai.datamodel.data_source import (ConnectorResponse,
                                          SnowflakeConnectorArgs)
from kumoai.datamodel.jobs import (BatchPredictionJobResource,
                                   BatchPredictionOptions,
                                   BatchPredictionRequest, JobStatus,
                                   PredictionOutputConfig, TrainingJobResource)
from kumoai.datamodel.json_serde import from_json, to_json_dict
from kumoai.datamodel.pquery import (PQueryResource, S3SourceTableRequest,
                                     SnowflakeSourceTableRequest,
                                     SourceTableInfo)

API_VERSION = 'v1'


class KumoClient:
    """Client for accessing Kumo public API over http/REST.
    Users are recommended to use :py:meth:`from_env` to create a client while
    storing their secret api key in "KUMO_API_KEY" environment variable.
    """

    def __init__(self, api_key: str, base_url: str) -> None:
        self._session = Session()
        self._session.headers.update({"X-API-Key": api_key})
        # Allow overrie base url via 'KUMO_API_ENDPOINT' env variable.
        base_url_override = os.environ.get('KUMO_API_ENDPOINT', None)
        base_url = base_url_override or base_url
        self._base_url = f'{base_url}/{API_VERSION}'

    @staticmethod
    def from_env() -> 'KumoClient':
        """Create a KumoClient instance from env variable 'KUMO_API_KEY'."""
        api_key = os.environ['KUMO_API_KEY']
        customer_id = api_key.split(':')[0]
        base_url = f'https://{customer_id}-api.kumoai.cloud'
        return KumoClient(api_key, base_url)

    # === Connectors API (only support SNOWFLAKE now) === #
    #
    def create_snowflake_connector(
            self, snowflake_connector: SnowflakeConnectorArgs):
        url = f'{self._base_url}/connectors'
        res = self._session.post(url, json=to_json_dict(snowflake_connector))
        _check_success(res)

    def get_snowflake_connector_if_exists(
            self,
            snowflake_connector_name: str) -> Optional[ConnectorResponse]:
        url = f'{self._base_url}/connectors/{snowflake_connector_name}'
        res = self._session.get(url)
        _check_success(res, allow_not_found=True)

        if not res.ok:
            return None  # not found

        connector_type = res.json()['config']['type']
        if connector_type != 'snowflake':
            raise Exception(
                f'Connector with name {snowflake_connector_name} has '
                f'a different type: {connector_type} != snowflake')
        return from_json(res.json(), ConnectorResponse)

    def list_snowflake_connectors(self) -> List[ConnectorResponse]:
        url = f'{self._base_url}/connectors?data_source_type=SNOWFLAKE'
        res = self._session.get(url)
        _check_success(res)
        return [
            from_json(json_array_element, ConnectorResponse)
            for json_array_element in res.json()
        ]

    def delete_snowflake_connector_if_exists(self,
                                             snowflake_connector_name: str):
        if self.get_snowflake_connector_if_exists(snowflake_connector_name):
            url = f'{self._base_url}/connectors/{snowflake_connector_name}'
            res = self._session.delete(url)
            _check_success(res)

    # === List Source Table API === #
    #
    def list_s3_source_tables(self, s3_dir: str) -> List[SourceTableInfo]:
        url = f'{self._base_url}/source_tables/s3'
        res = self._session.post(url,
                                 json=to_json_dict(
                                     S3SourceTableRequest(s3_root_dir=s3_dir)))
        _check_success(res)
        return [
            from_json(json_array_element, SourceTableInfo)
            for json_array_element in res.json()
        ]

    def list_snowflake_source_tables(
            self, snowflake_connector_id: str) -> List[SourceTableInfo]:
        url = f'{self._base_url}/source_tables/snowflake'
        res = self._session.post(
            url,
            json=to_json_dict(
                SnowflakeSourceTableRequest(
                    snowflake_connector_id=snowflake_connector_id)))
        _check_success(res)
        return [
            from_json(json_array_element, SourceTableInfo)
            for json_array_element in res.json()
        ]

    # === Predictive Queries API: create, list, get, delete === #
    #
    def create_pquery(self, pquery_resource: PQueryResource):
        url = f'{self._base_url}/predictive_queries'
        res = self._session.post(url, json=to_json_dict(pquery_resource))
        _check_success(res)

    def get_pquery(self, query_name: str) -> PQueryResource:
        url = f'{self._base_url}/predictive_queries/{query_name}'
        res = self._session.get(url)
        _check_success(res)
        return from_json(res.json(), PQueryResource)

    def get_pquery_if_exists(self,
                             query_name: str) -> Optional[PQueryResource]:
        url = f'{self._base_url}/predictive_queries/{query_name}'
        res = self._session.get(url)
        _check_success(res, allow_not_found=True)
        return from_json(res.json(), PQueryResource) if res.ok else None

    def list_pqueries(self,
                      name_pattern: Optional[str] = None
                      ) -> List[PQueryResource]:
        url = f'{self._base_url}/predictive_queries'
        if name_pattern:
            url = f'{url}?name_pattern={name_pattern}'
        res = self._session.get(url)
        _check_success(res)
        return [from_json(pq_json, PQueryResource) for pq_json in res.json()]

    def delete_pquery_if_exists(self,
                                query_name: str,
                                *,
                                force_delete_all_jobs: bool = False) -> None:
        url = f'{self._base_url}/predictive_queries/{query_name}'
        if force_delete_all_jobs:
            url = f'{url}?force_delete=true'
        res = self._session.delete(url)
        _check_success(res, allow_not_found=True)

    # === Traning Jobs API: create, list, get, cancel, delete === #

    def create_training_job(self,
                            pquery_id: str,
                            advanced_options_yaml: Optional[str] = None
                            ) -> TrainingJobResource:
        url = f'{self._base_url}/predictive_queries/{pquery_id}/training_jobs'
        json_data = {}
        if advanced_options_yaml:
            json_data['advanced_options_yaml'] = advanced_options_yaml
        res = self._session.post(url, json=json_data)
        _check_success(res)
        return from_json(res.json(), TrainingJobResource)

    def list_training_jobs(
        self,
        pquery_id: str,
        job_status: Optional[JobStatus] = None,
    ) -> List[TrainingJobResource]:
        url = f'{self._base_url}/predictive_queries/{pquery_id}/training_jobs'
        if job_status:
            url = f'{url}?job_status={job_status}'
        res = self._session.get(url)
        _check_success(res)
        return [
            from_json(job_json, TrainingJobResource)
            for job_json in res.json()
        ]

    def get_training_job(self, training_job_id: str) -> TrainingJobResource:
        url = f'{self._base_url}/training_jobs/{training_job_id}'
        res = self._session.get(url)
        _check_success(res)
        return from_json(res.json(), TrainingJobResource)

    def cancel_training_job(self, training_job_id: str) -> None:
        url = f'{self._base_url}/training_jobs/{training_job_id}/cancel'
        res = self._session.post(url)
        _check_success(res)

    # Delete a training job by job id. If the training job finished
    # successfully, force_delete_model must be explicitly set to True in order
    # to force delete model artifact otherwise exception will be raised.
    def delete_training_job(self,
                            training_job_id: str,
                            *,
                            force_delete_model: bool = False) -> None:
        job = self.get_training_job(training_job_id)
        if (job.job_status_report.status == JobStatus.DONE
                and not force_delete_model):
            raise Exception(
                'force_delete_model must be set to True in order to delete a '
                'successful training job.')
        url = f'{self._base_url}/training_jobs/{training_job_id}'
        res = self._session.delete(url)
        _check_success(res)

    # === Batch Prediction Jobs API: create, list, get, cancel, delete === #
    def create_batch_prediction_job(
            self,
            pquery_id: str,
            outputs: List[PredictionOutputConfig],
            options=BatchPredictionOptions(),
    ) -> BatchPredictionJobResource:
        url = (f'{self._base_url}/predictive_queries'
               f'/{pquery_id}/prediction_jobs')
        job_request = BatchPredictionRequest(predict_options=options,
                                             outputs=outputs)
        res = self._session.post(url, json=to_json_dict(job_request))
        _check_success(res)
        return from_json(res.json(), BatchPredictionJobResource)

    def list_batch_prediction_jobs(
        self,
        pquery_id: str,
        job_status: Optional[JobStatus] = None,
    ) -> List[BatchPredictionJobResource]:
        url = (f'{self._base_url}/predictive_queries'
               f'/{pquery_id}/prediction_jobs')
        if job_status:
            url = f'{url}?job_status={job_status}'
        res = self._session.get(url)
        _check_success(res)
        return [
            from_json(job_json, BatchPredictionJobResource)
            for job_json in res.json()
        ]

    def get_batch_prediction_job(
            self, batch_prediction_job_id: str) -> BatchPredictionJobResource:
        url = f'{self._base_url}/prediction_jobs/{batch_prediction_job_id}'
        res = self._session.get(url)
        _check_success(res)
        return from_json(res.json(), BatchPredictionJobResource)

    def cancel_batch_prediction_job(self,
                                    batch_prediction_job_id: str) -> None:
        url = (f'{self._base_url}/prediction_jobs'
               f'/{batch_prediction_job_id}/cancel')
        res = self._session.post(url)
        _check_success(res)

    def delete_batch_prediction_job(self,
                                    batch_prediction_job_id: str) -> None:
        url = f'{self._base_url}/prediction_jobs/{batch_prediction_job_id}'
        res = self._session.delete(url)
        _check_success(res)


def _check_success(response: Response, allow_not_found: bool = False):
    if allow_not_found and response.status_code == HTTPStatus.NOT_FOUND:
        return
    if not response.ok:
        raise Exception(
            f'{response.url} failed, status code={response.status_code}, '
            f'reason: {response.reason}, message: {response.text}')
