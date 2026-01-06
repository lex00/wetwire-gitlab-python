"""Tests for serialization module."""

import yaml


class TestToDict:
    """Tests for dataclass to dict conversion."""

    def test_job_to_dict_minimal(self):
        """Job converts to dict with only set fields."""
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(name="build", script=["echo hello"])
        result = to_dict(job)

        assert result["script"] == ["echo hello"]
        assert "stage" not in result  # None values omitted
        assert "image" not in result

    def test_job_to_dict_full(self):
        """Job converts to dict with all fields."""
        from wetwire_gitlab.pipeline import Artifacts, Image, Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(
            name="test",
            stage="test",
            image=Image(name="python:3.11"),
            script=["pytest"],
            artifacts=Artifacts(paths=["coverage/"]),
        )
        result = to_dict(job)

        assert result["stage"] == "test"
        assert result["image"]["name"] == "python:3.11"
        assert result["script"] == ["pytest"]
        assert result["artifacts"]["paths"] == ["coverage/"]

    def test_rule_if_field_conversion(self):
        """Rule if_ field converts to 'if' in dict."""
        from wetwire_gitlab.pipeline import Rule
        from wetwire_gitlab.serialize import to_dict

        rule = Rule(if_="$CI_COMMIT_BRANCH == 'main'", when="always")
        result = to_dict(rule)

        assert "if" in result
        assert "if_" not in result
        assert result["if"] == "$CI_COMMIT_BRANCH == 'main'"
        assert result["when"] == "always"

    def test_artifacts_to_dict(self):
        """Artifacts converts to dict properly."""
        from wetwire_gitlab.pipeline import Artifacts
        from wetwire_gitlab.serialize import to_dict

        artifacts = Artifacts(
            paths=["dist/"],
            expire_in="1 week",
            when="on_success",
        )
        result = to_dict(artifacts)

        assert result["paths"] == ["dist/"]
        assert result["expire_in"] == "1 week"
        assert result["when"] == "on_success"

    def test_cache_to_dict(self):
        """Cache converts to dict properly."""
        from wetwire_gitlab.pipeline import Cache
        from wetwire_gitlab.serialize import to_dict

        cache = Cache(
            paths=[".cache/pip"],
            key="pip-$CI_COMMIT_REF_SLUG",
            policy="pull-push",
        )
        result = to_dict(cache)

        assert result["paths"] == [".cache/pip"]
        assert result["key"] == "pip-$CI_COMMIT_REF_SLUG"
        assert result["policy"] == "pull-push"

    def test_include_to_dict(self):
        """Include converts to dict properly."""
        from wetwire_gitlab.pipeline import Include
        from wetwire_gitlab.serialize import to_dict

        include = Include(local="/.gitlab/ci/build.yml")
        result = to_dict(include)

        assert result["local"] == "/.gitlab/ci/build.yml"

    def test_include_component_to_dict(self):
        """Include component converts to dict properly."""
        from wetwire_gitlab.pipeline import Include
        from wetwire_gitlab.serialize import to_dict

        include = Include(component="gitlab.com/components/sast@1.0.0")
        result = to_dict(include)

        assert result["component"] == "gitlab.com/components/sast@1.0.0"

    def test_workflow_to_dict(self):
        """Workflow converts to dict properly."""
        from wetwire_gitlab.pipeline import Rule, Workflow
        from wetwire_gitlab.serialize import to_dict

        workflow = Workflow(
            name="Build Pipeline",
            rules=[Rule(if_="$CI_COMMIT_BRANCH")],
        )
        result = to_dict(workflow)

        assert result["name"] == "Build Pipeline"
        assert len(result["rules"]) == 1
        assert result["rules"][0]["if"] == "$CI_COMMIT_BRANCH"

    def test_trigger_to_dict(self):
        """Trigger converts to dict properly."""
        from wetwire_gitlab.pipeline import Trigger
        from wetwire_gitlab.serialize import to_dict

        trigger = Trigger(
            include="deploy/.gitlab-ci.yml",
            strategy="depend",
        )
        result = to_dict(trigger)

        assert result["include"] == "deploy/.gitlab-ci.yml"
        assert result["strategy"] == "depend"

    def test_pipeline_to_dict(self):
        """Pipeline converts to dict properly."""
        from wetwire_gitlab.pipeline import Include, Pipeline
        from wetwire_gitlab.serialize import to_dict

        pipeline = Pipeline(
            stages=["build", "test", "deploy"],
            include=[Include(local="/ci/build.yml")],
        )
        result = to_dict(pipeline)

        assert result["stages"] == ["build", "test", "deploy"]
        assert len(result["include"]) == 1

    def test_none_values_omitted(self):
        """None values are not included in dict."""
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(name="build", script=["echo hi"])
        result = to_dict(job)

        # These fields are None and should not appear
        assert "image" not in result
        assert "artifacts" not in result
        assert "cache" not in result
        assert "stage" not in result

    def test_empty_list_omitted(self):
        """Empty lists are preserved (not omitted)."""
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(name="build", script=[])
        result = to_dict(job)

        # Empty list should be preserved
        assert result["script"] == []


class TestJobRefSerialization:
    """Tests for JobRef serialization in needs."""

    def test_jobref_simple_in_needs(self):
        """JobRef serializes to job name string."""
        from wetwire_gitlab.contracts import JobRef
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(
            name="test",
            script=["pytest"],
            needs=[JobRef(job="build")],
        )
        result = to_dict(job)

        assert result["needs"] == ["build"]

    def test_jobref_with_artifacts_in_needs(self):
        """JobRef with artifacts serializes to dict."""
        from wetwire_gitlab.contracts import JobRef
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(
            name="deploy",
            script=["deploy.sh"],
            needs=[JobRef(job="build", artifacts=True)],
        )
        result = to_dict(job)

        assert result["needs"] == [{"job": "build", "artifacts": True}]

    def test_mixed_needs_serialization(self):
        """Mixed string and JobRef needs serialize correctly."""
        from wetwire_gitlab.contracts import JobRef
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_dict

        job = Job(
            name="deploy",
            script=["deploy.sh"],
            needs=["build", JobRef(job="test", artifacts=True)],
        )
        result = to_dict(job)

        assert result["needs"] == ["build", {"job": "test", "artifacts": True}]


class TestToYaml:
    """Tests for YAML serialization."""

    def test_job_to_yaml(self):
        """Job serializes to valid YAML."""
        from wetwire_gitlab.pipeline import Job
        from wetwire_gitlab.serialize import to_yaml

        job = Job(name="build", stage="build", script=["go build ./..."])
        result = to_yaml(job)

        # Parse the YAML to verify it's valid
        parsed = yaml.safe_load(result)
        assert parsed["stage"] == "build"
        assert parsed["script"] == ["go build ./..."]

    def test_pipeline_to_yaml(self):
        """Pipeline serializes to valid YAML."""
        from wetwire_gitlab.pipeline import Pipeline
        from wetwire_gitlab.serialize import to_yaml

        pipeline = Pipeline(stages=["build", "test", "deploy"])
        result = to_yaml(pipeline)

        parsed = yaml.safe_load(result)
        assert parsed["stages"] == ["build", "test", "deploy"]

    def test_rule_if_in_yaml(self):
        """Rule if_ serializes as 'if' in YAML."""
        from wetwire_gitlab.pipeline import Rule
        from wetwire_gitlab.serialize import to_yaml

        rule = Rule(if_="$CI_COMMIT_BRANCH == 'main'")
        result = to_yaml(rule)

        parsed = yaml.safe_load(result)
        assert "if" in parsed
        assert parsed["if"] == "$CI_COMMIT_BRANCH == 'main'"


class TestBuildPipeline:
    """Tests for building complete pipeline YAML."""

    def test_build_pipeline_with_jobs(self):
        """Build complete pipeline with jobs."""
        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(stages=["build", "test"])
        jobs = [
            Job(name="build", stage="build", script=["make build"]),
            Job(name="test", stage="test", script=["make test"]),
        ]

        result = build_pipeline_yaml(pipeline, jobs)
        parsed = yaml.safe_load(result)

        assert parsed["stages"] == ["build", "test"]
        assert "build" in parsed
        assert "test" in parsed
        assert parsed["build"]["script"] == ["make build"]
        assert parsed["test"]["script"] == ["make test"]

    def test_build_pipeline_with_includes(self):
        """Build pipeline with includes."""
        from wetwire_gitlab.pipeline import Include, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(
            stages=["build"],
            include=[Include(local="/ci/build.yml")],
        )

        result = build_pipeline_yaml(pipeline, [])
        parsed = yaml.safe_load(result)

        assert "include" in parsed
        assert parsed["include"][0]["local"] == "/ci/build.yml"

    def test_build_pipeline_with_workflow(self):
        """Build pipeline with workflow rules."""
        from wetwire_gitlab.pipeline import Pipeline, Rule, Workflow
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(
            stages=["build"],
            workflow=Workflow(
                name="My Pipeline",
                rules=[Rule(if_="$CI_COMMIT_BRANCH")],
            ),
        )

        result = build_pipeline_yaml(pipeline, [])
        parsed = yaml.safe_load(result)

        assert "workflow" in parsed
        assert parsed["workflow"]["name"] == "My Pipeline"
        assert parsed["workflow"]["rules"][0]["if"] == "$CI_COMMIT_BRANCH"

    def test_build_pipeline_with_default(self):
        """Build pipeline with default settings."""
        from wetwire_gitlab.pipeline import Default, Image, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(
            stages=["build"],
            default=Default(image=Image(name="python:3.11")),
        )

        result = build_pipeline_yaml(pipeline, [])
        parsed = yaml.safe_load(result)

        assert "default" in parsed
        assert parsed["default"]["image"]["name"] == "python:3.11"

    def test_build_pipeline_with_variables(self):
        """Build pipeline with variables."""
        from wetwire_gitlab.pipeline import Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(
            stages=["build"],
            variables={"CI_DEBUG": "true", "APP_ENV": "test"},
        )

        result = build_pipeline_yaml(pipeline, [])
        parsed = yaml.safe_load(result)

        assert "variables" in parsed
        assert parsed["variables"]["CI_DEBUG"] == "true"
        assert parsed["variables"]["APP_ENV"] == "test"

    def test_job_name_not_in_job_dict(self):
        """Job name is used as key, not in job dict."""
        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(stages=["build"])
        jobs = [Job(name="my-build-job", stage="build", script=["make"])]

        result = build_pipeline_yaml(pipeline, jobs)
        parsed = yaml.safe_load(result)

        assert "my-build-job" in parsed
        assert "name" not in parsed["my-build-job"]


class TestFieldNameConversion:
    """Tests for field name conversion."""

    def test_if_underscore_to_if(self):
        """if_ converts to if."""
        from wetwire_gitlab.serialize import convert_field_name

        assert convert_field_name("if_") == "if"

    def test_regular_field_unchanged(self):
        """Regular field names are unchanged."""
        from wetwire_gitlab.serialize import convert_field_name

        assert convert_field_name("script") == "script"
        assert convert_field_name("before_script") == "before_script"
        assert convert_field_name("artifacts") == "artifacts"

    def test_expire_in_unchanged(self):
        """expire_in stays as expire_in."""
        from wetwire_gitlab.serialize import convert_field_name

        assert convert_field_name("expire_in") == "expire_in"
