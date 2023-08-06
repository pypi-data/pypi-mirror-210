from typing import Optional

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ..entities.feature_view import FeatureView


class FeatureViews:
    def __init__(self, stub: CoreServiceStub, project):
        self._project = project
        self._stub = stub

    def create(self, name: str, query, description: str = ""):
        """Create a feature view.

        Args:
            name: (str) Title of new feature view.
            query: (Query) Object represents Query instance from featurestore.core.entities.query.
            description: (str) Description about new feature view.

        Returns:
            FeatureView: A feature view with relevant metadata.

        Typical example:
            feature_view = project.feature_views.create(name = "test", description="", query)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#creating-a-feature-view
        """
        request = pb.CreateFeatureViewRequest(
            name=name,
            description=description,
            project_id=self._project.id,
            query=query._to_proto(),
        )
        response = self._stub.CreateFeatureView(request)
        return FeatureView(self._stub, response.feature_view)

    def get(self, name: str, version: Optional[int] = None):
        """Obtain an existing feature view.

        Args:
            name: (str) Title of existing feature view.
            version: (int) Version of existing feature view.

        Returns:
            FeatureView: A feature view with relevant metadata.

        Typical example:
            feature_view = project.feature_views.get("feature_view_name", version=None)

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#obtaining-a-feature-view
        """
        request = pb.GetFeatureViewRequest(project_id=self._project.id, name=name, version=(version or 0))
        resource = self._stub.GetFeatureView(request)
        return FeatureView(self._stub, resource.feature_view)

    def list(self):
        """Return a collection of feature views within a project.

        Returns:
            list[FeatureView]: A list of existing feature views.

        Typical example:
            project.feature_views.list()

        For more details:
            https://docs.h2o.ai/feature-store/latest-stable/docs/api/feature_view_api.html#listing-feature-views-within-a-project
        """
        request = pb.ListFeatureViewsRequest(project_id=self._project.id)
        response = self._stub.ListFeatureViews(request)
        return [FeatureView(self._stub, feature_view) for feature_view in response.feature_views]
