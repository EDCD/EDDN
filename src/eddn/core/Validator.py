# coding: utf8
"""Handle validating incoming messages against the schemas."""

from enum import IntEnum
from typing import Dict, List

import simplejson
from jsonschema import FormatChecker, ValidationError
from jsonschema import validate as json_validate


class ValidationSeverity(IntEnum):
    """Enum of validation status."""

    OK = 0,
    WARN = 1,
    ERROR = 2,
    FATAL = 3


class JsonValidationException(Exception):
    """Exception for JSON Validation errors."""

    pass


class ValidationResults(object):
    """Validation results."""

    def __init__(self) -> None:
        self.severity = ValidationSeverity.OK
        self.messages: List[JsonValidationException] = []

    def add(self, severity: ValidationSeverity, exception: JsonValidationException) -> None:
        """
        Add a validation failure to the results.

        :param severity:
        :param exception:
        :return:
        """
        self.severity = max(severity, self.severity)
        self.messages.append(exception)


class Validator(object):
    """Perform validation on incoming messages."""

    schemas: Dict = {"http://example.com": {}}

    def add_schema_resource(self, schema_ref, schema) -> None:
        """
        Add the given schema to the list to validate against.

        :param schema_ref: Schema URL.
        :param schema: The schema
        """
        if schema_ref in self.schemas.keys():
            raise Exception("Attempted to redefine schema for " + schema_ref)

        try:
            schema = simplejson.loads(schema)
            self.schemas[schema_ref] = schema

        except simplejson.JSONDecodeError:
            raise Exception(f'SCHEMA: Failed to load: {schema_ref}')

    def validate(self, json_object: Dict) -> ValidationResults:
        """
        Validate the given message.

        :param json_object: The message to be validated.
        :return: The results of validation.
        """
        results = ValidationResults()

        if "$schemaRef" not in json_object:
            results.add(ValidationSeverity.FATAL, JsonValidationException("No $schemaRef found, unable to validate."))
            return results

        schema_ref = json_object["$schemaRef"]
        if schema_ref not in self.schemas.keys():
            #  We don't want to go out to the Internet and retrieve unknown schemas.
            results.add(
                ValidationSeverity.FATAL,
                JsonValidationException(f'Schema {schema_ref} is unknown, unable to validate.')
            )
            return results

        schema = self.schemas[schema_ref]
        try:
            json_validate(json_object, schema, format_checker=FormatChecker())

        except ValidationError as e:
            results.add(ValidationSeverity.ERROR, e)

        return results
