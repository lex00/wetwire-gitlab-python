"""Tests for template builder module."""


class TestTopologicalSort:
    """Tests for topological sorting of jobs."""

    def test_sort_linear_dependencies(self):
        """Sort jobs with linear dependencies."""
        from wetwire_gitlab.template import topological_sort

        # build -> test -> deploy
        graph = {
            "build": [],
            "test": ["build"],
            "deploy": ["test"],
        }

        result = topological_sort(graph)

        assert result.index("build") < result.index("test")
        assert result.index("test") < result.index("deploy")

    def test_sort_parallel_dependencies(self):
        """Sort jobs with parallel dependencies."""
        from wetwire_gitlab.template import topological_sort

        # build -> test1, test2 -> deploy
        graph = {
            "build": [],
            "test1": ["build"],
            "test2": ["build"],
            "deploy": ["test1", "test2"],
        }

        result = topological_sort(graph)

        assert result.index("build") < result.index("test1")
        assert result.index("build") < result.index("test2")
        assert result.index("test1") < result.index("deploy")
        assert result.index("test2") < result.index("deploy")

    def test_sort_no_dependencies(self):
        """Sort jobs with no dependencies."""
        from wetwire_gitlab.template import topological_sort

        graph = {
            "job1": [],
            "job2": [],
            "job3": [],
        }

        result = topological_sort(graph)

        assert len(result) == 3
        assert set(result) == {"job1", "job2", "job3"}

    def test_sort_complex_graph(self):
        """Sort jobs with complex dependencies."""
        from wetwire_gitlab.template import topological_sort

        # a -> b, c
        # b -> d
        # c -> d
        # d -> e
        graph = {
            "a": [],
            "b": ["a"],
            "c": ["a"],
            "d": ["b", "c"],
            "e": ["d"],
        }

        result = topological_sort(graph)

        assert result.index("a") < result.index("b")
        assert result.index("a") < result.index("c")
        assert result.index("b") < result.index("d")
        assert result.index("c") < result.index("d")
        assert result.index("d") < result.index("e")


class TestCycleDetection:
    """Tests for cycle detection in dependency graphs."""

    def test_detect_simple_cycle(self):
        """Detect a simple two-node cycle."""
        from wetwire_gitlab.template import detect_cycle

        # a -> b -> a
        graph = {
            "a": ["b"],
            "b": ["a"],
        }

        has_cycle, cycle_nodes = detect_cycle(graph)

        assert has_cycle is True
        assert len(cycle_nodes) > 0

    def test_detect_self_cycle(self):
        """Detect a self-referencing cycle."""
        from wetwire_gitlab.template import detect_cycle

        # a -> a
        graph = {
            "a": ["a"],
        }

        has_cycle, cycle_nodes = detect_cycle(graph)

        assert has_cycle is True

    def test_detect_indirect_cycle(self):
        """Detect an indirect cycle."""
        from wetwire_gitlab.template import detect_cycle

        # a -> b -> c -> a
        graph = {
            "a": ["b"],
            "b": ["c"],
            "c": ["a"],
        }

        has_cycle, cycle_nodes = detect_cycle(graph)

        assert has_cycle is True

    def test_no_cycle(self):
        """No cycle in valid dependency graph."""
        from wetwire_gitlab.template import detect_cycle

        graph = {
            "build": [],
            "test": ["build"],
            "deploy": ["test"],
        }

        has_cycle, cycle_nodes = detect_cycle(graph)

        assert has_cycle is False
        assert len(cycle_nodes) == 0


class TestDependencyOrdering:
    """Tests for dependency ordering for YAML generation."""

    def test_order_jobs_for_yaml(self):
        """Order jobs for YAML output."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import order_jobs_for_yaml

        jobs = [
            DiscoveredJob(
                name="deploy",
                variable_name="deploy",
                file_path="jobs.py",
                line_number=3,
                dependencies=["test"],
            ),
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path="jobs.py",
                line_number=1,
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=2,
                dependencies=["build"],
            ),
        ]

        ordered = order_jobs_for_yaml(jobs)

        names = [j.name for j in ordered]
        assert names.index("build") < names.index("test")
        assert names.index("test") < names.index("deploy")

    def test_order_jobs_with_missing_dependency(self):
        """Handle jobs with missing dependencies gracefully."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import order_jobs_for_yaml

        jobs = [
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=1,
                dependencies=["nonexistent"],
            ),
        ]

        # Should not raise, just return jobs (missing deps are ignored)
        ordered = order_jobs_for_yaml(jobs)
        assert len(ordered) == 1


class TestBuildFromGraph:
    """Tests for building dependency graph from jobs."""

    def test_build_graph_from_jobs(self):
        """Build dependency graph from DiscoveredJob list."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import build_graph_from_jobs

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path="jobs.py",
                line_number=1,
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=2,
                dependencies=["build"],
            ),
        ]

        graph = build_graph_from_jobs(jobs)

        assert "build" in graph
        assert "test" in graph
        assert graph["build"] == []
        assert graph["test"] == ["build"]

    def test_build_graph_empty(self):
        """Build graph from empty job list."""
        from wetwire_gitlab.template import build_graph_from_jobs

        graph = build_graph_from_jobs([])

        assert graph == {}


class TestExtractStages:
    """Tests for extracting stages from ordered jobs."""

    def test_extract_stages_from_jobs(self):
        """Extract unique stages in order."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import extract_stages

        # Simulate ordered jobs (already sorted)
        jobs = [
            DiscoveredJob(name="build", variable_name="build", file_path="", line_number=1),
            DiscoveredJob(name="test1", variable_name="test1", file_path="", line_number=2),
            DiscoveredJob(name="test2", variable_name="test2", file_path="", line_number=3),
            DiscoveredJob(name="deploy", variable_name="deploy", file_path="", line_number=4),
        ]

        # Provide a mapping of job names to stages
        job_stages = {
            "build": "build",
            "test1": "test",
            "test2": "test",
            "deploy": "deploy",
        }

        stages = extract_stages(jobs, job_stages)

        assert stages == ["build", "test", "deploy"]

    def test_extract_stages_preserves_order(self):
        """Stages are in dependency order, not alphabetical."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import extract_stages

        jobs = [
            DiscoveredJob(name="z_job", variable_name="z", file_path="", line_number=1),
            DiscoveredJob(name="a_job", variable_name="a", file_path="", line_number=2),
        ]

        job_stages = {
            "z_job": "zebra",
            "a_job": "alpha",
        }

        stages = extract_stages(jobs, job_stages)

        # Order should be based on job order, not alphabetical
        assert stages == ["zebra", "alpha"]
