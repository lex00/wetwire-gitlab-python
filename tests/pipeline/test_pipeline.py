"""Tests for pipeline module dataclasses."""

from dataclasses import fields


class TestJob:
    """Tests for Job dataclass."""

    def test_job_creation_minimal(self):
        """Job can be created with just a name."""
        from wetwire_gitlab.pipeline import Job

        job = Job(name="build")
        assert job.name == "build"

    def test_job_creation_full(self):
        """Job can be created with all fields."""
        from wetwire_gitlab.pipeline import Artifacts, Cache, Image, Job, Rule

        job = Job(
            name="test",
            stage="test",
            image=Image(name="python:3.11"),
            script=["pytest"],
            before_script=["pip install -e ."],
            after_script=["echo done"],
            rules=[Rule(if_="$CI_COMMIT_BRANCH == 'main'")],
            artifacts=Artifacts(paths=["coverage/"]),
            cache=Cache(paths=[".cache/"]),
            needs=["build"],
            variables={"PYTHONPATH": "src"},
            allow_failure=False,
            when="on_success",
            timeout="1h",
            retry=2,
            tags=["docker"],
            services=["postgres:15"],
            coverage="/^TOTAL.+?(\\d+%)$/",
            environment="production",
            resource_group="deploy",
            interruptible=True,
            parallel=4,
        )
        assert job.name == "test"
        assert job.stage == "test"
        assert job.script == ["pytest"]

    def test_job_is_dataclass(self):
        """Job is a proper dataclass."""
        from wetwire_gitlab.pipeline import Job

        assert hasattr(Job, "__dataclass_fields__")
        field_names = {f.name for f in fields(Job)}
        assert "name" in field_names
        assert "script" in field_names
        assert "stage" in field_names


class TestImage:
    """Tests for Image dataclass."""

    def test_image_string_name(self):
        """Image can be created with just a name."""
        from wetwire_gitlab.pipeline import Image

        img = Image(name="python:3.11")
        assert img.name == "python:3.11"

    def test_image_with_entrypoint(self):
        """Image can have entrypoint."""
        from wetwire_gitlab.pipeline import Image

        img = Image(name="python:3.11", entrypoint=["/bin/bash"])
        assert img.entrypoint == ["/bin/bash"]


class TestArtifacts:
    """Tests for Artifacts dataclass."""

    def test_artifacts_paths(self):
        """Artifacts can specify paths."""
        from wetwire_gitlab.pipeline import Artifacts

        artifacts = Artifacts(paths=["dist/", "coverage/"])
        assert artifacts.paths == ["dist/", "coverage/"]

    def test_artifacts_full(self):
        """Artifacts can have all options."""
        from wetwire_gitlab.pipeline import Artifacts

        artifacts = Artifacts(
            paths=["dist/"],
            exclude=["*.pyc"],
            expire_in="1 week",
            expose_as="Build output",
            name="build-$CI_COMMIT_SHA",
            untracked=False,
            when="on_success",
            reports={"junit": "report.xml"},
        )
        assert artifacts.expire_in == "1 week"


class TestCache:
    """Tests for Cache dataclass."""

    def test_cache_paths(self):
        """Cache can specify paths."""
        from wetwire_gitlab.pipeline import Cache

        cache = Cache(paths=[".cache/pip"])
        assert cache.paths == [".cache/pip"]

    def test_cache_with_key(self):
        """Cache can have a key."""
        from wetwire_gitlab.pipeline import Cache

        cache = Cache(paths=[".cache/"], key="pip-$CI_COMMIT_REF_SLUG")
        assert cache.key == "pip-$CI_COMMIT_REF_SLUG"

    def test_cache_policy(self):
        """Cache can have a policy."""
        from wetwire_gitlab.pipeline import Cache

        cache = Cache(paths=[".cache/"], policy="pull-push")
        assert cache.policy == "pull-push"


class TestRule:
    """Tests for Rule dataclass."""

    def test_rule_if_condition(self):
        """Rule can have if condition."""
        from wetwire_gitlab.pipeline import Rule

        rule = Rule(if_="$CI_COMMIT_BRANCH == 'main'")
        assert rule.if_ == "$CI_COMMIT_BRANCH == 'main'"

    def test_rule_changes(self):
        """Rule can have changes condition."""
        from wetwire_gitlab.pipeline import Rule

        rule = Rule(changes=["src/**/*.py"])
        assert rule.changes == ["src/**/*.py"]

    def test_rule_exists(self):
        """Rule can have exists condition."""
        from wetwire_gitlab.pipeline import Rule

        rule = Rule(exists=["Dockerfile"])
        assert rule.exists == ["Dockerfile"]

    def test_rule_when(self):
        """Rule can specify when."""
        from wetwire_gitlab.pipeline import Rule

        rule = Rule(if_="$CI_COMMIT_TAG", when="manual")
        assert rule.when == "manual"

    def test_rule_allow_failure(self):
        """Rule can allow failure."""
        from wetwire_gitlab.pipeline import Rule

        rule = Rule(if_="$CI_COMMIT_TAG", allow_failure=True)
        assert rule.allow_failure is True


class TestInclude:
    """Tests for Include dataclass."""

    def test_include_local(self):
        """Include can reference local file."""
        from wetwire_gitlab.pipeline import Include

        inc = Include(local="/.gitlab/ci/build.yml")
        assert inc.local == "/.gitlab/ci/build.yml"

    def test_include_remote(self):
        """Include can reference remote URL."""
        from wetwire_gitlab.pipeline import Include

        inc = Include(remote="https://example.com/ci.yml")
        assert inc.remote == "https://example.com/ci.yml"

    def test_include_template(self):
        """Include can reference template."""
        from wetwire_gitlab.pipeline import Include

        inc = Include(template="Auto-DevOps.gitlab-ci.yml")
        assert inc.template == "Auto-DevOps.gitlab-ci.yml"

    def test_include_project(self):
        """Include can reference project file."""
        from wetwire_gitlab.pipeline import Include

        inc = Include(project="group/project", file="/ci/template.yml", ref="main")
        assert inc.project == "group/project"
        assert inc.file == "/ci/template.yml"
        assert inc.ref == "main"

    def test_include_component(self):
        """Include can reference component."""
        from wetwire_gitlab.pipeline import Include

        inc = Include(component="gitlab.com/components/sast@1.0.0")
        assert inc.component == "gitlab.com/components/sast@1.0.0"


class TestWorkflow:
    """Tests for Workflow dataclass."""

    def test_workflow_rules(self):
        """Workflow can have rules."""
        from wetwire_gitlab.pipeline import Rule, Workflow

        workflow = Workflow(rules=[Rule(if_="$CI_COMMIT_BRANCH")])
        assert len(workflow.rules) == 1

    def test_workflow_name(self):
        """Workflow can have name."""
        from wetwire_gitlab.pipeline import Workflow

        workflow = Workflow(name="Build Pipeline")
        assert workflow.name == "Build Pipeline"


class TestTrigger:
    """Tests for Trigger dataclass (child/multi-project pipelines)."""

    def test_trigger_include(self):
        """Trigger can include child pipeline."""
        from wetwire_gitlab.pipeline import Trigger

        trigger = Trigger(include="deploy/.gitlab-ci.yml")
        assert trigger.include == "deploy/.gitlab-ci.yml"

    def test_trigger_project(self):
        """Trigger can reference another project."""
        from wetwire_gitlab.pipeline import Trigger

        trigger = Trigger(project="group/other-project", branch="main")
        assert trigger.project == "group/other-project"
        assert trigger.branch == "main"

    def test_trigger_strategy(self):
        """Trigger can have strategy."""
        from wetwire_gitlab.pipeline import Trigger

        trigger = Trigger(include="child.yml", strategy="depend")
        assert trigger.strategy == "depend"


class TestVariables:
    """Tests for Variables dataclass."""

    def test_variables_dict(self):
        """Variables can hold key-value pairs."""
        from wetwire_gitlab.pipeline import Variables

        vars = Variables(variables={"FOO": "bar", "BAZ": "qux"})
        assert vars.variables["FOO"] == "bar"

    def test_variables_with_description(self):
        """Variables can have descriptions (for CI/CD settings)."""
        from wetwire_gitlab.pipeline import Variable

        var = Variable(value="default", description="API key for service")
        assert var.description == "API key for service"


class TestPipeline:
    """Tests for Pipeline dataclass."""

    def test_pipeline_stages(self):
        """Pipeline can define stages."""
        from wetwire_gitlab.pipeline import Pipeline

        pipeline = Pipeline(stages=["build", "test", "deploy"])
        assert pipeline.stages == ["build", "test", "deploy"]

    def test_pipeline_with_workflow(self):
        """Pipeline can have workflow."""
        from wetwire_gitlab.pipeline import Pipeline, Rule, Workflow

        pipeline = Pipeline(
            stages=["build"],
            workflow=Workflow(rules=[Rule(if_="$CI_COMMIT_BRANCH")]),
        )
        assert pipeline.workflow is not None

    def test_pipeline_with_includes(self):
        """Pipeline can have includes."""
        from wetwire_gitlab.pipeline import Include, Pipeline

        pipeline = Pipeline(
            stages=["build"],
            include=[Include(local="/ci/build.yml")],
        )
        assert len(pipeline.include) == 1

    def test_pipeline_default(self):
        """Pipeline can have default job settings."""
        from wetwire_gitlab.pipeline import Default, Image, Pipeline

        pipeline = Pipeline(
            stages=["build"],
            default=Default(image=Image(name="python:3.11")),
        )
        assert pipeline.default.image.name == "python:3.11"
