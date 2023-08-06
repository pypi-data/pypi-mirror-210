# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio administration marshmallow utils module."""

from invenio_vocabularies.services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    VocabularyRelationSchema,
)
from marshmallow import fields
from marshmallow_utils import fields as invenio_fields

vocabulary_schemas = [ContribVocabularyRelationSchema, BaseVocabularySchema,
                      VocabularyRelationSchema]

custom_mapping = {
    # marshmallow
    fields.Str: "string",
    fields.Integer: "integer",
    fields.List: "array",
    fields.Dict: "object",
    fields.Url: "string",
    fields.String: "string",
    fields.DateTime: "datetime",
    fields.Float: "float",
    fields.Boolean: "bool",
    fields.Raw: "dict",
    fields.UUID: "uuid",
    fields.Time: "time",
    fields.Date: "date",
    fields.TimeDelta: "timedelta",
    fields.Decimal: "decimal",
    # invenio fields
    invenio_fields.SanitizedUnicode: "string",
    invenio_fields.links.Links: "array",
    invenio_fields.links.Link: "string",
    invenio_fields.tzdatetime.TZDateTime: "datetime",
    invenio_fields.sanitizedhtml.SanitizedHTML: "string",
}


def jsonify_schema(schema):
    """Marshmallow schema to dict."""
    schema_dict = {}

    for field, field_type in schema.fields.items():
        is_links = isinstance(field_type, invenio_fields.links.Links)

        if is_links:
            continue

        is_read_only = field_type.dump_only
        is_create_only = field_type.metadata["create_only"] \
            if "create_only" in field_type.metadata else False

        field_type_name = field_type.__class__
        is_required = field_type.required

        nested_field = isinstance(field_type, fields.Nested)
        list_field = isinstance(field_type, fields.List)

        schema_dict[field] = {
            "required": is_required,
            "readOnly": is_read_only,
            "title": field_type.metadata[
                "title"] if "title" in field_type.metadata else None,
            "createOnly": is_create_only,
            "metadata": field_type.metadata
        }

        if nested_field:
            if any([isinstance(field_type.schema, x) for x in vocabulary_schemas]):
                schema_type = "vocabulary"
            else:
                schema_type = "object"

            schema_dict[field].update({
                "type": schema_type,
                "properties": jsonify_schema(field_type.schema),
            })
        elif list_field and isinstance(field_type.inner, fields.Nested):
            # list of objects (vocabularies or nested)
            schema_dict[field].update({
                "type": "array",
                "items": {"type": "object",
                          "properties": jsonify_schema(field_type.inner.schema)},
            })
        elif list_field and not isinstance(field_type.inner, fields.Nested):
            # list of plain types
            schema_dict[field].update({
                "type": "array",
                "items": {"type": custom_mapping[field_type.inner]},
            })
        else:
            try:
                schema_dict[field].update({
                    "type": custom_mapping[field_type_name],
                })
            except KeyError:
                raise Exception(f"Unrecognised schema field {field}: {field_type_name}")
    return schema_dict
