from mlr_pos_nodeless_payments.models.pos_payment_method import PosPaymentMethod
import unittest
from http_client_mock import HttpClientMock

GET_API = '/api/v1/transaction' # Get nodeless transactions list
POST_API = '/api/v1/paywall/{id}/invoice' # Create nodeless store invoice
DEFAULT_PAYLOAD = ['foo', 'bar']

class TestPosPaymentMethod(unittest.TestCase):
    """Tests for PosPaymentMethod"""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.pos_payment_method = PosPaymentMethod()

    def test_call_nodeless_api_post_bad_payload(self):
        # Test call_nodeless_api with bad payload
        with self.assertRaises(TypeError):
            self.pos_payment_method.call_nodeless_api(None, POST_API, 'POST')

    def test_call_nodeless_api_get_bad_api(self):
        # Test call_nodeless_api with bad API
        response = self.pos_payment_method.call_nodeless_api(DEFAULT_PAYLOAD, None, 'GET')
