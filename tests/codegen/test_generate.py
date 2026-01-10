"""Tests for component code generation module."""

import tempfile
from pathlib import Path


class TestGenerateComponent:
    """Tests for generating component wrapper code."""

    def test_generate_component_class(self):
        """Generate a component class from ComponentIR."""
        from wetwire_gitlab.codegen.generate import generate_component_code
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component = ComponentIR(
            name="sast",
            inputs=[
                InputIR(name="stage", default="test", description="The stage to run"),
                InputIR(
                    name="SAST_EXCLUDED_PATHS",
                    default="",
                    description="Paths to exclude",
                ),
            ],
        )

        code = generate_component_code(component)

        assert "class SAST" in code
        assert "stage" in code
        assert "SAST_EXCLUDED_PATHS" in code
        assert "dataclass" in code

    def test_generate_component_with_required_input(self):
        """Generate component with required (no default) input."""
        from wetwire_gitlab.codegen.generate import generate_component_code
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component = ComponentIR(
            name="custom",
            inputs=[
                InputIR(name="required_param", default=None, description="Required"),
                InputIR(
                    name="optional_param",
                    default="default_value",
                    description="Optional",
                ),
            ],
        )

        code = generate_component_code(component)

        # Required param should not have default
        assert "required_param: str" in code
        # Optional param should have default
        assert (
            'optional_param: str = "default_value"' in code
            or "optional_param: str | None" in code
        )

    def test_generate_component_valid_python(self):
        """Generated code is valid Python."""
        from wetwire_gitlab.codegen.generate import generate_component_code
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component = ComponentIR(
            name="test",
            inputs=[InputIR(name="stage", default="test")],
        )

        code = generate_component_code(component)

        # Should compile without errors
        compile(code, "<string>", "exec")


class TestGenerateModule:
    """Tests for generating component module files."""

    def test_generate_component_module(self):
        """Generate a complete module file."""
        from wetwire_gitlab.codegen.generate import generate_component_module
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component = ComponentIR(
            name="sast",
            inputs=[InputIR(name="stage", default="test")],
        )

        code = generate_component_module(component)

        assert '"""' in code  # Has docstring
        assert "from dataclasses import dataclass" in code
        assert "class SAST" in code

    def test_generate_component_module_to_file(self):
        """Generate module and write to file."""
        from wetwire_gitlab.codegen.generate import generate_component_module_file
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR

        component = ComponentIR(
            name="sast",
            inputs=[InputIR(name="stage", default="test")],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "sast.py"
            generate_component_module_file(component, output_path)

            assert output_path.exists()
            content = output_path.read_text()
            assert "class SAST" in content


class TestGenerateAllComponents:
    """Tests for generating all component wrappers."""

    def test_generate_all_components(self):
        """Generate all component modules from ParsedSchemas."""
        from wetwire_gitlab.codegen.generate import generate_all_components
        from wetwire_gitlab.codegen.parse import ComponentIR, InputIR, ParsedSchemas

        schemas = ParsedSchemas(
            ci_schema=None,
            components={
                "sast": ComponentIR(
                    name="sast",
                    inputs=[InputIR(name="stage", default="test")],
                ),
                "dast": ComponentIR(
                    name="dast",
                    inputs=[InputIR(name="stage", default="dast")],
                ),
            },
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            result = generate_all_components(schemas, output_dir)

            assert len(result) == 2
            assert (output_dir / "sast.py").exists()
            assert (output_dir / "dast.py").exists()
            assert (output_dir / "__init__.py").exists()

    def test_generate_init_file(self):
        """Generate __init__.py with imports."""
        from wetwire_gitlab.codegen.generate import generate_init_file

        components = ["sast", "dast", "secret_detection"]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            generate_init_file(components, output_dir)

            init_path = output_dir / "__init__.py"
            assert init_path.exists()

            content = init_path.read_text()
            assert "from .sast import SAST" in content
            assert "from .dast import DAST" in content
            assert "from .secret_detection import SecretDetection" in content


class TestNameConversion:
    """Tests for name conversion utilities."""

    def test_component_to_class_name(self):
        """Convert component name to class name."""
        from wetwire_gitlab.codegen.generate import component_to_class_name

        assert component_to_class_name("sast") == "SAST"
        assert component_to_class_name("dast") == "DAST"
        assert component_to_class_name("secret-detection") == "SecretDetection"
        assert component_to_class_name("dependency_scanning") == "DependencyScanning"
        assert component_to_class_name("coverage-report") == "CoverageReport"

    def test_component_to_module_name(self):
        """Convert component name to module name."""
        from wetwire_gitlab.codegen.generate import component_to_module_name

        assert component_to_module_name("sast") == "sast"
        assert component_to_module_name("secret-detection") == "secret_detection"
        assert component_to_module_name("dependency-scanning") == "dependency_scanning"
