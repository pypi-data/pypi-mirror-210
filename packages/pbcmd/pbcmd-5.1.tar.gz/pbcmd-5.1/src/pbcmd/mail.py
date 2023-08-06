"""Send an email using a remote SMTP server."""

import sys
import ssl
import json
import smtplib

import click

from .obscure import text_unobscure


@click.command()
@click.option(
    "-a",
    "--auth-file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Authentication file.",
)
@click.option("-t", "--to", type=str, required=True, help="Recipient email address.")
@click.option("-s", "--subject", required=True, help="Subject of the email.")
@click.option(
    "-b",
    "--body-file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default="-",
    show_default=True,
    help="Text file containing body of the email.",
)
def mail(auth_file, to, subject, body_file):
    """Send an email.

    Authentication file should be an obscured json file,
    containing the following fields:
    server, port, username, password, and sender_email
    """
    with open(auth_file, "rt") as fobj:
        auth = fobj.read()
        auth = text_unobscure(auth)
        auth = json.loads(auth)

    if body_file is None:
        body_text = sys.stdin.read()
    else:
        with open(body_file, "rt") as fobj:
            body_text = fobj.read()

    subject = subject.strip()
    body_text = body_text.strip()

    message = f"Subject: {subject}\nTo: {to}\n\n{body_text}"

    context = ssl.create_default_context()
    with smtplib.SMTP(auth["server"], auth["port"]) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(auth["username"], auth["password"])
        server.sendmail(auth["sender_email"], [to], message)

    click.secho("Email sent successfully", fg="green")


if __name__ == "__main__":
    mail()
