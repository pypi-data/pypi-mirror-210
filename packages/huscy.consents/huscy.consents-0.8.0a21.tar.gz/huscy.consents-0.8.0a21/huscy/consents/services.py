import jsonschema

from huscy.consents.models import Consent, ConsentCategory, ConsentFile


CHECKBOX = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'checkbox'.",
            "type": "string",
            "pattern": "checkbox",
        },
        "is_mandatory": {
            "description": "This field indicates whether this text fragment is mandatory.",
            "type": "boolean",
        },
        "properties": {
            "description": "The checkbox has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text of the "
                                    "checkbox."),
                    "type": "string",
                },
                "required": {
                    "description": ("This property indicates whether checking the checkbox "
                                    "is mandatory."),
                    "type": "boolean",
                },
            },
            "required": ["text", "required"],
        },
    },
    "required": ["properties", "type"],
}


HEADING = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'heading'.",
            "type": "string",
            "pattern": "heading",
        },
        "is_mandatory": {
            "description": "This field indicates whether this text fragment is mandatory.",
            "type": "boolean",
        },
        "properties": {
            "description": "The heading has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text of the "
                                    "heading."),
                    "type": "string",
                },
                "size": {
                    "description": "This property specifies the size of the heading.",
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5,
                },
            },
            "required": ["text", "size"],
        },
    },
    "required": ["properties", "type"],
}


MARKDOWN = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'markdown'",
            "type": "string",
            "pattern": "markdown",
        },
        "properties": {
            "description": "The markdown text has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text as "
                                    "markdown text"),
                    "type": "string",
                },
            },
            "required": ["text"],
        },
    },
    "required": ["properties", "type"],
}


PAGE_BREAK = {
    "type": "object",
    "properties": {
        "type": {
            "description": "Should force the renderer to add a page break",
            "type": "string",
            "pattern": "page-break",
        },
        "properties": {
            "description": "This node has no properties.",
            "type": "object",
            "properties": {},
        },
    },
    "required": ["type"],
}


PARAGRAPH = {
    "type": "object",
    "properties": {
        "type": {
            "description": "The type must be 'paragraph'.",
            "type": "string",
            "pattern": "paragraph",
        },
        "is_mandatory": {
            "description": "This field indicates whether this text fragment is mandatory.",
            "type": "boolean",
        },
        "properties": {
            "decsription": "The paragraph has the following properties.",
            "type": "object",
            "properties": {
                "text": {
                    "description": ("This property contains the displayed text of the "
                                    "checkbox."),
                    "type": "string",
                },
                "boldface": {
                    "description": ("This property indicates whether the displayed text "
                                    "will be printed in bold type."),
                    "type": "boolean",
                },
            },
            "required": ["text", "boldface"],
        },
    },
    "required": ["properties", "type"],
}


TEXT_FRAGMENTS_SCHEMA = {
    "$defs": {
        "checkbox": CHECKBOX,
        "heading": HEADING,
        "markdown": MARKDOWN,
        "page-break": PAGE_BREAK,
        "paragraph": PARAGRAPH,
    },

    "type": "array",
    "items": {
        "anyOf": [
            {"$ref": "#/$defs/checkbox"},
            {"$ref": "#/$defs/heading"},
            {"$ref": "#/$defs/markdown"},
            {"$ref": "#/$defs/page-break"},
            {"$ref": "#/$defs/paragraph"},
        ],
    },
    "minItems": 1,
}


def create_consent_category(name, template_text_fragments):
    jsonschema.validate(template_text_fragments, TEXT_FRAGMENTS_SCHEMA)
    return ConsentCategory.objects.create(
        name=name,
        template_text_fragments=template_text_fragments,
    )


def create_consent(name, text_fragments):
    jsonschema.validate(text_fragments, TEXT_FRAGMENTS_SCHEMA)
    return Consent.objects.create(name=name, text_fragments=text_fragments)


def create_consent_file(consent, filehandle):
    return ConsentFile.objects.create(
        consent=consent,
        consent_version=consent.version,
        filehandle=filehandle,
    )


def update_consent_category(consent_category, name=None, template_text_fragments=None):
    update_fields = []

    if name is not None and name != consent_category.name:
        consent_category.name = name
        update_fields.append('name')

    if (template_text_fragments is not None
            and template_text_fragments != consent_category.template_text_fragments):
        jsonschema.validate(template_text_fragments, TEXT_FRAGMENTS_SCHEMA)
        consent_category.template_text_fragments = template_text_fragments
        update_fields.append('template_text_fragments')

    consent_category.save(update_fields=update_fields)

    return consent_category


def update_consent(consent, name=None, text_fragments=None):
    update_fields = []

    if name is not None and name != consent.name:
        consent.name = name
        update_fields.append('name')

    if text_fragments is not None and text_fragments != consent.text_fragments:
        jsonschema.validate(text_fragments, TEXT_FRAGMENTS_SCHEMA)
        consent.text_fragments = text_fragments
        update_fields.append('text_fragments')

    if update_fields:
        consent.version += 1
        update_fields.append('version')
        consent.save(update_fields=update_fields)

    return consent
