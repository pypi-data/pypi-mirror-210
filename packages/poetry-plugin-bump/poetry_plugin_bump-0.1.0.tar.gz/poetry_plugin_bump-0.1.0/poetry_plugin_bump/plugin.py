import os
from typing import Any

import semver
from cleo.application import Application
from cleo.helpers import argument
from poetry.console.commands.env_command import EnvCommand
from poetry.plugins.application_plugin import ApplicationPlugin


class ExecCommand(EnvCommand):
    name = "bump"
    description = "poetry plugin to bump version"

    arguments = [
        argument(
            "target_version", "target version or patch/minor/major", multiple=False
        ),
    ]

    def exec(self, bin: str, *args: str) -> int:
        ret = self.env.execute(bin, *args)
        if ret:
            exit(ret)

    def handle(self) -> Any:
        pyproject_folder_path = self.poetry.pyproject.file.path.parent
        pyproject_data = self.poetry.pyproject.data

        target: str = self.argument("target_version")
        current_version = pyproject_data["tool"]["poetry"]["version"]

        if target == "major":
            target_version = semver.bump_major(current_version)
        elif target == "minor":
            target_version = semver.bump_minor(current_version)
        elif target == "patch":
            target_version = semver.bump_patch(current_version)
        else:
            target_version = str(semver.VersionInfo.parse(target.lstrip("v")))

        print(target_version)
        self.line(f"bump version to {target_version}")

        os.chdir(pyproject_folder_path)

        self.exec("poetry", "version", target_version)
        self.exec("git", "add", "pyproject.toml")

        commit_message = (
            pyproject_data.get("tool", {})
            .get("poetry-plugin-bump", {})
            .get("commit_msg", "{version}")
        )

        self.exec(
            "git",
            "commit",
            "-m",
            commit_message.format(version=target_version),
        )

        tag_name = (
            pyproject_data.get("tool", {})
            .get("poetry-plugin-bump", {})
            .get("tag_name", "v{version}")
        )

        self.exec(
            "git",
            "tag",
            tag_name.format(version=target_version),
            "-m",
            tag_name.format(version=target_version),
        )

        return


def factory() -> ExecCommand:
    return ExecCommand()


class ExecPlugin(ApplicationPlugin):
    def activate(self, application: Application, *args: Any, **kwargs: Any) -> None:
        application.command_loader.register_factory("bump", factory)
