import datetime
from typing import Optional, Tuple

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from .. import interactive_console
from ..entities.create_ml_dataset_job import CreateMLDatasetJob
from ..entities.ml_dataset import MLDataset
from ..utils import Utils


class MLDatasets:
    def __init__(self, stub: CoreServiceStub, feature_view):
        self._feature_view = feature_view
        self._stub = stub

    @interactive_console.record_stats
    def create(
        self,
        name: str,
        description: str = "",
        start_date_time: Optional[datetime.datetime] = None,
        end_date_time: Optional[datetime.datetime] = None,
    ):
        """Create a machine learning dataset (MLDataset).

        Args:
            name: (str) Title of a new MLDataset.
            description: (str) Description about a new MLDataset.
            start_date_time: (datetime.datetime) Object represents start time for setting the start line
              of range in ingestion data.
            end_date_time: (datetime.datetime) Object represents end time for setting the last line
              of range in ingestion data.

        Returns:
            MLDataset: Machine Learning Dataset

        Typical example:
            ml_dataset = my_feature_view.ml_datasets.create("name", start_date_time=None, end_date_time=None)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#creating-a-mldataset
        """
        job, ml_dataset = self.create_async(name, description, start_date_time, end_date_time)
        return job.wait_for_result()

    def create_async(
        self,
        name: str,
        description: str = "",
        start_date_time: Optional[datetime.datetime] = None,
        end_date_time: Optional[datetime.datetime] = None,
    ) -> Tuple[CreateMLDatasetJob, MLDataset]:
        """Create a job for machine learning dataset (MLDataset) creation.

        Args:
            name: (str) Title for a new MLDataset.
            description: (str) Description about a new MLDataset.
            start_date_time: (datetime.datetime) Object represents start time for setting the start line
              of range in ingestion data.
            end_date_time: (datetime.datetime) Object represents end time for setting the last line
              of range in ingestion data.

        Returns:
            Tuple[CreateMLDatasetJob, MLDataset]

            CreateMLDatasetJob: Represents a job

        Typical example:
            my_feature_view.ml_datasets.create_async("name", start_date_time=None, end_date_time=None)
        """
        request = pb.CreateMLDatasetRequest(
            name=name,
            description=description,
            feature_view_id=self._feature_view.id,
            feature_view_version=self._feature_view.version,
            start_date_time=Utils.date_time_to_proto_timestamp(start_date_time),
            end_date_time=Utils.date_time_to_proto_timestamp(end_date_time),
        )

        response = self._stub.CreateMLDataset(request)
        return CreateMLDatasetJob(self._stub, response.job), MLDataset(self._stub, response.ml_dataset)

    def get(self, name: str):
        """Obtain a specific machine learning dataset (MLDataset).

        Args:
            name: (str) Title of an existing MLDataset.

        Returns:
            MLDataset: Machine Learning Dataset

        Typical example:
            my_feature_view.ml_datasets.get("name")
        """
        request = pb.GetMLDatasetRequest(
            feature_view_id=self._feature_view.id,
            feature_view_version=self._feature_view.version,
            ml_dataset_name=name,
        )

        ml_dataset = self._stub.GetMLDataset(request)
        return MLDataset(self._stub, ml_dataset)

    def list(self):
        """List machine learning datasets (MLDatasets).

        Returns:
            list[MLDataset]: A list of MLDatasets.

        Typical example:
            my_feature_view.ml_datasets.list()
        """
        request = pb.ListMLDatasetsRequest(
            feature_view_id=self._feature_view.id,
            feature_view_version=self._feature_view.version,
        )

        response = self._stub.ListMLDatasets(request)
        return [MLDataset(self._stub, ml_dataset) for ml_dataset in response.ml_datasets]
