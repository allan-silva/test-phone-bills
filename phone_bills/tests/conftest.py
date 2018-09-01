import pytest
from billingcommon.db import BillingDb


@pytest.fixture
def dbo():
    db = BillingDb('sqlite://')
    db.metadata.create_all()
    return db
