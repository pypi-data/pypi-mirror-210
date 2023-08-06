from ..utils import Utils
from .base_job import BaseJob


class BackfillJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetBackfillJobOutput(job_id)
        return BackfillResponse(response)


class BackfillResponse:
    def __init__(self, response):
        self._response = response
        self._meta = response.ingest_response.meta

    def _get_feature_set(self):
        return self._response.ingest_response.feature_set

    def __repr__(self):
        return Utils.pretty_print_proto(self._meta)
