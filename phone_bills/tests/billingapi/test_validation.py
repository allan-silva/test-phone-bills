from phone_bills.billingapi.validation import validate_call_record


def test_validation_success_call_start(call_start_record):
    validation_result = validate_call_record(call_start_record)
    assert validation_result.is_valid
    assert len(validation_result.messages) == 0
    assert not validation_result.message


def test_validation_missing_source_destination_call_start(call_start_record):
    del call_start_record['source']
    del call_start_record['destination']
    validation_result = validate_call_record(call_start_record)
    assert not validation_result.is_valid
    assert len(validation_result.messages) == 2
    assert validation_result.message


def test_validation_source_destination_are_equals_call_start(call_start_record):
    call_start_record['source'] = call_start_record['destination']
    validation_result = validate_call_record(call_start_record)
    assert not validation_result.is_valid
    assert len(validation_result.messages) == 1
    assert validation_result.message


def test_validation_success_call_end(call_end_record):
    validation_result = validate_call_record(call_end_record)
    assert validation_result.is_valid
    assert len(validation_result.messages) == 0
    assert not validation_result.message


def test_validation_invalid_fields_call_end(call_start_record):
    call_start_record['type'] = 'end'
    validation_result = validate_call_record(call_start_record)
    assert not validation_result.is_valid
    assert len(validation_result.messages) == 2
    assert validation_result.message


def test_validation_invalid_type(call_end_record):
    call_end_record['type'] = 'the-wall'
    validation_result = validate_call_record(call_end_record)
    assert not validation_result.is_valid
    assert len(validation_result.messages) == 1
    assert validation_result.message
