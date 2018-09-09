import os
import pytest
from tempfile import mkstemp
from phone_bills.billingcommon.db import BillingDb


@pytest.fixture(scope='module')
def dbo(request):
    handle, path = mkstemp()
    db = BillingDb(f'sqlite:///{path}')
    db.metadata.create_all()
    if hasattr(request, 'param') and request.param:
        request.param(db)
    yield db
    os.close(handle)
    os.remove(path)
