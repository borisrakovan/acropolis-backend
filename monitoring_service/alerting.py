from configuration import Configuration
from database.models.alerts import AlertTrigger, AlertType
from monitoring_service.emails import EmailClient, EmailMessage


def send_alert_notifications(triggers: list[AlertTrigger]) -> None:
    email_client = EmailClient(
        smtp_server=Configuration.SERVICE_EMAIL_SERVER,
        smtp_port=Configuration.SERVICE_EMAIL_PORT_TLS,
        login=Configuration.SERVICE_EMAIL_ADDRESS,
        password=Configuration.SERVICE_EMAIL_PASSWORD,
    )

    for trigger in triggers:
        alerts = [
            # rest to be implemented
            alert for alert in trigger.monitoring_rule.alert_definitions
            if alert.alert_type == AlertType.Email
        ]
        for alert in alerts:
            message = EmailMessage(
                sender=Configuration.SERVICE_EMAIL_ADDRESS,
                recipients=[alert.contact_info],
                subject=f"Alert: {trigger.monitoring_rule.title}"
            )
            message.add_body(alert.message_template, html=False)
            email_client.send_email(
                sender=Configuration.SERVICE_EMAIL_ADDRESS,
                recipients=[alert.contact_info],
                message=message,
            )
