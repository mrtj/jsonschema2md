"""Test jsonschema2md."""


import jsonschema2md


class TestParser:
    test_schema = {
        "$id": "https://example.com/arrays.schema.json",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "description": "Vegetable preferences",
        "type": "object",
        "properties": {
            "fruits": {"type": "array", "items": {"type": "string"}},
            "vegetables": {"type": "array", "items": {"$ref": "#/definitions/veggie"}},
        },
        "definitions": {
            "veggie": {
                "type": "object",
                "required": ["veggieName", "veggieLike"],
                "properties": {
                    "veggieName": {
                        "type": "string",
                        "description": "The name of the vegetable.",
                    },
                    "veggieLike": {
                        "type": "boolean",
                        "description": "Do I like this vegetable?",
                    },
                },
            }
        },
        "examples": [
            {
                "fruits": ["apple", "orange"],
                "vegetables": [{"veggieName": "cabbage", "veggieLike": True}]
            }
        ],
    }

    def test_construct_description_line(self):
        test_cases = [
            {
                "input": {},
                "add_type": False,
                "expected_output": ""
            },
            {
                "input": {
                    "description": "The name of the vegetable.",
                },
                "add_type": False,
                "expected_output": ": The name of the vegetable."
            },
            {
                "input": {
                    "description": "The name of the vegetable.",
                    "default": "eggplant",
                    "type": "string",
                    "$ref": "#/definitions/veggies",
                    "enum": ["eggplant", "spinach", "cabbage"]
                },
                "add_type": True,
                "expected_output": (
                    ": The name of the vegetable. Must be of type *string*. "
                    "Must be one of: `['eggplant', 'spinach', 'cabbage']`. "
                    "Refer to *#/definitions/veggies*. "
                    "Default: `eggplant`."
                )
            },
            {
                "input": {
                    "description": "Number of vegetables",
                    "default": 0,
                    "type": "number",
                    "minimum": 0,
                    "maximum": 999,
                    "additionalProperties": True,
                },
                "add_type": False,
                "expected_output": (
                    ": Number of vegetables. Minimum: `0`. Maximum: `999`. "
                    "Can contain additional properties. Default: `0`."
                )
            },
            {
                "input": {
                    "description": "List of vegetables",
                    "default": [],
                    "type": "array",
                    "additionalProperties": False,
                },
                "add_type": False,
                "expected_output": (
                    ": List of vegetables. Cannot contain additional properties. "
                    "Default: `[]`."
                )
            }
        ]

        parser = jsonschema2md.Parser()

        for case in test_cases:
            observed_output = " ".join(parser._construct_description_line(
                case["input"], add_type=case["add_type"]
            ))
            assert case["expected_output"] == observed_output

    def test_parse_object(self):
        parser = jsonschema2md.Parser()
        expected_output = [
            '- **`fruits`** *(array)*\n',
            '  - **Items** *(string)*\n'
        ]
        assert expected_output == parser._parse_object(
            self.test_schema["properties"]["fruits"],
            "fruits"
        )

    def test_parse_schema(self):
        parser = jsonschema2md.Parser()
        expected_output = [
            '# JSON Schema\n\n',
            '*Vegetable preferences*\n\n',
            '## Properties\n\n',
            '- **`fruits`** *(array)*\n',
            '  - **Items** *(string)*\n',
            '- **`vegetables`** *(array)*\n',
            '  - **Items**: Refer to *#/definitions/veggie*.\n',
            '## Definitions\n\n',
            '- **`veggie`** *(object)*\n',
            '  - **`veggieName`** *(string)*: The name of the vegetable.\n',
            '  - **`veggieLike`** *(boolean)*: Do I like this vegetable?\n',
            '## Examples\n\n',
            '  ```json\n'
            '  {\n'
            '      "fruits": [\n'
            '          "apple",\n'
            '          "orange"\n'
            '      ],\n'
            '      "vegetables": [\n'
            '          {\n'
            '              "veggieName": "cabbage",\n'
            '              "veggieLike": true\n'
            '          }\n'
            '      ]\n'
            '  }\n'
            '  ```\n'
        ]
        assert expected_output == parser.parse_schema(self.test_schema)
        