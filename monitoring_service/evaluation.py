from abc import ABC, abstractmethod
from datetime import datetime, timedelta
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
            parameter_name="temperature",
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
    # 1 kg/m² = 1 mm
    TOTAL_ACC_PRECIPITATION_COLLECTION = [
        # "pressure_gnd-surf": "single-layer",  # (Pa)
        # Total precipitation - Ground surface - Accumulation 0h
        # "total-precipitation_gnd-surf_stat": "single-layer",  # kg/m²"
        ("total-precipitation_gnd-surf_stat:acc/PT0S", "single-layer_2",),
        ("total-precipitation_gnd-surf_stat:acc/PT1H", "single-layer_3",),
        ("total-precipitation_gnd-surf_stat:acc/PT2H", "single-layer_4",),
        ("total-precipitation_gnd-surf_stat:acc/PT3H", "single-layer_5",),
        ("total-precipitation_gnd-surf_stat:acc/PT4H", "single-layer_6",),
        ("total-precipitation_gnd-surf_stat:acc/PT5H", "single-layer_7",),
        ("total-precipitation_gnd-surf_stat:acc/PT6H", "single-layer_8"),
    ]

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

        time_delta = time_interval[1] - time_interval[0]

        hours = time_delta.seconds // 3600
        # we can look at most 6 hours
        hours = min(6, int(hours))

        parameter_name, collection = self.TOTAL_ACC_PRECIPITATION_COLLECTION[hours]

        return self._weather_client.fetch_data(
            parameter_name=parameter_name,
            lat=lat,
            long=long,
            collection=collection,
            query_type=query_type,
            query_params=query_params,
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
        return self._weather_client.fetch_data(
            parameter_name="precipitation",
            lat=lat,
            long=long,
            collection="height-above-ground",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )


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
        u_component = self._weather_client.fetch_data(
            parameter_name="u-component-of-wind",
            lat=lat,
            long=long,
            collection="height-above-ground_9",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )
        v_component = self._weather_client.fetch_data(
            parameter_name="v-component-of-wind",
            lat=lat,
            long=long,
            collection="height-above-ground_9",
            query_type=query_type,
            query_params=query_params,
            time_interval=time_interval,
        )
        wind_speed = np.sqrt(np.power(u_component, 2) + np.power(v_component, 2))
        return wind_speed


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
