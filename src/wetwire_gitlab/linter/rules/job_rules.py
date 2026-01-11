"""Job validation rules.

These rules check for common issues in Job definitions, such as missing
required fields or potentially problematic configurations.
"""

import ast
from pathlib import Path

from ...contracts import LintIssue


class WGL011MissingStage:
    """WGL011: Job definitions should have an explicit stage."""

    code = "WGL011"
    message = "Job should have an explicit stage"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without stage keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_stage = False
                    for kw in node.keywords:
                        if kw.arg == "stage":
                            has_stage = True
                            break
                    if not has_stage:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL014MissingScript:
    """WGL014: Job should have script, trigger, or extends."""

    code = "WGL014"
    message = "Job should have script, trigger, or extends"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without script, trigger, or extends."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_script = False
                    has_trigger = False
                    has_extends = False
                    for kw in node.keywords:
                        if kw.arg == "script":
                            has_script = True
                        elif kw.arg == "trigger":
                            has_trigger = True
                        elif kw.arg == "extends":
                            has_extends = True
                    if not has_script and not has_trigger and not has_extends:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL015MissingName:
    """WGL015: Job should have explicit name."""

    code = "WGL015"
    message = "Job should have explicit name"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without name keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_name = False
                    for kw in node.keywords:
                        if kw.arg == "name":
                            has_name = True
                            break
                    if not has_name:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL017EmptyRulesList:
    """WGL017: Empty rules list means job never runs."""

    code = "WGL017"
    message = "Empty rules list means job never runs"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for empty rules list in Job definitions."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "rules" and isinstance(kw.value, ast.List):
                            if len(kw.value.elts) == 0:
                                issues.append(
                                    LintIssue(
                                        code=self.code,
                                        message=self.message,
                                        file_path=str(file_path),
                                        line_number=kw.value.lineno,
                                        column=kw.value.col_offset,
                                    )
                                )

        return issues


class WGL018NeedsWithoutStage:
    """WGL018: Jobs with needs should specify stage."""

    code = "WGL018"
    message = "Jobs with needs should specify stage for clarity"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls with needs but without stage."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_needs = False
                    has_stage = False
                    for kw in node.keywords:
                        if kw.arg == "needs":
                            has_needs = True
                        elif kw.arg == "stage":
                            has_stage = True
                    if has_needs and not has_stage:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL019ManualWithoutAllowFailure:
    """WGL019: Manual jobs should consider allow_failure."""

    code = "WGL019"
    message = "Manual jobs should consider allow_failure to avoid blocking pipelines"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for manual jobs without allow_failure."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    is_manual = False
                    has_allow_failure = False
                    when_lineno = 0
                    when_col = 0

                    for kw in node.keywords:
                        if kw.arg == "when":
                            # Check for string "manual"
                            if isinstance(kw.value, ast.Constant):
                                if kw.value.value == "manual":
                                    is_manual = True
                                    when_lineno = kw.value.lineno
                                    when_col = kw.value.col_offset
                            # Check for When.MANUAL attribute access
                            elif isinstance(kw.value, ast.Attribute):
                                if kw.value.attr == "MANUAL":
                                    is_manual = True
                                    when_lineno = kw.value.lineno
                                    when_col = kw.value.col_offset
                        elif kw.arg == "allow_failure":
                            has_allow_failure = True

                    if is_manual and not has_allow_failure:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=when_lineno or node.lineno,
                                column=when_col or node.col_offset,
                            )
                        )

        return issues


class WGL020AvoidNestedJobConstructors:
    """WGL020: Avoid nested Job constructors in lists."""

    code = "WGL020"
    message = "Avoid inline Job constructors; extract to named variables"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for nested Job() calls in needs/dependencies lists."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    # Check needs and dependencies keywords
                    for kw in node.keywords:
                        if kw.arg in ("needs", "dependencies"):
                            if isinstance(kw.value, ast.List):
                                # Check each element in the list
                                for elt in kw.value.elts:
                                    if isinstance(elt, ast.Call):
                                        if (
                                            isinstance(elt.func, ast.Name)
                                            and elt.func.id == "Job"
                                        ):
                                            issues.append(
                                                LintIssue(
                                                    code=self.code,
                                                    message=self.message,
                                                    file_path=str(file_path),
                                                    line_number=elt.lineno,
                                                    column=elt.col_offset,
                                                )
                                            )

        return issues


class WGL022AvoidDuplicateNeeds:
    """WGL022: Avoid duplicate entries in needs/dependencies."""

    code = "WGL022"
    message = "Duplicate entries in needs/dependencies list"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for duplicate entries in needs/dependencies lists."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    # Check needs and dependencies keywords
                    for kw in node.keywords:
                        if kw.arg in ("needs", "dependencies"):
                            if isinstance(kw.value, ast.List):
                                seen: set[str] = set()
                                for elt in kw.value.elts:
                                    # Only check string constants
                                    if isinstance(elt, ast.Constant) and isinstance(
                                        elt.value, str
                                    ):
                                        if elt.value in seen:
                                            issues.append(
                                                LintIssue(
                                                    code=self.code,
                                                    message=f"{self.message}: '{elt.value}' appears multiple times",
                                                    file_path=str(file_path),
                                                    line_number=elt.lineno,
                                                    column=elt.col_offset,
                                                )
                                            )
                                        else:
                                            seen.add(elt.value)

        return issues


class WGL023MissingImageForScriptJobs:
    """WGL023: Warn on missing image for script jobs."""

    code = "WGL023"
    message = "Consider specifying an image for script jobs"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for jobs with script but no image."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_script = False
                    has_trigger = False
                    has_image = False

                    for kw in node.keywords:
                        if kw.arg == "script":
                            has_script = True
                        elif kw.arg == "trigger":
                            has_trigger = True
                        elif kw.arg == "image":
                            has_image = True

                    # Only flag if has script (not trigger) and no image
                    if has_script and not has_trigger and not has_image:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                                severity="info",
                            )
                        )

        return issues


class WGL024CircularDependency:
    """WGL024: Detect circular dependencies in job needs."""

    code = "WGL024"
    message = "Circular dependency detected"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for circular dependencies in job needs.

        Uses DFS with recursion stack to detect cycles in the dependency graph.
        """
        issues: list[LintIssue] = []

        # First pass: collect all Job definitions
        # Maps job_name -> (node, variable_name)
        jobs: dict[str, tuple[ast.Call, str | None]] = {}
        # Maps variable_name -> job_name
        var_to_job: dict[str, str] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Handle: job_a = Job(name="a", ...)
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    var_name = node.targets[0].id
                    if isinstance(node.value, ast.Call):
                        if (
                            isinstance(node.value.func, ast.Name)
                            and node.value.func.id == "Job"
                        ):
                            job_name = self._get_job_name(node.value)
                            if job_name:
                                jobs[job_name] = (node.value, var_name)
                                var_to_job[var_name] = job_name

        # Second pass: build dependency graph
        # Maps job_name -> list of needed job names
        dependencies: dict[str, list[str]] = {}

        for job_name, (node, _) in jobs.items():
            needs = self._get_needs(node, var_to_job)
            dependencies[job_name] = needs

        # Detect cycles using DFS
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []
        reported_cycles: set[tuple[str, ...]] = set()

        def find_cycle(job: str) -> list[str] | None:
            """DFS to find a cycle starting from job."""
            if job in rec_stack:
                # Found a cycle - extract it from path
                cycle_start = path.index(job)
                return path[cycle_start:] + [job]

            if job in visited:
                return None

            visited.add(job)
            rec_stack.add(job)
            path.append(job)

            for dep in dependencies.get(job, []):
                cycle = find_cycle(dep)
                if cycle:
                    return cycle

            path.pop()
            rec_stack.remove(job)
            return None

        for job_name in jobs:
            if job_name not in visited:
                cycle = find_cycle(job_name)
                if cycle:
                    # Normalize cycle to avoid duplicate reports
                    # e.g., [a, b, c, a] and [b, c, a, b] are the same cycle
                    cycle_core = cycle[:-1]  # Remove the repeated start
                    min_idx = cycle_core.index(min(cycle_core))
                    normalized = tuple(
                        cycle_core[min_idx:] + cycle_core[:min_idx]
                    )

                    if normalized not in reported_cycles:
                        reported_cycles.add(normalized)
                        cycle_str = " -> ".join(cycle)
                        # Find the line number of the first job in the cycle
                        first_job = cycle[0]
                        job_node, _ = jobs[first_job]
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=f"{self.message}: {cycle_str}",
                                file_path=str(file_path),
                                line_number=job_node.lineno,
                                column=job_node.col_offset,
                            )
                        )
                    # Reset for next search
                    visited.clear()
                    rec_stack.clear()
                    path.clear()

        return issues

    def _get_job_name(self, node: ast.Call) -> str | None:
        """Extract the job name from a Job() call."""
        for kw in node.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, str):
                    return kw.value.value
        return None

    def _get_needs(self, node: ast.Call, var_to_job: dict[str, str]) -> list[str]:
        """Extract the list of needed job names from a Job() call.

        Handles both string literals and variable references.
        """
        needs: list[str] = []
        for kw in node.keywords:
            if kw.arg == "needs" and isinstance(kw.value, ast.List):
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        # String literal: needs=["build"]
                        needs.append(elt.value)
                    elif isinstance(elt, ast.Name):
                        # Variable reference: needs=[build_job]
                        var_name = elt.id
                        if var_name in var_to_job:
                            needs.append(var_to_job[var_name])
        return needs
