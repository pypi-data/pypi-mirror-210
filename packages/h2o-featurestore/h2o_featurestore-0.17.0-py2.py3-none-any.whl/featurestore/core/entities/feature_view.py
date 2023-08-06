import datetime
import json
import time
from typing import Optional

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ..collections.ml_datasets import MLDatasets
from ..job_info import JobInfo
from ..utils import Utils
from .query import Query


class FeatureView:
    def __init__(self, stub: CoreServiceStub, feature_view):
        fv = pb.FeatureView()
        fv.CopyFrom(feature_view)
        self._feature_view = fv
        self._stub = stub
        self.ml_datasets = MLDatasets(stub, self)

    @property
    def id(self):
        return self._feature_view.id

    @property
    def version(self):
        return self._feature_view.version

    @property
    def name(self):
        return self._feature_view.name

    @property
    def query(self):
        return Query._from_proto(self._feature_view.query)

    @property
    def description(self):
        return self._feature_view.description

    @description.setter
    def description(self, value):
        update_request = pb.UpdateFeatureViewRequest(
            feature_view_id=self.id,
            feature_view_version=self.version,
            description=value,
        )
        response = self._stub.UpdateFeatureView(update_request)
        fv = pb.FeatureView()
        fv.CopyFrom(response.feature_view)
        self._feature_view = fv

    def create_new_version(self, new_query: Query):
        """Create a new version of a feature view.

        Args:
            new_query: (FeatureQuery) A feature query.

        Returns:
            FeatureView: A feature view with a new version.

        Typical example:
            fv.create_new_version(query)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_set_new_version.html
        """
        request = pb.CreateFeatureViewNewVersionRequest(
            feature_view_id=self.id,
            feature_view_version=self.version,
            query=new_query._to_proto(),
        )
        response: pb.FeatureViewResponse = self._stub.CreateFeatureViewNewVersion(request)
        return FeatureView(self._stub, response.feature_view)

    def delete(self):
        """Delete a feature view."""
        request = pb.DeleteFeatureViewRequest(feature_view_id=self.id)
        self._stub.DeleteFeatureView(request)

    def download(
        self,
        start_at: Optional[datetime.datetime] = None,
        end_at: Optional[datetime.datetime] = None,
        output_dir=None,
    ):
        """Download files to the specified directory location.

        This retrieves only a specific range of ingested data. If the parameters are empty,
        all ingested data are fetched.

        Args:
            start_at: (datetime.datetime) A start date and time of the range of ingested data.
            end_at: (datetime.datetime) A end date and time of the range of ingested data.
            output_dir: (str) A directory location as string. Default is None.

        Returns:
            str: A directory path where the files are downloaded.

        Typical usage example:
            dir = my_feature_view.download(start_at=None, end_at=None)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#downloading-the-files-from-feature-store
        """
        request = pb.RetrieveFeatureViewAsAsLinksRequest(
            feature_view_id=self.id,
            feature_view_version=self.version,
            start_at=Utils.date_time_to_proto_timestamp(start_at),
            end_at=Utils.date_time_to_proto_timestamp(end_at),
        )
        job_id = self._stub.StartRetrieveFeatureViewAsLinksJob(request)

        info = JobInfo(self._stub, job_id)
        while not self._stub.GetJob(job_id).done:
            info.show_progress()
            time.sleep(2)
        info.show_progress()  # there is possibility that some progress was pushed before finishing job
        response = self._stub.GetRetrieveFeatureViewAsLinksJobOutput(job_id)

        return Utils.download_files(output_dir, response.download_links)

    def as_spark_frame(
        self,
        spark_session,
        start_at: Optional[datetime.datetime] = None,
        end_at: Optional[datetime.datetime] = None,
    ):
        """Return a spark data frame.

        This generates a data frame of the retrieved data using spark session.

        Args:
            spark_session: (SparkSession) Represents a spark session.
            start_at: (datetime.datetime) A start date and time of the range of ingested data.
            end_at: (datetime.datetime) A end date and time of the range of ingested data.

        Returns:
            DataFrame: Represents a spark data frame.

        Typical usage example:
            data_frame = my_feature_view.as_spark_frame(spark_session, start_at=None, end_at=None)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#obtaining-data-as-a-spark-frame
        """
        from ..commons.spark_utils import SparkUtils

        session_id = spark_session.conf.get("ai.h2o.featurestore.sessionId", "")
        request = pb.RetrieveFeatureViewAsSparkRequest(
            feature_view_id=self.id,
            feature_view_version=self.version,
            start_at=Utils.date_time_to_proto_timestamp(start_at),
            end_at=Utils.date_time_to_proto_timestamp(end_at),
            session_id=session_id,
        )
        job_id = self._stub.StartRetrieveFeatureViewAsSparkJob(request)

        info = JobInfo(self._stub, job_id)
        while not self._stub.GetJob(job_id).done:
            info.show_progress()
            time.sleep(2)
        info.show_progress()  # there is possibility that some progress was pushed before finishing job
        response = self._stub.GetRetrieveFeatureViewAsSparkJobOutput(job_id)

        spark_session.conf.set("ai.h2o.featurestore.sessionId", response.session_id)

        SparkUtils.configure_user_spark(spark_session)
        for k, v in response.options.items():
            spark_session.conf.set(k, v)

        return spark_session.read.format("parquet").load(response.path)

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature_view)

    def __str__(self):
        selected_features = json.dumps(Utils.proto_to_dict(self._feature_view.query).get("selected_features"), indent=3)
        from_feature_set = json.dumps(Utils.proto_to_dict(self._feature_view.query).get("from_feature_set"), indent=3)
        join = json.dumps(Utils.proto_to_dict(self._feature_view.query).get("join"), indent=3)
        return (
            f"Name                  : {self.name} \n"
            f"Description           : {self.description} \n"
            f"Version               : {self.version} \n"
            f"Query                   \n"
            f"  Selected features   : {Utils.output_indent_spacing(selected_features, '  ')} \n"
            f"  From feature set    : {Utils.output_indent_spacing(from_feature_set, '  ')} \n"
            f"  Join                : {Utils.output_indent_spacing(join, '  ')} \n"
        )
