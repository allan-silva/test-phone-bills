import pytest
import uuid

from unittest.mock import patch, MagicMock
from phone_bills.billingapi.api import create_app
from phone_bills.billingmq.producer import BillingAPIProducer


TEST_TRANSACTION = uuid.UUID('16fd2706-8baf-433b-82eb-8c7fada84742')


@pytest.fixture
def client():
    app = create_app()
    return app.test_client()


@pytest.fixture
def call_start_record():
    return {
        'id': 42,
        'type': 'start',
        'timestamp': '2017-12-12T15:07:13Z',
        'call_id': 71,
        'source': '99988526423',
        'destination': '9993468278'
    }


@pytest.fixture
def call_end_record():
    return {
        'id': 442,
        'type': 'end',
        'timestamp': '2017-12-12T15:14:56Z',
        'call_id': 71
    }


@patch('uuid.uuid4', MagicMock(return_value=TEST_TRANSACTION))
def test_post_call_start_success(client, call_start_record):
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        response = client.post('/v1/call', json=call_start_record)
        assert response.status_code == 202
        transaction = response.get_json()
        assert transaction['transaction_id'] == str(TEST_TRANSACTION)
        assert amqp_mock.call_count == 1


@patch('uuid.uuid4', MagicMock(return_value=TEST_TRANSACTION))
def test_post_call_start_validation_error(client, call_start_record):
    call_start_record['source'] = call_start_record['destination']
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        response = client.post('/v1/call', json=call_start_record)
        assert response.status_code == 400
        response_error = response.get_json()
        assert response_error['transaction_id'] == str(TEST_TRANSACTION)
        assert not amqp_mock.called


@pytest.mark.parametrize('phone_number,http_status', [
        ('1127227777', 202),
        ('11272277771', 202),
        ('', 400),
        ('112722777', 400),
        ('112722777712', 400),
        ('1127227A77', 400),
        ('112A2277771', 400),
    ])
def test_post_call_start_phone_number_validation(client, call_start_record, phone_number, http_status):
    call_start_record['source'] = phone_number
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        response = client.post('/v1/call', json=call_start_record)
        assert response.status_code == http_status
        should_call_publish = True if http_status == 202 else False
        assert amqp_mock.called == should_call_publish


@patch('uuid.uuid4', MagicMock(return_value=TEST_TRANSACTION))
def test_post_call_end_success(client, call_end_record):
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        response = client.post('/v1/call', json=call_end_record)
        assert response.status_code == 202
        transaction = response.get_json()
        assert transaction['transaction_id'] == str(TEST_TRANSACTION)
        assert amqp_mock.call_count == 1


@patch('uuid.uuid4', MagicMock(return_value=TEST_TRANSACTION))
def test_post_call_end_with_source_phone_number(client, call_end_record):
    call_end_record['source'] = '1127227777'
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        response = client.post('/v1/call', json=call_end_record)
        assert response.status_code == 400
        response_error = response.get_json()
        assert response_error['transaction_id'] == str(TEST_TRANSACTION)
        assert not amqp_mock.called


def remove_field(field):
    def f(call_record):
        del call_record[field]
        return field
    return f

@pytest.mark.parametrize('remove_field_fn', [
        remove_field('id'),
        remove_field('type'),
        remove_field('timestamp'),
        remove_field('call_id')
    ])
def test_post_call_record_with_no_required_fields(client, call_end_record, remove_field_fn):
    with patch.object(BillingAPIProducer, 'publish') as amqp_mock:
        field_removed = remove_field_fn(call_end_record)
        response = client.post('/v1/call', json=call_end_record)
        assert response.status_code == 400
        response_error = response.get_json()
        assert field_removed in response_error['detail']
        assert not amqp_mock.called
