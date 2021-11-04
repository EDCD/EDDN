# coding: utf8
"""Handle validating incoming messages against the schemas."""

from enum import IntEnum

import simplejson
from jsonschema import FormatChecker, ValidationError
from jsonschema import validate as jsValidate


class Validator(object):

    schemas = {"http://example.com": {}}

    def addSchemaResource(self, schemaRef, schema):
        if schemaRef in self.schemas.keys():
            raise Exception("Attempted to redefine schema for " + schemaRef)
        try:
            schema = simplejson.loads(schema)
            self.schemas[schemaRef] = schema

        except simplejson.errors.JSONDecodeError as e:
            raise Exception('SCHEMA: Failed to load: ' + schemaRef)

    def validate(self, json_object):
        results = ValidationResults()

        if "$schemaRef" not in json_object:
            results.add(ValidationSeverity.FATAL, JsonValidationException("No $schemaRef found, unable to validate."))
            return results

        schemaRef = json_object["$schemaRef"]
        if schemaRef not in self.schemas.keys():
            #  We don't want to go out to the Internet and retrieve unknown schemas.
            results.add(ValidationSeverity.FATAL, JsonValidationException("Schema " + schemaRef + " is unknown, unable to validate."))
            return results

        schema = self.schemas[schemaRef]
        try:
            jsValidate(json_object, schema, format_checker=FormatChecker())
        except ValidationError as e:
            results.add(ValidationSeverity.ERROR, e)

        return results


class ValidationSeverity(IntEnum):
    OK = 0,
    WARN = 1,
    ERROR = 2,
    FATAL = 3


class ValidationResults(object):

    def __init__(self):
        self.severity = ValidationSeverity.OK
        self.messages = []

    def add(self, severity, exception):
        self.severity = max(severity, self.severity)
        self.messages.append(exception)


class JsonValidationException(Exception):
    pass
