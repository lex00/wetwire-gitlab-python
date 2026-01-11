"""Tests for additional linter rules WGL012-WGL019."""


class TestWGL012UseCachePolicyConstants:
    """Tests for WGL012: Use typed CachePolicy constants."""

    def test_rule_in_registry(self):
        """WGL012 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL012" in RULE_REGISTRY

    def test_detects_string_cache_policy(self):
        """WGL012 detects string literals for cache policy."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Cache

cache = Cache(key="npm", paths=["node_modules/"], policy="pull")
job = Job(name="build", stage="build", script=["npm install"], cache=cache)
"""
        issues = lint_code(code, rules=["WGL012"])
        assert len(issues) == 1
        assert issues[0].code == "WGL012"
        assert "CachePolicy" in issues[0].message

    def test_no_issue_for_cache_policy_constant(self):
        """WGL012 allows CachePolicy constants."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Cache
from wetwire_gitlab.intrinsics import CachePolicy

cache = Cache(key="npm", paths=["node_modules/"], policy=CachePolicy.PULL)
job = Job(name="build", stage="build", script=["npm install"], cache=cache)
"""
        issues = lint_code(code, rules=["WGL012"])
        assert len(issues) == 0


class TestWGL013UseArtifactsWhenConstants:
    """Tests for WGL013: Use typed ArtifactsWhen constants."""

    def test_rule_in_registry(self):
        """WGL013 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL013" in RULE_REGISTRY

    def test_detects_string_artifacts_when(self):
        """WGL013 detects string literals for artifacts when."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Artifacts

artifacts = Artifacts(paths=["dist/"], when="always")
job = Job(name="build", stage="build", script=["make"], artifacts=artifacts)
"""
        issues = lint_code(code, rules=["WGL013"])
        assert len(issues) == 1
        assert issues[0].code == "WGL013"
        assert "ArtifactsWhen" in issues[0].message

    def test_no_issue_for_artifacts_when_constant(self):
        """WGL013 allows ArtifactsWhen constants."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Artifacts
from wetwire_gitlab.intrinsics import ArtifactsWhen

artifacts = Artifacts(paths=["dist/"], when=ArtifactsWhen.ALWAYS)
job = Job(name="build", stage="build", script=["make"], artifacts=artifacts)
"""
        issues = lint_code(code, rules=["WGL013"])
        assert len(issues) == 0


class TestWGL014MissingScript:
    """Tests for WGL014: Job should have script, trigger, or inherit."""

    def test_rule_in_registry(self):
        """WGL014 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL014" in RULE_REGISTRY

    def test_detects_job_without_script(self):
        """WGL014 detects jobs without script."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="empty", stage="test")
"""
        issues = lint_code(code, rules=["WGL014"])
        assert len(issues) == 1
        assert issues[0].code == "WGL014"
        assert "script" in issues[0].message.lower()

    def test_no_issue_for_job_with_script(self):
        """WGL014 allows jobs with script."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"])
"""
        issues = lint_code(code, rules=["WGL014"])
        assert len(issues) == 0

    def test_no_issue_for_job_with_trigger(self):
        """WGL014 allows jobs with trigger (child pipelines)."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Trigger

job = Job(name="trigger", stage="deploy", trigger=Trigger(include="child.yml"))
"""
        issues = lint_code(code, rules=["WGL014"])
        assert len(issues) == 0


class TestWGL015MissingName:
    """Tests for WGL015: Job should have explicit name."""

    def test_rule_in_registry(self):
        """WGL015 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL015" in RULE_REGISTRY

    def test_detects_job_without_name(self):
        """WGL015 detects jobs without name."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(stage="test", script=["pytest"])
"""
        issues = lint_code(code, rules=["WGL015"])
        assert len(issues) == 1
        assert issues[0].code == "WGL015"
        assert "name" in issues[0].message.lower()

    def test_no_issue_for_job_with_name(self):
        """WGL015 allows jobs with explicit name."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"])
"""
        issues = lint_code(code, rules=["WGL015"])
        assert len(issues) == 0


class TestWGL016UseImageDataclass:
    """Tests for WGL016: Use Image dataclass instead of string."""

    def test_rule_in_registry(self):
        """WGL016 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL016" in RULE_REGISTRY

    def test_detects_string_image(self):
        """WGL016 detects string image specification."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], image="python:3.11")
"""
        issues = lint_code(code, rules=["WGL016"])
        assert len(issues) == 1
        assert issues[0].code == "WGL016"
        assert "Image" in issues[0].message

    def test_no_issue_for_image_dataclass(self):
        """WGL016 allows Image dataclass."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Image

job = Job(name="test", stage="test", script=["pytest"], image=Image(name="python:3.11"))
"""
        issues = lint_code(code, rules=["WGL016"])
        assert len(issues) == 0


class TestWGL017EmptyRulesList:
    """Tests for WGL017: Empty rules list means job never runs."""

    def test_rule_in_registry(self):
        """WGL017 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL017" in RULE_REGISTRY

    def test_detects_empty_rules_list(self):
        """WGL017 detects empty rules list."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], rules=[])
"""
        issues = lint_code(code, rules=["WGL017"])
        assert len(issues) == 1
        assert issues[0].code == "WGL017"
        assert "empty" in issues[0].message.lower()

    def test_no_issue_for_non_empty_rules(self):
        """WGL017 allows non-empty rules list."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Rule

job = Job(name="test", stage="test", script=["pytest"], rules=[Rule(if_="$CI_COMMIT_BRANCH")])
"""
        issues = lint_code(code, rules=["WGL017"])
        assert len(issues) == 0


class TestWGL018NeedsWithoutStage:
    """Tests for WGL018: Jobs with needs should specify stage."""

    def test_rule_in_registry(self):
        """WGL018 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL018" in RULE_REGISTRY

    def test_detects_needs_without_stage(self):
        """WGL018 detects needs keyword without stage."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", script=["deploy"], needs=["build"])
"""
        issues = lint_code(code, rules=["WGL018"])
        assert len(issues) == 1
        assert issues[0].code == "WGL018"

    def test_no_issue_for_needs_with_stage(self):
        """WGL018 allows needs with explicit stage."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], needs=["build"])
"""
        issues = lint_code(code, rules=["WGL018"])
        assert len(issues) == 0


class TestWGL019ManualWithoutAllowFailure:
    """Tests for WGL019: Manual jobs should consider allow_failure."""

    def test_rule_in_registry(self):
        """WGL019 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL019" in RULE_REGISTRY

    def test_detects_manual_without_allow_failure(self):
        """WGL019 detects manual jobs without allow_failure."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(name="deploy", stage="deploy", script=["deploy"], when=When.MANUAL)
"""
        issues = lint_code(code, rules=["WGL019"])
        assert len(issues) == 1
        assert issues[0].code == "WGL019"
        assert "allow_failure" in issues[0].message.lower()

    def test_no_issue_for_manual_with_allow_failure(self):
        """WGL019 allows manual jobs with allow_failure."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(name="deploy", stage="deploy", script=["deploy"], when=When.MANUAL, allow_failure=True)
"""
        issues = lint_code(code, rules=["WGL019"])
        assert len(issues) == 0

    def test_detects_manual_string_without_allow_failure(self):
        """WGL019 also detects string 'manual' without allow_failure."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
"""
        issues = lint_code(code, rules=["WGL019"])
        # Should have WGL019 (may also have WGL010 for string when)
        wgl019_issues = [i for i in issues if i.code == "WGL019"]
        assert len(wgl019_issues) == 1


class TestWGL020AvoidNestedJobConstructors:
    """Tests for WGL020: Avoid nested Job constructors."""

    def test_rule_in_registry(self):
        """WGL020 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL020" in RULE_REGISTRY

    def test_detects_inline_job_in_needs_list(self):
        """WGL020 detects inline Job() in needs list."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make build"])
test = Job(
    name="test",
    stage="test",
    script=["make test"],
    needs=[Job(name="build", stage="build", script=["make build"])]
)
"""
        issues = lint_code(code, rules=["WGL020"])
        assert len(issues) == 1
        assert issues[0].code == "WGL020"
        assert (
            "nested" in issues[0].message.lower()
            or "inline" in issues[0].message.lower()
        )

    def test_no_issue_for_job_reference_in_needs(self):
        """WGL020 allows Job references in needs."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make build"])
test = Job(name="test", stage="test", script=["make test"], needs=[build])
"""
        issues = lint_code(code, rules=["WGL020"])
        assert len(issues) == 0

    def test_no_issue_for_string_needs(self):
        """WGL020 allows string needs."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

test = Job(name="test", stage="test", script=["make test"], needs=["build"])
"""
        issues = lint_code(code, rules=["WGL020"])
        assert len(issues) == 0


class TestWGL021UseTypedServiceConstants:
    """Tests for WGL021: Use typed Service constants."""

    def test_rule_in_registry(self):
        """WGL021 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL021" in RULE_REGISTRY

    def test_detects_string_service(self):
        """WGL021 detects string service specification."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], services=["postgres:14"])
"""
        issues = lint_code(code, rules=["WGL021"])
        assert len(issues) == 1
        assert issues[0].code == "WGL021"
        assert "service" in issues[0].message.lower()

    def test_detects_multiple_string_services(self):
        """WGL021 detects multiple string services."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    stage="test",
    script=["pytest"],
    services=["postgres:14", "redis:latest"]
)
"""
        issues = lint_code(code, rules=["WGL021"])
        assert len(issues) == 2
        assert all(i.code == "WGL021" for i in issues)

    def test_no_issue_for_service_dataclass(self):
        """WGL021 allows Service dataclass."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Service

job = Job(
    name="test",
    stage="test",
    script=["pytest"],
    services=[Service(name="postgres:14")]
)
"""
        issues = lint_code(code, rules=["WGL021"])
        assert len(issues) == 0


class TestWGL022AvoidDuplicateNeeds:
    """Tests for WGL022: Avoid duplicate needs/dependencies."""

    def test_rule_in_registry(self):
        """WGL022 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL022" in RULE_REGISTRY

    def test_detects_duplicate_string_needs(self):
        """WGL022 detects duplicate entries in needs list."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["deploy"],
    needs=["build", "test", "build"]
)
"""
        issues = lint_code(code, rules=["WGL022"])
        assert len(issues) == 1
        assert issues[0].code == "WGL022"
        assert "duplicate" in issues[0].message.lower()

    def test_detects_duplicate_dependencies(self):
        """WGL022 detects duplicate entries in dependencies list."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["deploy"],
    dependencies=["build", "test", "build"]
)
"""
        issues = lint_code(code, rules=["WGL022"])
        assert len(issues) == 1
        assert issues[0].code == "WGL022"
        assert "duplicate" in issues[0].message.lower()

    def test_no_issue_for_unique_needs(self):
        """WGL022 allows unique needs entries."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["deploy"],
    needs=["build", "test", "lint"]
)
"""
        issues = lint_code(code, rules=["WGL022"])
        assert len(issues) == 0


class TestWGL023MissingImageForScriptJobs:
    """Tests for WGL023: Warn on missing image for script jobs."""

    def test_rule_in_registry(self):
        """WGL023 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL023" in RULE_REGISTRY

    def test_detects_script_job_without_image(self):
        """WGL023 detects jobs with script but no image."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"])
"""
        issues = lint_code(code, rules=["WGL023"])
        assert len(issues) == 1
        assert issues[0].code == "WGL023"
        assert issues[0].severity == "info"
        assert "image" in issues[0].message.lower()

    def test_no_issue_for_script_job_with_image(self):
        """WGL023 allows jobs with script and image."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Image

job = Job(
    name="test",
    stage="test",
    script=["pytest"],
    image=Image(name="python:3.11")
)
"""
        issues = lint_code(code, rules=["WGL023"])
        assert len(issues) == 0

    def test_no_issue_for_trigger_job_without_image(self):
        """WGL023 allows trigger jobs without image."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job, Trigger

job = Job(name="trigger", stage="deploy", trigger=Trigger(include="child.yml"))
"""
        issues = lint_code(code, rules=["WGL023"])
        assert len(issues) == 0

    def test_no_issue_for_script_job_with_string_image(self):
        """WGL023 allows jobs with script and string image."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], image="python:3.11")
"""
        issues = lint_code(code, rules=["WGL023"])
        assert len(issues) == 0


class TestWGL024CircularDependency:
    """Tests for WGL024: Detect circular dependencies in job needs."""

    def test_rule_in_registry(self):
        """WGL024 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL024" in RULE_REGISTRY

    def test_detects_simple_circular_dependency(self):
        """WGL024 detects A -> B -> A cycle."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"], needs=["b"])
job_b = Job(name="b", stage="build", script=["echo b"], needs=["a"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL024"
        assert "circular" in issues[0].message.lower()

    def test_detects_self_reference(self):
        """WGL024 detects A -> A self-reference."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"], needs=["a"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL024"
        assert "circular" in issues[0].message.lower()

    def test_detects_longer_cycle(self):
        """WGL024 detects A -> B -> C -> A cycle."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"], needs=["c"])
job_b = Job(name="b", stage="build", script=["echo b"], needs=["a"])
job_c = Job(name="c", stage="build", script=["echo c"], needs=["b"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL024"
        # Should mention all jobs in the cycle
        cycle_jobs = ["a", "b", "c"]
        for job in cycle_jobs:
            assert job in issues[0].message.lower()

    def test_no_issue_for_valid_dag(self):
        """WGL024 allows valid DAG with no cycles."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make build"])
test = Job(name="test", stage="test", script=["make test"], needs=["build"])
deploy = Job(name="deploy", stage="deploy", script=["make deploy"], needs=["test"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) == 0

    def test_no_issue_for_diamond_dependency(self):
        """WGL024 allows diamond-shaped DAG (A -> B, A -> C, B -> D, C -> D)."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"])
job_b = Job(name="b", stage="test", script=["echo b"], needs=["a"])
job_c = Job(name="c", stage="test", script=["echo c"], needs=["a"])
job_d = Job(name="d", stage="deploy", script=["echo d"], needs=["b", "c"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) == 0

    def test_detects_cycle_with_job_reference(self):
        """WGL024 detects cycle using Job variable references."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"], needs=[job_b])
job_b = Job(name="b", stage="build", script=["echo b"], needs=[job_a])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL024"

    def test_reports_cycle_with_file_location(self):
        """WGL024 reports cycles with line numbers."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job_a = Job(name="a", stage="build", script=["echo a"], needs=["b"])
job_b = Job(name="b", stage="build", script=["echo b"], needs=["a"])
"""
        issues = lint_code(code, rules=["WGL024"])
        assert len(issues) >= 1
        assert issues[0].line_number > 0


class TestWGL025SecretPatternDetection:
    """Tests for WGL025: Detect hardcoded secrets in job definitions."""

    def test_rule_in_registry(self):
        """WGL025 is registered in RULE_REGISTRY."""
        from wetwire_gitlab.linter import RULE_REGISTRY

        assert "WGL025" in RULE_REGISTRY

    def test_detects_aws_access_key(self):
        """WGL025 detects AWS access key ID patterns."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["aws s3 sync . s3://bucket"],
    variables={"AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE"},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"
        assert "secret" in issues[0].message.lower() or "aws" in issues[0].message.lower()

    def test_detects_aws_secret_key(self):
        """WGL025 detects AWS secret access key patterns."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["aws s3 sync . s3://bucket"],
    variables={"AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_private_key_header(self):
        """WGL025 detects private key headers in scripts."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["echo '-----BEGIN RSA PRIVATE KEY-----' > key.pem"],
)
'''
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_gitlab_token(self):
        """WGL025 detects GitLab personal access tokens."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["curl -H 'PRIVATE-TOKEN: glpat-xxxxxxxxxxxxxxxxxxxx' https://gitlab.com/api"],
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_github_token(self):
        """WGL025 detects GitHub personal access tokens."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["curl -H 'Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' https://api.github.com"],
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_generic_api_key_variable(self):
        """WGL025 detects generic API key patterns in variable names."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["echo $API_KEY"],
    variables={"API_KEY": "sk_live_1234567890abcdefghij"},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_password_in_script(self):
        """WGL025 detects password patterns in scripts."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["mysql -u root -pMySecretP@ssw0rd123 database"],
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_no_issue_for_ci_variable_reference(self):
        """WGL025 allows CI variable references (not hardcoded)."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import CI

job = Job(
    name="deploy",
    stage="deploy",
    script=["aws s3 sync . s3://bucket"],
    variables={"AWS_ACCESS_KEY_ID": CI.AWS_ACCESS_KEY_ID},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) == 0

    def test_no_issue_for_safe_variables(self):
        """WGL025 allows safe variable values."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="build",
    stage="build",
    script=["make build"],
    variables={"NODE_ENV": "production", "LOG_LEVEL": "debug"},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) == 0

    def test_detects_slack_webhook(self):
        """WGL025 detects Slack webhook URLs."""
        from wetwire_gitlab.linter import lint_code

        # Use a URL with TEST prefix to avoid GitHub secret scanning
        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="notify",
    stage="notify",
    script=["curl -X POST https://hooks.slack.com/services/TESTTOKEN/BTESTTEST/testwebhooktoken"],
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"

    def test_detects_gcp_service_account_key(self):
        """WGL025 detects GCP service account key patterns."""
        from wetwire_gitlab.linter import lint_code

        code = """from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["gcloud auth activate-service-account"],
    variables={"GOOGLE_APPLICATION_CREDENTIALS_JSON": '{"type":"service_account","private_key":"-----BEGIN PRIVATE KEY-----"}'},
)
"""
        issues = lint_code(code, rules=["WGL025"])
        assert len(issues) >= 1
        assert issues[0].code == "WGL025"
