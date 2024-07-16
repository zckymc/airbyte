#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import dagger
import os
import re
import toml
from typing import TYPE_CHECKING, Optional

from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.helpers import git
from pipelines.helpers.connectors import cdk_helpers
from pipelines.models.steps import Step, StepResult, StepStatus
from pipelines.airbyte_ci.connectors.up_to_date.steps import PoetryUpdate

if TYPE_CHECKING:
    from anyio import Semaphore


class SetCDKVersion(Step):
    context: ConnectorContext
    title = "Set CDK Version"

    def __init__(
        self,
        context: ConnectorContext,
        new_version: str,
    ) -> None:
        super().__init__(context)
        self.new_version = new_version

    async def _run(self) -> StepResult:
        context = self.context

        try:
            og_connector_dir = await context.get_connector_dir()
            print(f"Original connector directory: {og_connector_dir}")
            if self.context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                updated_connector_dir = await self.upgrade_cdk_version_for_python_connector(og_connector_dir)
            elif self.context.connector.language is ConnectorLanguage.JAVA:
                updated_connector_dir = await self.upgrade_cdk_version_for_java_connector(og_connector_dir)
            else:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"No CDK for connector {self.context.connector.technical_name} of written in {self.context.connector.language}",
                )

            if updated_connector_dir is None:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stderr=f"Could not set CDK version for connector {self.context.connector.technical_name}",
                )
            

            print(f"Updated connector directory: {updated_connector_dir}")

            diff = og_connector_dir.diff(updated_connector_dir)
            exported_successfully = await diff.export(os.path.join(git.get_git_repo_path(), context.connector.code_directory))
            if not exported_successfully:
                return StepResult(
                    step=self,
                    status=StepStatus.FAILURE,
                    stdout="Could not export diff to local git repo.",
                )
            return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"Updated CDK version to {self.new_version}", output=diff)
        except ValueError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=f"Could not set CDK version: {e}",
                exc_info=e,
            )
        except TypeError as e:
            return StepResult(
                step=self,
                status=StepStatus.FAILURE,
                stderr=str(e),
                exc_info=e,
            )

    async def upgrade_cdk_version_for_java_connector(self, og_connector_dir: Directory) -> Directory:
        if "build.gradle" not in await og_connector_dir.entries():
            raise ValueError(f"Java connector {self.context.connector.technical_name} does not have a build.gradle file.")

        build_gradle = og_connector_dir.file("build.gradle")
        build_gradle_content = await build_gradle.contents()

        old_cdk_version_required = re.search(r"cdkVersionRequired *= *'(?P<version>[0-9]*\.[0-9]*\.[0-9]*)?'", build_gradle_content)
        # If there is no airbyte-cdk dependency, add the version
        if old_cdk_version_required is None:
            raise ValueError("Could not find airbyte-cdk dependency in build.gradle")

        if self.new_version == "latest":
            new_version = await cdk_helpers.get_latest_java_cdk_version(self.context.get_repo_dir())
        else:
            new_version = self.new_version

        updated_build_gradle = build_gradle_content.replace(old_cdk_version_required.group("version"), new_version)

        use_local_cdk = re.search(r"useLocalCdk *=.*", updated_build_gradle)
        if use_local_cdk is not None:
            updated_build_gradle = updated_build_gradle.replace(use_local_cdk.group(), "useLocalCdk = false")

        return og_connector_dir.with_new_file("build.gradle", updated_build_gradle)

    async def upgrade_cdk_version_for_python_connector(self, og_connector_dir: Directory) -> Optional[Directory]:
        context = self.context
        og_connector_dir = await context.get_connector_dir()


        # Verify that the connector uses poetry for dependency management
        if "pyproject.toml" not in await og_connector_dir.entries():
            raise ValueError(f"Could not find pyproject.toml file for {self.context.connector.technical_name}.")

        pyproject_toml = og_connector_dir.file("pyproject.toml")
        pyproject_content = await pyproject_toml.contents()
        pyproject_data = toml.loads(pyproject_content)

        # Validate that the airbyte-cdk dependency is already present in the pyproject.toml file
        deps = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        airbyte_cdk_dependency = deps.get("airbyte-cdk")

        if not airbyte_cdk_dependency:
            raise ValueError("Could not find the airbyte-cdk dependency in pyproject.toml")
        
        if self.new_version == "latest":
            new_version = cdk_helpers.get_latest_python_cdk_version()
        else:
            new_version = self.new_version

        # Update the dependency version
        deps["airbyte-cdk"] = f"{new_version}"

        updated_pyproject_toml_content = toml.dumps(pyproject_data)
        updated_connector_dir = og_connector_dir.with_new_file("pyproject.toml", updated_pyproject_toml_content)

        # Now handle the poetry lock update within a container
        base_image_name = self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        base_container = self.dagger_client.container(platform=LOCAL_BUILD_PLATFORM).from_(base_image_name)
        connector_container = base_container.with_mounted_directory("/connector", updated_connector_dir).with_workdir("/connector")
    
        try:
        # Run poetry lock to update the lock file
            connector_container = await connector_container.with_exec(["poetry", "lock"])
            self.logger.info(await connector_container.stdout())
        except dagger.ExecError as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stderr=str(e))

        return StepResult(step=self, status=StepStatus.SUCCESS, output=connector_container.directory("."))


async def run_connector_cdk_upgrade_pipeline(
    context: ConnectorContext,
    semaphore: Semaphore,
    target_version: str,
) -> ConnectorReport:
    """Run a pipeline to upgrade the CDK version for a single connector.

    Args:
        context (ConnectorContext): The initialized connector context.

    Returns:
        Report: The reports holding the CDK version set results.
    """
    async with semaphore:
        steps_results = []
        report = None
        async with context:
            set_cdk_version = SetCDKVersion(context, target_version)
            set_cdk_version_result = await set_cdk_version.run()
            steps_results.append(set_cdk_version_result)
            print(f"Set CDK version result: {set_cdk_version_result}")

            if set_cdk_version_result.success:
                updated_connector_dir = set_cdk_version_result.output
                if not isinstance(updated_connector_dir, dagger.Directory):
                    raise TypeError(f"Expected updated_connector_dir to be Directory, but got {type(updated_connector_dir)}")

            if set_cdk_version_result.success and context.connector.language in [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]:
                poetry_update = PoetryUpdate(context, specific_dependencies=[], connector_directory=set_cdk_version_result.output)
                poetry_update_result = await poetry_update.run()
                steps_results.append(poetry_update_result)
                print(f"Poetry update result: {poetry_update_result}")

            report = ConnectorReport(context, steps_results, name="CONNECTOR VERSION CDK UPGRADE RESULTS")
            context.report = report
                
    return report
