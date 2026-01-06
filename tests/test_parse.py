"""Tests for schema parsing module."""

import json
import tempfile
from pathlib import Path


class TestCISchemaParser:
    """Tests for CI schema parser."""

    def test_parse_ci_schema(self):
        """Parse CI schema extracts job properties."""
        from wetwire_gitlab.codegen.parse import parse_ci_schema

        # Minimal CI schema structure
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {
                "job": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "array"},
                        "stage": {"type": "string"},
                        "image": {"type": "string"},
                    },
                },
            },
        }

        result = parse_ci_schema(schema)
        assert "job" in result.definitions
        assert "script" in result.definitions["job"].properties

    def test_parse_ci_schema_from_file(self):
        """Parse CI schema from file."""
        from wetwire_gitlab.codegen.parse import parse_ci_schema_file

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "definitions": {
                "job": {
                    "type": "object",
                    "properties": {
                        "script": {"type": "array"},
                    },
                },
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(schema, f)
            f.flush()

            result = parse_ci_schema_file(Path(f.name))
            assert "job" in result.definitions


class TestComponentSpecParser:
    """Tests for component spec parser."""

    def test_parse_component_spec(self):
        """Parse component spec extracts inputs."""
        from wetwire_gitlab.codegen.parse import parse_component_spec

        spec_content = """
spec:
  inputs:
    stage:
      default: test
      description: The stage to run the job in
    SAST_EXCLUDED_PATHS:
      default: ""
      description: Paths to exclude from scanning
"""

        result = parse_component_spec(spec_content)
        assert len(result.inputs) == 2
        assert "stage" in [i.name for i in result.inputs]

    def test_parse_component_spec_from_file(self):
        """Parse component spec from file."""
        from wetwire_gitlab.codegen.parse import parse_component_spec_file

        spec_content = """
spec:
  inputs:
    stage:
      default: test
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(spec_content)
            f.flush()

            result = parse_component_spec_file(Path(f.name))
            assert len(result.inputs) == 1


class TestIntermediateRepresentation:
    """Tests for IR dataclasses."""

    def test_schema_ir_creation(self):
        """SchemaIR can be created."""
        from wetwire_gitlab.codegen.parse import (
            PropertyIR,
            SchemaDefinitionIR,
            SchemaIR,
        )

        schema_ir = SchemaIR(
            definitions={
                "job": SchemaDefinitionIR(
                    name="job",
                    type_="object",
                    properties={
                        "script": PropertyIR(name="script", type_="array"),
                    },
                ),
            },
        )

        assert schema_ir.definitions["job"].name == "job"
        assert schema_ir.definitions["job"].properties["script"].type_ == "array"

    def test_component_ir_creation(self):
        """ComponentIR can be created."""
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component_ir = ComponentIR(
            name="sast",
            inputs=[
                InputIR(name="stage", default="test", description="Stage name"),
            ],
        )

        assert component_ir.name == "sast"
        assert len(component_ir.inputs) == 1
        assert component_ir.inputs[0].name == "stage"

    def test_input_ir_optional(self):
        """InputIR handles optional inputs."""
        from wetwire_gitlab.codegen.parse import InputIR

        # Input with default is optional
        optional_input = InputIR(name="stage", default="test")
        assert optional_input.is_optional is True

        # Input without default is required
        required_input = InputIR(name="stage", default=None)
        assert required_input.is_optional is False


class TestParseAll:
    """Tests for parsing all schemas."""

    def test_parse_all_schemas(self):
        """Parse all schemas in specs directory."""
        from wetwire_gitlab.codegen.parse import parse_all_schemas

        with tempfile.TemporaryDirectory() as tmpdir:
            specs_dir = Path(tmpdir)
            components_dir = specs_dir / "components"
            components_dir.mkdir()

            # Create CI schema
            ci_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "definitions": {
                    "job": {
                        "type": "object",
                        "properties": {"script": {"type": "array"}},
                    },
                },
            }
            with open(specs_dir / "ci-schema.json", "w") as f:
                json.dump(ci_schema, f)

            # Create component spec
            with open(components_dir / "sast.yml", "w") as f:
                f.write("spec:\n  inputs:\n    stage:\n      default: test\n")

            result = parse_all_schemas(specs_dir)

            assert result.ci_schema is not None
            assert "sast" in result.components
