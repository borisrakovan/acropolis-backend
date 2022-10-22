from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Literal, Any

import numpy as np

from database.models.monitoring_rules import MetricType
from monitoring_service.weather_client import EDRWeatherClient


class MetricDataProvider(ABC):

    def __init__(self, weather_client: EDRWeatherClient):
        self._weather_client = weather_client

    @abstractmethod
    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None,
        time_interval: tuple[datetime, datetime] = None
    ) -> np.ndarray:
        ...


class TemperatureDataProvider(MetricDataProvider):
    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None,
        time_interval: tuple[datetime, datetime] = None
    ) -> np.ndarray:
        data = self._weather_client.fetch_data(
            metric=MetricType.Temperature,
            lat=lat,
            long=long,
            collection="height-above-ground",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )

        return self._kelvin_2_celsius(data)

    @staticmethod
    def _kelvin_2_celsius(k: np.ndarray):
        return k - 273.15


class PrecipitationDataProvider(MetricDataProvider):
    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None,
        time_interval: tuple[datetime, datetime] = None
    ) -> np.ndarray:
        data = self._weather_client.fetch_data(
            metric=MetricType.Precipitation,
            lat=lat,
            long=long,
            collection="height-above-ground",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )


class RelativeHumidityDataProvider(MetricDataProvider):
    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None,
        time_interval: tuple[datetime, datetime] = None
    ) -> np.ndarray:
        ...


class WindSpeedDataProvider(MetricDataProvider):
    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None,
        time_interval: tuple[datetime, datetime] = None
    ) -> np.ndarray:
        data = self._weather_client.fetch_data(
            metric=MetricType.WindSpeed,
            lat=lat,
            long=long,
            collection="height-above-ground",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )



def create_data_provider(metric: MetricType):
    """Metric data provider factory"""
    weather_client = EDRWeatherClient()
    providers = {
        MetricType.Temperature: TemperatureDataProvider(weather_client),
        MetricType.WindSpeed: WindSpeedDataProvider(weather_client),
        MetricType.RelativeHumidity: RelativeHumidityDataProvider(weather_client),
        MetricType.Precipitation: PrecipitationDataProvider(weather_client),
    }
    return providers[metric]
