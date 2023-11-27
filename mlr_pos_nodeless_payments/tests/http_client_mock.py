import unittest
from unittest.mock import MagicMock

class HTTPClientMock:
    def mock_http_success(self):
        return MagicMock(status_code=200, text="{'success': True}")

    def mock_http_failure(self):
        return MagicMock(status_code=500, text="{'success': False}")
    
    def mock_http_error(self):
        raise Exception("Something went wrong")
