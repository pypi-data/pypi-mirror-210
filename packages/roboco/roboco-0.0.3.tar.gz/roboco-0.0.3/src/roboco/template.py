# ruff: noqa: T201
import os
import shutil
from importlib.resources import files
from pathlib import Path

from roboco import __version__
from roboco.configurations import ProjectConfiguration, realsense_camera, ur5


def generate_from_template(configuration: ProjectConfiguration):
    dockerfile_template = f"{configuration.robot.key}/Dockerfile.{configuration.ros_distro}"
    print(f"Generating from {dockerfile_template}")
    package_dir = files("roboco")
    run_script_dest = "./run.py"
    dockerfile_dest = "./Dockerfile"
    run_script_src = f"{package_dir}/run.py"
    dockerfile_src = f"{package_dir}/templates/{dockerfile_template}"

    shutil.copyfile(dockerfile_src, dockerfile_dest)
    shutil.copyfile(run_script_src, run_script_dest)
    os.chmod("run.py", 0o755)  # noqa: S103

    replace_string_in_file(Path(run_script_dest), "please_change_project_name", configuration.name)
    add_to_beginning_of_file(Path(dockerfile_dest), f"# Generated using roboco version {__version__}\n")


def replace_string_in_file(file: Path, old: str, new: str):
    """Removes the old string and inserts the new string in its place."""
    with open(file) as f:
        new_text = f.read().replace(old, new)
    with open(file, "w") as f:
        f.write(new_text)


def add_to_beginning_of_file(file: Path, new: str):
    """Adds the new string to the beginning of the file."""
    with open(file) as f:
        old_text = f.read()
    with open(file, "w") as f:
        f.write(new)
        f.write(old_text)


if __name__ == "__main__":
    test_config = ProjectConfiguration("my_test_project", ur5, "noetic", [realsense_camera])
    generate_from_template(test_config)
