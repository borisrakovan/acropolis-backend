import json

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from api.schemas import ReadMetricsResponse
from database.db import create_db_and_tables, engine
from database.models.alerts import AlertDefinition
from database.models.monitoring_rules import MonitoringRule, MonitoringRuleRead, MonitoringRuleCreate, MetricType

app = FastAPI(name="Acropolis API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/monitoring-rules/", response_model=list[MonitoringRule])
async def read_monitoring_rules(
    *, session: Session = Depends(get_session),
):
    monitoring_rules = session.exec(select(MonitoringRule)).all()
    return monitoring_rules


@app.get("/metrics/", response_model=ReadMetricsResponse)
async def read_metrics():
    return {
        "metrics": [metric.value for metric in list(MetricType)]
    }


@app.post("/monitoring-rules/", response_model=MonitoringRuleRead)
async def create_monitoring_rule(
    *,
    session: Session = Depends(get_session),
    monitoring_rule: MonitoringRuleCreate
):
    db_monitoring_rule = MonitoringRule.from_orm(monitoring_rule)
    area_definition = db_monitoring_rule.area_definition.dict()
    # db_monitoring_rule.area_definition = {
    #
    # }
    db_monitoring_rule.alert_definitions = [
        AlertDefinition.from_orm(alert)
        for alert in monitoring_rule.alert_definitions
    ]

    print(db_monitoring_rule)
    print(db_monitoring_rule.alert_definitions)
    session.add(db_monitoring_rule)
    session.commit()
    return db_monitoring_rule

