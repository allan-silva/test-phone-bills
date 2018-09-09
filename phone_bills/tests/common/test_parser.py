import pytest

from datetime import datetime
from phone_bills.billingcommon.parser import CallRecordParser


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


@pytest.fixture
def parser():
    return CallRecordParser()


def assert_call_fields(call_event):
    assert 'call_id' in call_event
    assert call_event['call_id'] == 71
    assert 'external_id' in call_event
    assert 'type' in call_event
    assert 'timestamp' in call_event


def assert_call_start_fields(call_event):
    assert_call_fields(call_event)
    assert 'source_area_code' in call_event
    assert 'source' in call_event
    assert 'destination_area_code' in call_event
    assert 'destination' in call_event


def test_parse_call_start(parser, call_start_record):
    call_event = parser.parse(call_start_record)
    assert_call_start_fields(call_event)
    call_event['external_id'] = 42
    call_event['type'] = 'start'
    call_event['timestamp'] = datetime(2017, 12, 12, 15, 7, 13)
    call_event['source_area_code'] = '99'
    call_event['source'] = '988526423'
    call_event['destination_area_code'] = '99'
    call_event['destination'] = '93468278'


def test_parse_call_end(parser, call_end_record):
    call_end_record['timestamp'] = datetime(2018, 1, 25)
    call_event = parser.parse(call_end_record)
    assert_call_fields(call_event)
    call_event['external_id'] = 442
    call_event['type'] = 'end'
    call_event['timestamp'] = datetime(2017, 12, 12, 15, 14, 56)


@pytest.mark.parametrize('phone_number', [
    '',
    '112722777',
    '112722777712',
    '1127227A77',
    '112A2277771'])
def test_parse_phone_format_error(parser, call_start_record, phone_number):
    with pytest.raises(ValueError):
        call_start_record['source'] = phone_number
        parser.parse(call_start_record)
