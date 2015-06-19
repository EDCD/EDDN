# coding: utf8

import simplejson
from enum import IntEnum
from jsonschema import validate as jsValidate, ValidationError


class Validator(object):

    schemas = {}	# { schemaRef: schema_dict }. schema_dict is None if the schemaRef is recognised but unsupported.

    def addSchemaResource(self, schemaRef, schema):
        if schemaRef in self.schemas.keys():
            raise Exception("Attempted to redefine schema for " + schemaRef)
        if schema:
            schema = simplejson.loads(schema)
        self.schemas[schemaRef] = schema

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
        if not schema:
            results.add(ValidationSeverity.RETIRED, JsonValidationException("Schema " + schemaRef + " is retired, please upgrade your client."))
        else:
            try:
                jsValidate(json_object, schema)
            except ValidationError as e:
                results.add(ValidationSeverity.ERROR, e)

        return results


class ValidationSeverity(IntEnum):
    OK, WARN, RETIRED, ERROR, FATAL = range(5)


class ValidationResults(object):

    def __init__(self):
        self.severity = ValidationSeverity.OK
        self.messages = []

    def add(self, severity, exception):
        self.severity = max(severity, self.severity)
        self.messages.append(exception)


class JsonValidationException(Exception):
    pass
