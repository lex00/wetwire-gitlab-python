"""Component code generation for wetwire-gitlab.

This module generates typed Python wrappers for GitLab CI/CD components
using Jinja2 templates.
"""

from pathlib import Path

from jinja2 import Template

from .parse import ComponentIR, ParsedSchemas

# Template for component class
COMPONENT_CLASS_TEMPLATE = Template('''"""{{ component.name }} component wrapper.

Auto-generated wrapper for gitlab.com/components/{{ component.name }}
"""

from dataclasses import dataclass


@dataclass
class {{ class_name }}:
    """{{ class_name }} component configuration.

    GitLab CI/CD component wrapper for {{ component.name }}.
    """

{% for input in component.inputs %}
    {{ input.name }}: str{% if input.default is not none %} = "{{ input.default }}"{% endif %}
    """{{ input.description or input.name }}"""
{% endfor %}

    def to_include(self) -> dict:
        """Generate include configuration for this component.

        Returns:
            Dictionary with component include configuration.
        """
        inputs = {}
{% for input in component.inputs %}
        if self.{{ input.name }}{% if input.default is not none %} != "{{ input.default }}"{% endif %}:
            inputs["{{ input.name }}"] = self.{{ input.name }}
{% endfor %}

        result = {
            "component": "gitlab.com/components/{{ component.name }}@main",
        }
        if inputs:
            result["inputs"] = inputs
        return result
''')

# Template for module __init__.py
INIT_TEMPLATE = Template('''"""Generated component wrappers for GitLab CI/CD components."""

{% for component in components %}
from .{{ module_names[component] }} import {{ class_names[component] }}
{% endfor %}

__all__ = [
{% for component in components %}
    "{{ class_names[component] }}",
{% endfor %}
]
''')


def component_to_class_name(name: str) -> str:
    """Convert component name to Python class name.

    Args:
        name: Component name (e.g., "secret-detection").

    Returns:
        Class name (e.g., "SecretDetection").
    """
    # Handle special cases for acronyms
    upper_words = {"sast", "dast"}

    # Split on hyphens and underscores
    parts = name.replace("-", "_").split("_")

    result_parts = []
    for part in parts:
        if part.lower() in upper_words:
            result_parts.append(part.upper())
        else:
            result_parts.append(part.capitalize())

    return "".join(result_parts)


def component_to_module_name(name: str) -> str:
    """Convert component name to Python module name.

    Args:
        name: Component name (e.g., "secret-detection").

    Returns:
        Module name (e.g., "secret_detection").
    """
    return name.replace("-", "_")


def generate_component_code(component: ComponentIR) -> str:
    """Generate Python code for a component wrapper.

    Args:
        component: Parsed component specification.

    Returns:
        Generated Python code as string.
    """
    class_name = component_to_class_name(component.name)

    return COMPONENT_CLASS_TEMPLATE.render(
        component=component,
        class_name=class_name,
    )


def generate_component_module(component: ComponentIR) -> str:
    """Generate a complete Python module for a component.

    Args:
        component: Parsed component specification.

    Returns:
        Generated Python module code as string.
    """
    return generate_component_code(component)


def generate_component_module_file(component: ComponentIR, output_path: Path) -> None:
    """Generate a component module and write to file.

    Args:
        component: Parsed component specification.
        output_path: Path to write the module file.
    """
    code = generate_component_module(component)
    output_path.write_text(code)


def generate_init_file(components: list[str], output_dir: Path) -> None:
    """Generate __init__.py for components package.

    Args:
        components: List of component names.
        output_dir: Directory to write __init__.py.
    """
    class_names = {c: component_to_class_name(c) for c in components}
    module_names = {c: component_to_module_name(c) for c in components}

    code = INIT_TEMPLATE.render(
        components=sorted(components),
        class_names=class_names,
        module_names=module_names,
    )

    (output_dir / "__init__.py").write_text(code)


def generate_all_components(
    schemas: ParsedSchemas,
    output_dir: Path,
) -> dict[str, bool]:
    """Generate all component wrappers from parsed schemas.

    Args:
        schemas: Parsed schemas containing component specifications.
        output_dir: Directory to write generated files.

    Returns:
        Dictionary of component names to generation success status.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, bool] = {}
    generated_components: list[str] = []

    for name, component in schemas.components.items():
        try:
            module_name = component_to_module_name(name)
            output_path = output_dir / f"{module_name}.py"
            generate_component_module_file(component, output_path)
            result[name] = True
            generated_components.append(name)
        except Exception:
            result[name] = False

    # Generate __init__.py
    if generated_components:
        generate_init_file(generated_components, output_dir)

    return result
