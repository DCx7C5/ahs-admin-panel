from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class WebAuthnAPITests(APITestCase):
    def test_register_options_returns_challenge(self):
        url = reverse('auth:webauthn_reg')
        data = {
            "username": "alice",
            "pubkeycredparams": [-7],
            "authattachment": "platform",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resp_json = response.json()
        self.assertIn("options", resp_json)
        self.assertIn("random", resp_json)

    def test_verify_registration_missing_data(self):
        url = reverse('auth:webauthn_verify_reg')
        response = self.client.post(url, {}, format="json")
        self.assertIn(response.status_code, (400, 422))
        resp_json = response.json()
        self.assertTrue("error" in resp_json or "errors" in resp_json)

    def test_authentication_options_invalid_user(self):
        url = reverse('auth:webauthn_auth')
        response = self.client.post(url, {"username": "noexists"}, format="json")
        self.assertIn(response.status_code, (400, 404, 403))

    def test_authentication_options_valid_user(self):
        from django.contrib.auth import get_user_model
        from backend.ahs_auth.models.webauthn import WebAuthnCredential  # Adjust path if needed
        user = get_user_model().objects.create(username="testauthn")

        # Create a minimal valid credential for this user so the endpoint succeeds
        WebAuthnCredential.objects.create(
            user=user,
            credential_id=b"testcredid000000000000000000",
            public_key=b"testpubkey",
            sign_count=0,
            credential_type="public-key",
            device_type="multi-device",
        )

        url = reverse('auth:webauthn_auth')
        response = self.client.post(url, {"username": user.username}, format="json")
        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertTrue("options" in resp_json or "challenge" in resp_json)

    def test_authentication_verify_invalid_user(self):
        url = reverse('auth:webauthn_verify_auth')
        response = self.client.post(url, {"username": "noexists"}, format="json")
        self.assertIn(response.status_code, (400, 404, 403))

    def test_authentication_verify_valid_user(self):
        ...
