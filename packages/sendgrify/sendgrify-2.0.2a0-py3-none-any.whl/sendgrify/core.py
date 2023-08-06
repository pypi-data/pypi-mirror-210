import base64
import json
import os

import markdown
import sendgrid
from python_http_client.exceptions import BadRequestsError


class SendGrid:
    def __init__(self, apikey: str, from_addr: str, from_name: str):
        self.sg = sendgrid.SendGridAPIClient(apikey=apikey)
        self.data = {
            "personalizations": [{"to": [], "subject": None}],
            "from": {"email": from_addr, "name": from_name},
            "content": [{"type": "text/plain", "value": None}],
        }

    def send(
        self,
        *,
        to: str,
        subject: str,
        msg: str,
        cc: list = [],
        bcc: list = [],
        attachments: list = [],
        as_markdown: bool = False,
    ):
        # personalizations -> to
        self.data["personalizations"][0]["to"] = []
        addrs = to if type(to) == list else [to]
        for addr in addrs:
            self.data["personalizations"][0]["to"].append({"email": addr})
        # personalizations -> subject
        self.data["personalizations"][0]["subject"] = subject
        # content -> value
        if as_markdown:
            msg = markdown.markdown(msg)
            self.data["content"][0]["type"] = "text/html"
        self.data["content"][0]["value"] = msg
        # personalizations -> cc
        if cc:
            self.data["personalizations"][0]["cc"] = []
            addrs = cc if type(cc) in (list, tuple) else [cc]
            for addr in addrs:
                self.data["personalizations"][0]["cc"].append({"email": addr})
        # personalizations -> bcc
        if bcc:
            self.data["personalizations"][0]["bcc"] = []
            addrs = bcc if type(bcc) in (list, tuple) else [bcc]
            for addr in addrs:
                self.data["personalizations"][0]["bcc"].append({"email": addr})
        # attachments
        if attachments:
            self.data["attachments"] = []
            attachments = attachments if type(attachments) in (list, tuple) else [attachments]
            for attachment in attachments:
                with open(attachment, "rb") as f:
                    file_content = f.read()
                    f.close()
                encoded_file_content = base64.b64encode(file_content).decode()
                self.data["attachments"].append(
                    {
                        "content": encoded_file_content,
                        "filename": os.path.split(attachment)[1],
                    }
                )

        try:
            self.sg.client.mail.send.post(request_body=self.data)
        except BadRequestsError as e:
            print(e.reason)
            print(json.loads(e.body)["errors"][0]["message"])
            print(json.loads(e.body)["errors"][0]["field"])
            print(json.loads(e.body)["errors"][0]["help"])
