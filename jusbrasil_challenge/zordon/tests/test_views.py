from json import loads

from django.test import TestCase
from django.http import HttpRequest
from django.contrib.auth.models import User

from zordon.views import BatchManager, ConsultationManager
from zordon.models import BatchConsultation, BatchGenerator, BatchLine


class BatchManagerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = BatchManager()
        cls.user = User.objects.create(
            id=1,
        )

    def setUp(self):
        self.request = HttpRequest()
        self.request.data = {
            "cnjs": ["0005691-75.2019.8.06.0134"],
            "refresh_lawsuit": True,
            "public_consultation": True,
        }
        self.request.user = self.user

    def test_post(self):
        """
        When request to post cnjs into batch through the BatchManager \
        Then create BatchGenerator structure and returns consultation_id \
        """
        response = self.view.post(self.request)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.data.get("consultationId"))

    def test_post_unsupported_cnj_error(self):
        """
        When request to post cnjs into batch through the BatchManager and cnj format is invalid \
        Then returns CNJUnsupportedError \
        """
        self.request.data["cnjs"] = "123456"
        expected_error_type = "CNJUnsupportedError"

        response = self.view.post(self.request)

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_error_type, response.data.get("type"))

    def test_post_missing_value_error(self):
        """
        When request to post cnjs into batch through the BatchManager and not pass 'cnjs' field in request data \
        Then returns MissingValueError \
        """
        self.request.data.pop("cnjs")
        expected_error_type = "MissingValueError"

        response = self.view.post(self.request)

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_error_type, response.data.get("type"))


class ConsultationManagerViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.view = ConsultationManager()
        cls.user = User.objects.create(
            id=1,
        )
        cls.batch_id = "cf7d1067-746c-41bf-829e-9ebf1dcb343a"
        cls.consultation_id = "d12ab1e7-6c71-4306-90e0-6c4b1097efa1"
        cls.batch_generator = BatchGenerator.objects.create(
            id=cls.batch_id, user=cls.user
        )
        cls.consultation = BatchConsultation.objects.create(
            id=cls.consultation_id, generator=cls.batch_generator
        )

    def setUp(self):
        self.request = HttpRequest()
        self.request.user = self.user

    def test_get(self):
        """
        When request to get captured batch infos through the consultation_id \
        Then returns BatchConsultation infos sucessfuly \
        """
        BatchLine.objects.create(generator=self.batch_generator)
        response = self.view.get(self.request, consultation_id=self.consultation_id)
        expected_type = "BatchConsultation"

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_type, response.data.get("type"))

    def test_get_required_consultation_id(self):
        """
        When request to get captured batch infos without consultation_id \
        Then returns BatchConsultationError type and required consultation description \
        """
        expected_type = "BatchConsultationError"
        expected_description = "Parameter 'consultation_id' is required"

        response = self.view.get(self.request)

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_type, response.data.get("type"))
        self.assertEqual(expected_description, response.data.get("description"))

    def test_get_invalid_uuid(self):
        """
        When request to get captured batch infos through the wrong consultation_id \
        Then returns BatchConsultationError type and uuid invalid description \
        """
        wrong_uuid = "1234"
        expected_type = "BatchConsultationError"
        expected_description = "'1234' is not a valid UUID"

        response = self.view.get(self.request, consultation_id=wrong_uuid)

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_type, response.data.get("type"))
        self.assertEqual(expected_description, response.data.get("description"))

    def test_get_unauthorized_consultation(self):
        """
        When request to get captured batch infos and user is not authorized or the consultation is not public \
        Then returns UnauthorizedConsultation type and unauthorized description \
        """
        expected_type = "UnauthorizedConsultation"
        expected_description = "Your profile is not authorized to get infos through this consultation_id 'd12ab1e7-6c71-4306-90e0-6c4b1097efa1'"

        self.request.user = User.objects.create(id=99, username="test")

        BatchLine.objects.create(generator=self.batch_generator)
        response = self.view.get(self.request, consultation_id=self.consultation_id)

        self.assertEqual(401, response.status_code)
        self.assertEqual(expected_type, response.data.get("type"))
        self.assertEqual(expected_description, response.data.get("description"))
