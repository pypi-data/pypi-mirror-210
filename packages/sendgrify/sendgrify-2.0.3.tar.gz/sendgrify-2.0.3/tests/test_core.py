from types import SimpleNamespace

import pytest
import python_http_client
import sendgrid

from sendgrify import SendGrid


class MockHttpClient:
    def __init__(self, *args, **kwargs):
        self.mail = SimpleNamespace()
        self.mail.send = SimpleNamespace()
        self.mail.send.post = self.post

    def post(self, *args, **kwargs):
        self.post_made = True


@pytest.fixture()
def sg_handler(monkeypatch):
    monkeypatch.setattr(python_http_client, 'Client', MockHttpClient)
    return SendGrid('top-secret', 'from@example.com', 'From PyTest')


def test_init(sg_handler):
    assert isinstance(sg_handler.sg, sendgrid.SendGridAPIClient)
    assert sg_handler.data['from']['email'] == 'from@example.com'
    assert sg_handler.data['from']['name'] == 'From PyTest'


def test_send(sg_handler):
    to = 'to@example.com'
    subject = 'PyTest'
    msg = 'PyTest'
    sg_handler.send(to=to, subject=subject, msg=msg)
    assert sg_handler.data["personalizations"][0]["to"] == [{'email': to}]
    assert sg_handler.data["personalizations"][0]["subject"] == subject
    assert sg_handler.data["content"][0]["value"] == msg
    assert sg_handler.sg.client.post_made is True


def test_cc(sg_handler):
    to = 'to@example.com'
    subject = 'PyTest'
    msg = 'PyTest'
    cc = ['one@example.com', 'two@example.com']
    sg_handler.send(to=to, subject=subject, msg=msg, cc=cc)
    assert cc == [t['email'] for t in sg_handler.data["personalizations"][0]["cc"]]
    assert sg_handler.sg.client.post_made is True


def test_bcc(sg_handler):
    to = 'to@example.com'
    subject = 'PyTest'
    msg = 'PyTest'
    bcc = ['one@example.com', 'two@example.com']
    sg_handler.send(to=to, subject=subject, msg=msg, bcc=bcc)
    assert bcc == [t['email'] for t in sg_handler.data["personalizations"][0]["bcc"]]
    assert sg_handler.sg.client.post_made is True


def test_attachments(sg_handler):
    to = 'to@example.com'
    subject = 'PyTest'
    msg = 'PyTest'
    attachments = ['README.md', 'LICENSE']
    sg_handler.send(to=to, subject=subject, msg=msg, attachments=attachments)
    assert all([a['content'] for a in sg_handler.data['attachments']])
    assert attachments == [a['filename'] for a in sg_handler.data['attachments']]
    assert sg_handler.sg.client.post_made is True
