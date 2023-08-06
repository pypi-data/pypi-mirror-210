import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ..entities.transformation_function import TransformationFunctionMetadata


class TransformationFunctions:
    def __init__(self, stub: CoreServiceStub):
        self._stub = stub

    def list(self):
        response: pb.ListTransformationFunctionsResponse = self._stub.ListTransformationFunctions(
            pb.ListTransformationFunctionsRequest()
        )
        return [
            TransformationFunctionMetadata(transformation_function)
            for transformation_function in response.transformation_functions
        ]

    def get(self, function_name: str):
        response = self._stub.GetTransformationFunction(
            pb.GetTransformationFunctionRequest(transformation_function_name=function_name)
        )
        return TransformationFunctionMetadata(response.transformation_function)
