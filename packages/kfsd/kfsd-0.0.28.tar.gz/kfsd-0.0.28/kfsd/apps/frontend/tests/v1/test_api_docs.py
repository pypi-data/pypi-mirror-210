from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class APIDocsViewTests(TestCase):
    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    @patch("kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.genConfig")
    def test_get(self, genCommonConfigMocked, tokenUserInfoMocked):
        genCommonConfigMocked.side_effect = [{}]
        tokenUserInfoMocked.side_effect = [{"status": True, "data": {"user": {"identifier": "123", "is_staff": True, "is_active": True, "is_email_verified": True}}}]
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
