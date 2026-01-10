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

        code = '''from wetwire_gitlab.pipeline import Job, Cache

cache = Cache(key="npm", paths=["node_modules/"], policy="pull")
job = Job(name="build", stage="build", script=["npm install"], cache=cache)
'''
        issues = lint_code(code, rules=["WGL012"])
        assert len(issues) == 1
        assert issues[0].code == "WGL012"
        assert "CachePolicy" in issues[0].message

    def test_no_issue_for_cache_policy_constant(self):
        """WGL012 allows CachePolicy constants."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job, Cache
from wetwire_gitlab.intrinsics import CachePolicy

cache = Cache(key="npm", paths=["node_modules/"], policy=CachePolicy.PULL)
job = Job(name="build", stage="build", script=["npm install"], cache=cache)
'''
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

        code = '''from wetwire_gitlab.pipeline import Job, Artifacts

artifacts = Artifacts(paths=["dist/"], when="always")
job = Job(name="build", stage="build", script=["make"], artifacts=artifacts)
'''
        issues = lint_code(code, rules=["WGL013"])
        assert len(issues) == 1
        assert issues[0].code == "WGL013"
        assert "ArtifactsWhen" in issues[0].message

    def test_no_issue_for_artifacts_when_constant(self):
        """WGL013 allows ArtifactsWhen constants."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job, Artifacts
from wetwire_gitlab.intrinsics import ArtifactsWhen

artifacts = Artifacts(paths=["dist/"], when=ArtifactsWhen.ALWAYS)
job = Job(name="build", stage="build", script=["make"], artifacts=artifacts)
'''
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

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="empty", stage="test")
'''
        issues = lint_code(code, rules=["WGL014"])
        assert len(issues) == 1
        assert issues[0].code == "WGL014"
        assert "script" in issues[0].message.lower()

    def test_no_issue_for_job_with_script(self):
        """WGL014 allows jobs with script."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"])
'''
        issues = lint_code(code, rules=["WGL014"])
        assert len(issues) == 0

    def test_no_issue_for_job_with_trigger(self):
        """WGL014 allows jobs with trigger (child pipelines)."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job, Trigger

job = Job(name="trigger", stage="deploy", trigger=Trigger(include="child.yml"))
'''
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

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(stage="test", script=["pytest"])
'''
        issues = lint_code(code, rules=["WGL015"])
        assert len(issues) == 1
        assert issues[0].code == "WGL015"
        assert "name" in issues[0].message.lower()

    def test_no_issue_for_job_with_name(self):
        """WGL015 allows jobs with explicit name."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"])
'''
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

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], image="python:3.11")
'''
        issues = lint_code(code, rules=["WGL016"])
        assert len(issues) == 1
        assert issues[0].code == "WGL016"
        assert "Image" in issues[0].message

    def test_no_issue_for_image_dataclass(self):
        """WGL016 allows Image dataclass."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job, Image

job = Job(name="test", stage="test", script=["pytest"], image=Image(name="python:3.11"))
'''
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

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["pytest"], rules=[])
'''
        issues = lint_code(code, rules=["WGL017"])
        assert len(issues) == 1
        assert issues[0].code == "WGL017"
        assert "empty" in issues[0].message.lower()

    def test_no_issue_for_non_empty_rules(self):
        """WGL017 allows non-empty rules list."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job, Rule

job = Job(name="test", stage="test", script=["pytest"], rules=[Rule(if_="$CI_COMMIT_BRANCH")])
'''
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

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", script=["deploy"], needs=["build"])
'''
        issues = lint_code(code, rules=["WGL018"])
        assert len(issues) == 1
        assert issues[0].code == "WGL018"

    def test_no_issue_for_needs_with_stage(self):
        """WGL018 allows needs with explicit stage."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], needs=["build"])
'''
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

        code = '''from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(name="deploy", stage="deploy", script=["deploy"], when=When.MANUAL)
'''
        issues = lint_code(code, rules=["WGL019"])
        assert len(issues) == 1
        assert issues[0].code == "WGL019"
        assert "allow_failure" in issues[0].message.lower()

    def test_no_issue_for_manual_with_allow_failure(self):
        """WGL019 allows manual jobs with allow_failure."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(name="deploy", stage="deploy", script=["deploy"], when=When.MANUAL, allow_failure=True)
'''
        issues = lint_code(code, rules=["WGL019"])
        assert len(issues) == 0

    def test_detects_manual_string_without_allow_failure(self):
        """WGL019 also detects string 'manual' without allow_failure."""
        from wetwire_gitlab.linter import lint_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
'''
        issues = lint_code(code, rules=["WGL019"])
        # Should have WGL019 (may also have WGL010 for string when)
        wgl019_issues = [i for i in issues if i.code == "WGL019"]
        assert len(wgl019_issues) == 1
