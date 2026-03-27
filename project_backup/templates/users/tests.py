from __future__ import annotations

from django.test import Client, TestCase
from django.urls import reverse


class PrivateKeyDownloadTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_download_private_key_requires_session(self) -> None:
        resp = self.client.get(reverse("download-private-key"))
        self.assertEqual(resp.status_code, 302)

    def test_download_private_key_returns_attachment_once(self) -> None:
        session = self.client.session
        session["registration_private_key_pem"] = "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----\n"
        session["registration_email"] = "user@example.com"
        session.save()

        resp = self.client.get(reverse("download-private-key"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment;", resp.headers.get("Content-Disposition", ""))
        self.assertIn("private_key.pem", resp.headers.get("Content-Disposition", ""))
        self.assertEqual(resp.content.decode("utf-8"), session["registration_private_key_pem"])

        resp2 = self.client.get(reverse("download-private-key"))
        self.assertEqual(resp2.status_code, 302)
