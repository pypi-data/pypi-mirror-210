# setup.py
import re
from copy import deepcopy
from pathlib import Path

from akerbp.mlops import __version__ as version
from akerbp.mlops.core.config import (
    generate_default_project_settings,
    validate_user_settings,
)
from akerbp.mlops.core.logger import get_logger
from akerbp.mlops.deployment.helpers import replace_string_file, to_folder

logger = get_logger(__name__)


def update_mlops_version_in_pipeline(folder_path: Path = Path(".")) -> None:
    """Update MLOps settings by overwriting the package version number.
    First, it will go through the pipeline definition and remove any quoatation mark prefix to akerbp.mlops
    (to make it robust against updating from previous versions),
    before it will replace the version number with whatever version the caller has on his/her local machine.

    Args:
        folder_path (Path, optional): Path to folder containing the pipeline file. Defaults to Path(".").
    """
    platform = input("Deployment platform (cdf, gcp): ").lower().strip()
    if platform not in ["cdf", "gcp"]:
        raise ValueError(f"Deployment platform {platform} not supported")
    pipeline_file = Path("bitbucket-pipelines.yml")
    pipeline_path = folder_path / pipeline_file
    replacement_package = f"akerbp.mlops[{platform}]=={version}"
    pattern_package = re.compile(
        r"akerbp\.mlops(?:\[(cdf|gcp)\])?==\d+\.\d+\.\d+(?:(a|alpha)\d+)?"
    )
    replacement_version = f"Version {version}"
    pattern_version = re.compile("Version \S{5,}")
    with pipeline_path.open() as f:
        pipeline = f.read()
        new_pipeline = re.sub(
            pattern_version,
            replacement_version,
            re.sub(
                pattern_package,
                replacement_package,
                pipeline,
            ),
        )
    with pipeline_path.open("w") as f:
        f.write(new_pipeline)
    if new_pipeline == pipeline:
        logger.info("No changes to the MLOps version were made in the pipeline file")
    else:
        logger.info("MLOps version successfully updated in pipeline file")


def remove_references_to_old_bash_script(folder_path: Path = Path(".")) -> None:
    """Remove references to the old bash script in the pipeline file

    Args:
        folder_path (Path, optional): Path to folder containing the pipeline file. Defaults to Path(".").
    """
    pipeline_file = Path("bitbucket-pipelines.yml")
    pipeline_path = folder_path / pipeline_file
    replacement_pattern = re.compile("bash deploy_.+.sh")
    with pipeline_path.open() as f:
        pipeline = f.read()
        matches = list(re.finditer(replacement_pattern, pipeline))
        if matches:
            new_pipeline = deepcopy(pipeline)
            for match in matches:
                logger.info(f"Removing reference to old bash script {match}")
                match_string = match.group()
                script_name = (
                    match_string.replace("bash", "").replace(".sh", "").strip()
                )
                new_pipeline = new_pipeline.replace(match_string, script_name)
            with pipeline_path.open("w") as f:
                f.write(new_pipeline)
            logger.info(
                "References to old bash script successfully removed from pipeline file"
            )
        else:
            logger.info("No references to old bash scripts found")


def generate_pipeline(folder_path: Path = Path(".")) -> None:
    """Generate pipeline definition from template

    Args:
        folder_path (Path, optional): Path to folder that should contain the pipeline file. Defaults to Path(".").
    """
    pipeline_file = Path("bitbucket-pipelines.yml")
    pipeline_path = folder_path / pipeline_file
    pipeline = ("akerbp.mlops.deployment", pipeline_file)
    to_folder(pipeline, folder_path)
    replace_string_file("MLOPS_VERSION", version, pipeline_path)
    logger.info("Pipeline definition generated")


def setup_pipeline(folder_path: Path = Path(".")) -> None:
    """
    Set up pipeline file in the given folder.
    Update MLOps package version in the pipeline file if it exists, or generate from template if it doesn't.

    Args:
        folder_path (Path, optional): Path to folder that should contain the pipeline file. Defaults to Path(".").
    """
    pipeline_file = Path("bitbucket-pipelines.yml")
    pipeline_path = folder_path / pipeline_file
    if pipeline_path.exists():
        logger.info(f"Update MLOps version in pipeline definition to {version}")
        update_mlops_version_in_pipeline()
        remove_references_to_old_bash_script()
    else:
        logger.info("Generating pipeline definition from template")
        generate_pipeline()


if __name__ == "__main__":
    logger = get_logger(name="akerbp.mlops.deployment.setup.py")

    setup_pipeline()
    if Path("mlops_settings.yaml").exists():
        logger.info("Validate settings file")
        validate_user_settings()
    else:
        logger.info("Create settings file template")
        generate_default_project_settings()
    logger.info("Done!")
