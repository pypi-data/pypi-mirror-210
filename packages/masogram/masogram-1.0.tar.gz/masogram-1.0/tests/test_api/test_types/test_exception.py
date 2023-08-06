import pytest

from masogram.exceptions import DetailedmasogramError


class TestException:
    @pytest.mark.parametrize(
        "message,result",
        [
            ["reason", "DetailedmasogramError('reason')"],
        ],
    )
    def test_representation(self, message: str, result: str):
        exc = DetailedmasogramError(message=message)
        assert repr(exc) == result
