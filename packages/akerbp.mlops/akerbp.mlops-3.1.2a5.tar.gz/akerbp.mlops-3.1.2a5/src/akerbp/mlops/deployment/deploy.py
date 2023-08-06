"""
deploy.py

Deploy services in either Google Cloud Run or CDF Functions.
Model registry uses CDF Files.
"""
import os
import traceback
from pathlib import Path
from typing import List

import akerbp.mlops.model_manager as mm
from akerbp.mlops import __version__ as package_version
from akerbp.mlops.core import config
from akerbp.mlops.core.config import ServiceSettings

# Global variables
from akerbp.mlops.core.logger import get_logger
from akerbp.mlops.deployment import helpers

logger = get_logger(__name__)


def deploy_model(
    model_settings: ServiceSettings,
) -> str:
    """
    Deploy a model.

    This will create a deployment folder and change current working directory
    to it.

    Return "OK" if deployment was successful, otherwise return a string with the traceback for the failed deployment

    Args:
        model_settings (ServiceSettings): settings for the model service
        platform_methods (dict): where key is the platform and value is a tuple with deploy and test functions.
            Defaults to the globally set platform_methods variable.

    Returns:
        (str): status of the deployment
    """
    c = model_settings
    try:
        original_req_file = c.req_file
        envs = config.ENV_VARS
        env = envs.model_env
        testing_only = eval(envs.testing_only)
        local_deployment = eval(envs.local_deployment)
        service_name = envs.service_name
        platform = envs.platform
        if service_name is None:
            raise ValueError(
                "SERVICE_NAME environment variable must be set to either 'prediction' or 'training'"
            )
        deployment_folder = helpers.deployment_folder_path(c.model_name)
        function_name = f"{c.model_name}-{service_name}-{env}"

        # Handle mlops internal testing settings
        mlops_testing = os.environ.get("LOCAL_MLOPS_TESTING", False)

        logger.info(
            f"Starting deployment and/or testing of model {c.human_friendly_model_name}"
        )

        if (service_name == "prediction") and c.artifact_folder:
            if platform == "cdf" or platform == "local":
                mm.set_active_dataset(c.dataset)
                c.model_id = mm.set_up_model_artifact(c.artifact_folder, c.model_name)

        logger.info("Create deployment folder and move required files/folders")
        deployment_folder.mkdir()
        # Write settings to deployment folder
        config.store_service_settings(
            c, deployment_folder / "mlops_service_settings.yaml"
        )
        logger.info("Service settings %s", c)
        # Update requirements file with mlops version
        req_file = helpers.create_temporary_copy(c.req_file)
        c.req_file = req_file

        helpers.set_mlops_import(
            req_file=c.req_file,
            platform=c.platform,
            deployment_folder=deployment_folder if mlops_testing else None,
        )
        helpers.copy_to_deployment_folder(c.files, deployment_folder)

        logger.info(f"cd {deployment_folder}")
        os.chdir(deployment_folder)

        # Local testing - for MODEL_ENV=dev and LOCAL_DEPLOYMENT=False
        if envs.model_env == "dev" and envs.local_deployment == "False":
            c.platform = "local"
        if c.platform == "local":
            if c.test_file:
                logger.info("Performing local testing")
                helpers.run_tests(
                    c,
                    setup_venv=True,
                    deploy=False,
                )
            else:
                logger.warning(
                    "No test file specified in the settings, skipping local tests."
                )

        # Deploy to CDF
        elif c.platform == "cdf":
            if (env == "test" or env == "prod") and testing_only:

                logger.info(
                    f"Running tests for model {c.human_friendly_model_name} in {env}, will not deploy"
                )
                helpers.run_tests(c, setup_venv=True, deploy=False)
            elif (
                (env == "test" or env == "prod") and not testing_only
            ) or local_deployment:
                helpers.do_deploy(
                    c,
                    env,
                    service_name,
                    function_name,
                    deployment_folder,
                    setup_venv=True,
                )
            else:
                logger.warning(
                    f"Will not run tests nor deploy model(s), check your environment variables: {config.ENV_VARS}"
                )
        return "OK"
    except (Exception, KeyboardInterrupt):
        # Remove deployment folder if it exists
        helpers.rm_deployment_folder(c.model_name)
        # Remove temporary requirements file if it exists
        if c.req_file != original_req_file:
            req_file = Path(c.req_file).resolve()
            logger.info("Removing temporary requirements file %s", req_file)
            if req_file.exists():
                req_file.unlink()
        trace = traceback.format_exc()
        return f"Model failed to deploy and/or tests failed! See the following traceback for more info: \n\n{trace}"


def deploy(project_settings: List[ServiceSettings]) -> None:
    """
    Deploy a machine learning project that potentially contains multiple models.
    Deploy each model in the settings and make sure that if one model fails it
    does not affect the rest. At the end, if any model failed, it raises an
    exception with a summary of all models that failed.

    Args:
        Project settings as described by the user in the config file.

    Raises:
        Exception: If any model failed to deploy.
    """
    failed_models = {}
    cwd_path = Path.cwd()

    for c in project_settings:
        status = deploy_model(c)
        if status != "OK":
            logger.error(status)
            failed_models[c.human_friendly_model_name] = status

        logger.info("cd ..")
        os.chdir(cwd_path)
        helpers.rm_deployment_folder(c.model_name)

    if failed_models:
        for model, message in failed_models.items():
            logger.warning(f"Model {model} failed: {message}")
        raise Exception("At least one model failed.")


def main() -> None:
    logger = get_logger(name="akerbp.mlops.deployment.deploy.py")
    logger.info(
        f"Deploying prediction service using MLOps framework version {package_version}"
    )
    mm.setup()
    settings = config.read_project_settings()
    deploy(settings)


if __name__ == "__main__":
    main()
