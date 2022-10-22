from decimal import Decimal

from sqlmodel import Session, select

from database.db import engine
from database.models.monitoring_rules import MonitoringRule, AreaDefinition, TimeWindowDefinition
from monitoring_service.client import EDRWeatherClient


def dispatch_monitoring_request(rule: MonitoringRule):

    client = EDRWeatherClient()

    area_definition = AreaDefinition.parse_obj(rule.area_definition)
    time_window_definition = TimeWindowDefinition.parse_obj(rule.time_window)

    print(area_definition)
    print(time_window_definition)
    assert False
    resp = client.fetch_data(
        lat=Decimal(rule.area_definition.),
        long=Decimal("17.124840"),
        # dtime=datetime.fromisoformat("2022-10-24T03:00:00"),
        metric=MetricType.RelativeHumidity,
        query_type="radius",
        query_params={
            "within": 2,
            "within-units": "km"
        }
    )


def run_monitoring_flow():
    with Session(engine) as session:
        stmt = select(MonitoringRule)
        monitoring_rules = session.exec(stmt).all()
        print(monitoring_rules)

        resp = dispatch_monitoring_request(monitoring_rules[0])



if __name__ == "__main__":
    run_monitoring_flow()
