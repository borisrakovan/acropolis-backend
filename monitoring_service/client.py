import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
import numpy as np
import requests

import tortilla

from database.models.monitoring_rules import MetricType
from monitoring_service.utils import file_cache

logger = logging.getLogger(__name__)


class NoDataException(Exception):
    pass


class WeatherServerError(Exception):
    pass


TOTAL_ACC_PRECIPITATION_COLLECTION = {
    "pressure_gnd-surf": "single-layer", # (Pa)
    "total-precipitation_gnd-surf_stat": "single-layer", # kg/m²"
    "total-precipitation_gnd-surf_stat:acc/PT1H": "single-layer_3",
    "total-precipitation_gnd-surf_stat:acc/PT0S": "single-layer_2", # Total precipitation - Ground surface - Accumulation 0h
    "total-precipitation_gnd-surf_stat:acc/PT2H": "single-layer_4",
    "total-precipitation_gnd-surf_stat:acc/PT3H": "single-layer_5",
    "total-precipitation_gnd-surf_stat:acc/PT4H": "single-layer_6",
    "total-precipitation_gnd-surf_stat:acc/PT5H": "single-layer_7",
    "total-precipitation_gnd-surf_stat:acc/PT6H": "single-layer_8"
}


class EDRWeatherClient:

    _BASE_URL = "https://climathon.iblsoft.com/data/icon-de/edr"

    def __init__(self):
        self.api = tortilla.wrap(self._BASE_URL, debug=True)

    def fetch_data(
        self,
        *,
        lat: Decimal,
        long: Decimal,
        dtime: datetime | None = None,
        metric: MetricType,
        collection: str = "height-above-ground",
        query_type: Literal["radius"] | Literal["position"] = "radius",
        query_params: dict[str, Any] | None = None
    ) -> np.ndarray:

        parameter = metric.value.lower()

        params = {
            "coords": f"POINT({long} {lat})",
            "z": 2,
            "datetime": dtime.isoformat() if dtime else None,
            "parameter-name": parameter,
            "f": "CoverageJSON",
        } | query_params

        @file_cache("icon-de", f"collections/{query_type}/{json.dumps(params)}")
        def fetch():
            url = f"{self._BASE_URL}/collections/{collection}/{query_type}"
            response = requests.get(url, params=params)
            # base_req = self.api.collections(collection)
            # resp = getattr(base_req, query_type).get(
            #     params=params,
            #     silent=True
            # )
            print(url)

            if response.status_code == 204:
                raise NoDataException(f"No data for {str(params)}")

            resp_data = response.json()
            if "code" in resp_data and resp_data["code"] != "200":
                logger.error(str(resp_data))
                raise WeatherServerError(f"Error server response: {str(resp_data)}")

            return resp_data

        resp = fetch()

        if resp["type"] == "Coverage":
            # single time slice
            ...

        elif resp["type"] == "CoverageCollection":
            ...

        else:
            raise NotImplemented(f"Received coverage {resp['type']}")
        # 2022-10-22T06:00:00Z
        # 2022-10-24T06:00:00Z

        parameter_data = resp["ranges"][parameter]
        data = np.array(parameter_data["values"])
        data = data.reshape(parameter_data["shape"])

        if metric == MetricType.Temperature:
            data = kelvin_2_celsius(data)

        return data

    def list_collections(self):
        @file_cache("icon-de", "collections")
        def fetch():
            resp = client.api.collections.get()
            # print(resp.json())
            return resp

        resp = fetch()

        for col in resp["collections"]:
            print(col["id"] + " " + col["title"])


def kelvin_2_celsius(k: np.ndarray):
    return k - 273.15


if __name__ == "__main__":
    client = EDRWeatherClient()
    client.list_collections()
    assert False

    resp = client.fetch_data(
        lat=Decimal("48.163394"),
        long=Decimal("17.124840"),
        # dtime=datetime.fromisoformat("2022-10-24T03:00:00"),
        metric=MetricType.RelativeHumidity,
        query_type="radius",
        query_params={
            "within": 2,
            "within-units": "km"
        }
    )



    print(type(resp))
    print(resp)
    print()