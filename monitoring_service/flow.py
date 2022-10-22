import logging

import numpy as np
from sqlmodel import Session, select

from database.db import engine
from database.models.alerts import AlertTrigger
from database.models.monitoring_rules import EvaluationMode, \
    LogicalOperator, MetricType
from database.models.monitoring_runs import MonitoringRun
from monitoring_service.weather_client import NoDataException
from datetime import datetime, timedelta

from database.models.monitoring_rules import MonitoringRule, AreaDefinition, TimeWindowDefinition
from monitoring_service.evaluation import create_data_provider




def evaluate_monitoring_rule(rule: MonitoringRule, data: np.ndarray) -> AlertTrigger | None:

    if rule.evaluation_mode == EvaluationMode.SINGLE_VALUE:
        # we are looking for extremal values, either min of max based on logic operator
        if rule.logical_operator in [LogicalOperator.LTE, LogicalOperator.LT]:
            # data = data.min(axis=1, initial=np.inf)
            metric_value = data.min(initial=np.inf)

        else:
            # data = data.max(axis=1, initial=-np.inf)
            metric_value = data.max(initial=-np.inf)

    elif rule.evaluation_mode == EvaluationMode.AVERAGE_VALUE:
        # average the value across all measurements in the area
        metric_value = data.mean()

    else:
        raise ValueError(f"Unknown evaluation mode {rule.evaluation_mode}")

    reference_value = rule.value

    alert_triggered = (
        rule.logical_operator == LogicalOperator.LTE and metric_value <= reference_value
        or rule.logical_operator == LogicalOperator.LT and metric_value < reference_value
        or rule.logical_operator == LogicalOperator.GTE and metric_value >= reference_value
        or rule.logical_operator == LogicalOperator.GT and metric_value > reference_value
    )

    if alert_triggered:
        return AlertTrigger(
            monitoring_rule=rule,
            triggered_at=datetime.now(),
            reference_value=reference_value,
            actual_value=metric_value,
        )

    return None


logger = logging.getLogger(__name__)


def dispatch_monitoring_request(rule: MonitoringRule) -> np.ndarray:
    """Fetch the weather data based on rule definition"""

    area_definition = AreaDefinition.parse_obj(rule.area_definition).__root__
    time_window_definition = TimeWindowDefinition.parse_obj(rule.time_window)

    time_from = datetime.now()
    timedelta_unit = "days" if time_window_definition.time_unit == "DAY" else "hours"
    time_to = time_from + timedelta(**{timedelta_unit: time_window_definition.value})

    data_provider = create_data_provider(rule.metric)

    if area_definition.type == "POINT-RADIUS-AREA":
        weather_data = data_provider.fetch_data(
            lat=area_definition.lat,
            long=area_definition.long,
            query_type="radius",
            query_params={
                "within": area_definition.radius,
                "within-units": area_definition.radius_unit.lower()
            },
            time_interval=(time_from, time_to),
            # dtime=datetime.fromisoformat("2022-10-24T03:00:00"),
        )
        return weather_data

    else:
        raise NotImplementedError()


def run_monitoring_flow() -> MonitoringRun:
    with Session(engine) as session:

        monitoring_run = MonitoringRun(started_at=datetime.now())
        session.add(monitoring_run)
        session.commit()
        session.refresh(monitoring_run)

        stmt = select(MonitoringRule).where(MonitoringRule.metric == MetricType.WindSpeed)
        monitoring_rules = session.exec(stmt).all()
        print(monitoring_rules)
        for rule in monitoring_rules:
            # evaluate the current rule
            print(f"Evaluating rule {rule.title}")

            try:
                weather_data = dispatch_monitoring_request(rule)
            except NoDataException as exc:
                print(str(exc))
                continue

            trigger = evaluate_monitoring_rule(rule, weather_data)

            if trigger is not None:
                logger.info(f"Monitoring rule triggered: {trigger}")
                trigger.monitoring_run = monitoring_run
                session.add(trigger)
                session.commit()

        monitoring_run.finished_at = datetime.now()
        session.add(monitoring_run)
        session.commit()

        return monitoring_run


