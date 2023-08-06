from django.test import TestCase
from AkvoDjangoFormGateway.utils.validation import (
    is_date,
    is_valid_image,
    is_number,
    is_valid_string,
    is_valid_geolocation,
)


class UtilsValidationTestCase(TestCase):
    def setUp(self):
        self.data = {
            "geo": "[37.7749,-122.4194]",
            "text": "Call +6281393",
            "number": "123",
            "image_type": "image/png",
            "date": "17-5-2022",
        }

    def test_is_valid_alphanumeric(self):
        res = is_valid_string(input=self.data["text"])
        self.assertEqual(res, True)

    def test_is_invalid_alphanumeric(self):
        res = is_valid_string(input=f'{self.data["text"]}`*`')
        self.assertEqual(res, False)

    def test_is_valid_number(self):
        res = is_number(input=self.data["number"])
        self.assertEqual(res, True)

    def test_is_invalid_number(self):
        res = is_number(input=f'{self.data["number"]}O')
        self.assertEqual(res, False)

    def test_geo_string(self):
        valid = is_valid_geolocation(json_string=self.data["geo"])
        invalid1 = is_valid_geolocation(json_string="{37.7749,-122.4194}")
        invalid2 = is_valid_geolocation(json_string="['hello','world']")
        invalid3 = is_valid_geolocation(json_string="plaintext")
        self.assertEqual(valid, True)
        self.assertEqual(invalid1, False)
        self.assertEqual(invalid2, False)
        self.assertEqual(invalid3, False)

    def test_is_valid_date(self):
        res = is_date(input=self.data["date"])
        self.assertEqual(res, True)

    def test_is_invalid_date(self):
        res = is_date(input="2022-12-3")
        self.assertEqual(res, False)

    def test_is_valid_image(self):
        res = is_valid_image(image_type=self.data["image_type"])
        self.assertEqual(res, True)

    def test_is_invalid_image(self):
        res = is_valid_image(image_type="image.jpeg")
        self.assertEqual(res, False)
