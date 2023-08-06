from dicomselect.database import database_version
from setup import version


def test_version():
    assert version == database_version