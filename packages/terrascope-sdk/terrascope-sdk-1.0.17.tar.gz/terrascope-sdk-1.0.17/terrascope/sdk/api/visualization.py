from enum import Enum
from typing import List

from terrascope_api import TerrascopeAsyncClient
from terrascope_api.models.visualization_pb2 import (
    VisualizationGetRequest, Visualization, VisualizerConfigAlgoCreateRequest, VisualizerConfigAlgoCreateResponse
)


class VisualizationConfigType(Enum):
    UNKNOWN_TYPE = 0
    STANDARD = 1
    SPATIAL = 2
    TEMPORAL = 3


class APIVisualization:
    def __init__(self, client: TerrascopeAsyncClient, timeout):
        self.__timeout = timeout
        self.__client = client

    async def get(self, result_observation_ids: List) -> List[Visualization]:
        """

        :param result_observation_ids:
        :return: List[Visualization]
        """
        request = VisualizationGetRequest(
            result_observation_ids=result_observation_ids
        )
        response = await self.__client.api.visualization.get(request)
        return response.visualizations

    async def create_visualizer_config_algo(self, visualizer_config_id: str,
                                            algorithm_version_id: str) -> VisualizerConfigAlgoCreateResponse:
        request = VisualizerConfigAlgoCreateRequest(
            visualizer_config_id=visualizer_config_id,
            algorithm_version_id=algorithm_version_id
        )
        response = await self.__client.api.visualization.create_config_algo(request)
        return response
