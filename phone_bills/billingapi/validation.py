class ValidationResult:
    def __init__(self):
        self.messages = []

    def add_msg(self, msg):
        self.messages.append(msg)

    @property
    def is_valid(self):
        return not self.messages

    @property
    def message(self):
        return '\n'.join(self.messages)


def validate_call_record(call_record):
    validation_result = ValidationResult()
    if is_call_start(call_record):
        if not is_field_present('source', call_record):
            validation_result.add_msg('Source field is not present.')
        if not is_field_present('destination', call_record):
            validation_result.add_msg('Destination field is not present.')
        if not validation_result.is_valid:
            return validation_result
        if is_source_equals_destination(call_record):
            validation_result.add_msg('Source and Destination are the same.')
    elif is_call_end(call_record):
        if is_field_present('source', call_record):
            validation_result.add_msg('Source is a invalid field for a end-call event.')
        if is_field_present('destination', call_record):
            validation_result.add_msg('Destination is a invalid field for a end-call event.')
    else:
        validation_result.add_msg(f'{call_record["type"]} - Invalid call event')
    return validation_result


def is_source_equals_destination(call_record):
    return call_record['source'] == call_record['destination']


def is_field_present(field, call_record):
    return field in call_record


def is_call_start(call_record):
    return call_record['type'] == 'start'


def is_call_end(call_record):
    return call_record['type'] == 'end'
