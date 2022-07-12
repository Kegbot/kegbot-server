"""Unittests for the checkin module."""

from unittest.mock import Mock, patch

from django.test import TransactionTestCase

from pykeg.core import checkin, models
from pykeg.core.util import get_version


class CheckinTestCase(TransactionTestCase):
    def test_checkin(self):

        site = models.KegbotSite.get()
        site.registration_id = "original-regid"
        site.save()

        version = get_version()

        with patch("requests.post") as mock_post:
            mock_post.return_value = mock_response = Mock()

            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok", "reg_id": "new-regid"}
            checkin.checkin("http://example.com/checkin", "test-product", 1.23)
            mock_post.assert_called_with(
                "http://example.com/checkin",
                headers={"User-Agent": "KegbotServer/%s" % version},
                data={
                    "reg_id": "original-regid",
                    "product": "test-product",
                    "version": version,
                },
                timeout=1.23,
            )

        site = models.KegbotSite.get()
        self.assertEqual("new-regid", site.registration_id)
