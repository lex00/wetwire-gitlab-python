"""Comprehensive import testing against a corpus of GitLab CI templates.

This module tests the import functionality by:
1. Importing each template from tests/fixtures/templates/
2. Running round-trip tests: YAML -> parse -> build -> compare
3. Tracking coverage of GitLab CI features
4. Reporting success rates and feature support
"""

from pathlib import Path

import pytest

from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci
from wetwire_gitlab.serialize import build_pipeline_yaml
from wetwire_gitlab.testing import compare_yaml_semantic

# Template fixture directory
TEMPLATES_DIR = Path(__file__).parent.parent / "fixtures" / "templates"


def get_all_templates() -> list[Path]:
    """Get all YAML template files from the fixtures directory."""
    if not TEMPLATES_DIR.exists():
        return []
    return sorted(TEMPLATES_DIR.glob("*.yml"))


def extract_features(yaml_content: str) -> set[str]:
    """Extract GitLab CI features present in a YAML template.

    Returns a set of feature names found in the YAML.
    """
    features = set()

    # Parse as dict to check for top-level keys
    import yaml
    try:
        data = yaml.safe_load(yaml_content)
        if not data:
            return features

        # Top-level features
        if "stages" in data:
            features.add("stages")
        if "variables" in data:
            features.add("variables")
        if "include" in data:
            features.add("include")
        if "default" in data:
            features.add("default")
        if "cache" in data:
            features.add("cache")
        if "services" in data:
            features.add("services")

        # Job-level features
        for key, value in data.items():
            if isinstance(value, dict) and "script" in value:
                # This is a job
                if "stage" in value:
                    features.add("job.stage")
                if "image" in value:
                    features.add("job.image")
                if "artifacts" in value:
                    features.add("job.artifacts")
                if "cache" in value:
                    features.add("job.cache")
                if "rules" in value:
                    features.add("job.rules")
                if "needs" in value:
                    features.add("job.needs")
                if "dependencies" in value:
                    features.add("job.dependencies")
                if "environment" in value:
                    features.add("job.environment")
                if "parallel" in value:
                    features.add("job.parallel")
                if "tags" in value:
                    features.add("job.tags")
                if "retry" in value:
                    features.add("job.retry")
                if "timeout" in value:
                    features.add("job.timeout")
                if "allow_failure" in value:
                    features.add("job.allow_failure")
                if "before_script" in value:
                    features.add("job.before_script")
                if "after_script" in value:
                    features.add("job.after_script")
                if "coverage" in value:
                    features.add("job.coverage")
                if "trigger" in value:
                    features.add("job.trigger")
                if "interruptible" in value:
                    features.add("job.interruptible")

    except Exception:
        pass

    return features


class TestTemplateImport:
    """Test basic import functionality for all templates."""

    @pytest.mark.parametrize("template_path", get_all_templates(), ids=lambda p: p.name)
    def test_template_parses_successfully(self, template_path: Path):
        """Each template should parse without errors."""
        yaml_content = template_path.read_text()

        # Should not raise
        pipeline = parse_gitlab_ci(yaml_content)

        # Basic validation
        assert pipeline is not None
        assert isinstance(pipeline.stages, list)
        assert isinstance(pipeline.jobs, list)

    @pytest.mark.parametrize("template_path", get_all_templates(), ids=lambda p: p.name)
    def test_template_generates_valid_python(self, template_path: Path):
        """Each template should generate valid Python code."""
        yaml_content = template_path.read_text()
        pipeline = parse_gitlab_ci(yaml_content)

        # Generate Python code
        python_code = generate_python_code(pipeline)

        # Should be valid Python
        compile(python_code, f"<{template_path.name}>", "exec")

        # Should contain expected imports
        assert "from wetwire_gitlab.pipeline import" in python_code

    @pytest.mark.parametrize("template_path", get_all_templates(), ids=lambda p: p.name)
    def test_template_has_expected_structure(self, template_path: Path):
        """Each template should have expected structure after parsing."""
        yaml_content = template_path.read_text()
        pipeline = parse_gitlab_ci(yaml_content)

        # If YAML has stages, pipeline should have them
        import yaml
        data = yaml.safe_load(yaml_content)
        if data and "stages" in data:
            assert len(pipeline.stages) > 0

        # If YAML has jobs, pipeline should have them
        # Note: Jobs can have either 'script' or 'trigger' (but not necessarily both)
        if data:
            job_count = sum(1 for k, v in data.items()
                          if isinstance(v, dict) and ("script" in v or "trigger" in v))
            if job_count > 0:
                assert len(pipeline.jobs) == job_count


class TestTemplateRoundTrip:
    """Test round-trip conversion: YAML -> parse -> build -> YAML."""

    @pytest.mark.parametrize("template_path", get_all_templates(), ids=lambda p: p.name)
    def test_template_round_trip_semantic_equivalence(self, template_path: Path):
        """Each template should maintain semantic equivalence through round-trip."""
        original_yaml = template_path.read_text()

        # Parse the YAML
        ir_pipeline = parse_gitlab_ci(original_yaml)

        # Convert IR to typed objects
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]

        # Rebuild YAML from typed objects
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        # Compare for semantic equivalence
        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        # If not equivalent, print diffs for debugging
        if not is_eq:
            print(f"\n=== Template: {template_path.name} ===")
            print("Differences found:")
            for diff in diffs:
                print(f"  - {diff}")
            print(f"\nOriginal YAML:\n{original_yaml}")
            print(f"\nRebuilt YAML:\n{rebuilt_yaml}")

        assert is_eq is True, (
            f"Round-trip failed for {template_path.name} with differences: {diffs}"
        )


class TestFeatureCoverage:
    """Test and track coverage of GitLab CI features."""

    def test_feature_coverage_report(self):
        """Generate a report of GitLab CI features covered by test corpus."""
        all_features = set()
        feature_counts: dict[str, int] = {}
        template_features: dict[str, set[str]] = {}

        templates = get_all_templates()

        for template_path in templates:
            yaml_content = template_path.read_text()
            features = extract_features(yaml_content)

            all_features.update(features)
            template_features[template_path.name] = features

            for feature in features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1

        # Generate report
        print("\n" + "=" * 70)
        print("GitLab CI Feature Coverage Report")
        print("=" * 70)
        print(f"\nTotal templates: {len(templates)}")
        print(f"Total unique features: {len(all_features)}")
        print("\nFeature frequency:")
        for feature in sorted(feature_counts.keys()):
            count = feature_counts[feature]
            percentage = (count / len(templates)) * 100
            print(f"  {feature:30} {count:3} / {len(templates):3} ({percentage:5.1f}%)")

        print("\n" + "=" * 70)

        # Ensure we have good coverage of essential features
        essential_features = {
            "stages",
            "job.stage",
            "job.artifacts",
            "job.cache",
            "job.rules",
            "job.needs",
        }

        covered_essential = all_features & essential_features
        coverage_percentage = (len(covered_essential) / len(essential_features)) * 100

        print(f"\nEssential feature coverage: {len(covered_essential)}/{len(essential_features)} ({coverage_percentage:.1f}%)")
        print(f"Covered: {sorted(covered_essential)}")

        missing = essential_features - covered_essential
        if missing:
            print(f"Missing: {sorted(missing)}")

        # We should cover at least 80% of essential features
        assert coverage_percentage >= 80.0, (
            f"Essential feature coverage too low: {coverage_percentage:.1f}%"
        )

    def test_minimum_template_count(self):
        """Ensure we have a minimum number of test templates."""
        templates = get_all_templates()
        assert len(templates) >= 20, (
            f"Expected at least 20 templates, found {len(templates)}"
        )


class TestSuccessRate:
    """Test and report success rates for import operations."""

    def test_import_success_rate(self):
        """Calculate and report import success rate."""
        templates = get_all_templates()
        success_count = 0
        failures = []

        for template_path in templates:
            try:
                yaml_content = template_path.read_text()
                pipeline = parse_gitlab_ci(yaml_content)

                if pipeline is not None:
                    success_count += 1
                else:
                    failures.append((template_path.name, "Returned None"))
            except Exception as e:
                failures.append((template_path.name, str(e)))

        success_rate = (success_count / len(templates)) * 100 if templates else 0

        print("\n" + "=" * 70)
        print("Import Success Rate Report")
        print("=" * 70)
        print(f"\nTotal templates: {len(templates)}")
        print(f"Successful imports: {success_count}")
        print(f"Failed imports: {len(failures)}")
        print(f"Success rate: {success_rate:.1f}%")

        if failures:
            print("\nFailures:")
            for name, error in failures:
                print(f"  - {name}: {error}")

        print("=" * 70)

        # We should have at least 95% success rate
        assert success_rate >= 95.0, (
            f"Import success rate too low: {success_rate:.1f}%"
        )

    def test_code_generation_success_rate(self):
        """Calculate and report Python code generation success rate."""
        templates = get_all_templates()
        success_count = 0
        failures = []

        for template_path in templates:
            try:
                yaml_content = template_path.read_text()
                pipeline = parse_gitlab_ci(yaml_content)
                python_code = generate_python_code(pipeline)

                # Try to compile
                compile(python_code, f"<{template_path.name}>", "exec")
                success_count += 1
            except Exception as e:
                failures.append((template_path.name, str(e)))

        success_rate = (success_count / len(templates)) * 100 if templates else 0

        print("\n" + "=" * 70)
        print("Code Generation Success Rate Report")
        print("=" * 70)
        print(f"\nTotal templates: {len(templates)}")
        print(f"Successful generations: {success_count}")
        print(f"Failed generations: {len(failures)}")
        print(f"Success rate: {success_rate:.1f}%")

        if failures:
            print("\nFailures:")
            for name, error in failures:
                print(f"  - {name}: {error}")

        print("=" * 70)

        # We should have at least 95% success rate
        assert success_rate >= 95.0, (
            f"Code generation success rate too low: {success_rate:.1f}%"
        )

    def test_round_trip_success_rate(self):
        """Calculate and report round-trip success rate."""
        templates = get_all_templates()
        success_count = 0
        failures = []

        for template_path in templates:
            try:
                original_yaml = template_path.read_text()
                ir_pipeline = parse_gitlab_ci(original_yaml)
                pipeline = ir_pipeline.to_pipeline()
                jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
                rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

                is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

                if is_eq:
                    success_count += 1
                else:
                    failures.append((template_path.name, f"{len(diffs)} differences"))
            except Exception as e:
                failures.append((template_path.name, str(e)))

        success_rate = (success_count / len(templates)) * 100 if templates else 0

        print("\n" + "=" * 70)
        print("Round-Trip Success Rate Report")
        print("=" * 70)
        print(f"\nTotal templates: {len(templates)}")
        print(f"Successful round-trips: {success_count}")
        print(f"Failed round-trips: {len(failures)}")
        print(f"Success rate: {success_rate:.1f}%")

        if failures:
            print("\nFailures:")
            for name, error in failures:
                print(f"  - {name}: {error}")

        print("=" * 70)

        # We should have at least 90% success rate for round-trips
        # (slightly lower than import since semantic equivalence is stricter)
        assert success_rate >= 90.0, (
            f"Round-trip success rate too low: {success_rate:.1f}%"
        )


class TestSpecificPatterns:
    """Test specific GitLab CI patterns that are common or complex."""

    def test_dag_pattern_with_needs(self):
        """Test DAG-style dependencies with needs."""
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  script:
    - make test
  needs:
    - build
"""
        ir_pipeline = parse_gitlab_ci(yaml_content)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(yaml_content, rebuilt_yaml)
        assert is_eq is True, f"DAG pattern failed: {diffs}"

    def test_complex_needs_with_artifacts(self):
        """Test complex needs with artifact control."""
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  script:
    - make test
  needs:
    - job: build
      artifacts: true
"""
        ir_pipeline = parse_gitlab_ci(yaml_content)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(yaml_content, rebuilt_yaml)
        assert is_eq is True, f"Complex needs pattern failed: {diffs}"

    def test_multiple_rules_pattern(self):
        """Test job with multiple rules."""
        yaml_content = """
deploy:
  script:
    - deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
    - if: $CI_COMMIT_TAG
      when: on_success
"""
        ir_pipeline = parse_gitlab_ci(yaml_content)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(yaml_content, rebuilt_yaml)
        assert is_eq is True, f"Multiple rules pattern failed: {diffs}"

    def test_matrix_parallel_pattern(self):
        """Test parallel matrix pattern."""
        yaml_content = """
test:
  script:
    - pytest
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.9", "3.10", "3.11"]
"""
        ir_pipeline = parse_gitlab_ci(yaml_content)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(yaml_content, rebuilt_yaml)
        assert is_eq is True, f"Matrix parallel pattern failed: {diffs}"


class TestTemplateCategories:
    """Test templates organized by category."""

    def test_basic_templates(self):
        """Test basic template patterns (01-07)."""
        basic_templates = [p for p in get_all_templates()
                          if p.name.startswith(("01_", "02_", "03_", "04_", "05_", "06_", "07_"))]

        assert len(basic_templates) >= 7, "Expected at least 7 basic templates"

        for template_path in basic_templates:
            yaml_content = template_path.read_text()
            pipeline = parse_gitlab_ci(yaml_content)
            assert pipeline is not None, f"Failed to parse {template_path.name}"

    def test_advanced_templates(self):
        """Test advanced template patterns (08-20)."""
        advanced_templates = [p for p in get_all_templates()
                             if any(p.name.startswith(f"{i:02d}_") for i in range(8, 21))]

        assert len(advanced_templates) >= 10, "Expected at least 10 advanced templates"

        for template_path in advanced_templates:
            yaml_content = template_path.read_text()
            pipeline = parse_gitlab_ci(yaml_content)
            assert pipeline is not None, f"Failed to parse {template_path.name}"

    def test_real_world_templates(self):
        """Test real-world project templates (21+)."""
        real_world_templates = [p for p in get_all_templates()
                               if any(p.name.startswith(f"{i:02d}_") for i in range(21, 30))]

        assert len(real_world_templates) >= 3, "Expected at least 3 real-world templates"

        for template_path in real_world_templates:
            yaml_content = template_path.read_text()
            pipeline = parse_gitlab_ci(yaml_content)
            assert pipeline is not None, f"Failed to parse {template_path.name}"
