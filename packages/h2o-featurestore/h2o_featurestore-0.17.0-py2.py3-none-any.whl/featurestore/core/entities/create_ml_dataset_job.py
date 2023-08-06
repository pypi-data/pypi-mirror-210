from .base_job import BaseJob
from .ml_dataset import MLDataset


class CreateMLDatasetJob(BaseJob):
    def _response_method(self, job_id):
        return MLDataset(self._stub, self._stub.GetMLDatasetCreationJobOutput(job_id))
