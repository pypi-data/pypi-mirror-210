from contextlib import contextmanager
from typing import Type

import pytest
from packaging import version

import masogram


@contextmanager
def check_deprecated(
    max_version: str,
    exception: Type[Exception],
    warning: Type[Warning] = DeprecationWarning,
) -> None:
    """
    Should be used for modules that are being deprecated or already removed from masogram
    """

    parsed_max_version = version.parse(max_version)
    current_version = version.parse(masogram.__version__)

    if parsed_max_version <= current_version:
        with pytest.raises(exception):
            yield
    else:
        with pytest.warns(warning, match=max_version):
            yield
