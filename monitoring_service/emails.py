import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase


class EmailMessage:
    def __init__(
        self,
        sender: str,
        recipients: list[str],
        subject: str,
    ):
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        self._msg = msg

    def add_body(self, message: str, html: bool = True) -> None:
        mime = MIMEText(message, "html" if html else "plain")
        self._msg.attach(mime)

    def add_attachment(self, content: bytes, filename: str) -> None:
        # Add file as application/octet-stream
        part = MIMEBase("application", "octet-stream")
        part.set_payload(content)

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        self._msg.attach(part)

    def as_string(self) -> str:
        return self._msg.as_string()


class EmailClient:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        login: str | None = None,
        password: str | None = None,
    ):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._login = login
        self._password = password

    def send_email(
        self,
        sender: str,
        recipients: list[str],
        message: EmailMessage
    ):
        context = ssl.create_default_context()
        with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self._login, self._password)
            server.sendmail(sender, recipients, message.as_string())
