from enum import IntEnum


class Validator(object):

    def validate(self, json_object):
        results = ValidationResults()

        if "$schemaRef" not in json_object:
            results.add(ValidationSeverity.FATAL, JsonValidationException("No $schemaRef found, unable to validate."))

        return results


class ValidationSeverity(IntEnum):
    OK = 0,
    WARN = 1,
    ERROR = 2,
    FATAL = 3


class ValidationResults(object):

    severity = ValidationSeverity.OK
    messages = []

    def add(self, severity, exception):
        self.severity = max(severity, self.severity)
        self.messages.append(exception)


class JsonValidationException(Exception):
    pass
