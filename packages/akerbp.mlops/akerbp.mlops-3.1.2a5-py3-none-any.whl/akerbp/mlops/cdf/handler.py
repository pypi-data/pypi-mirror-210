# handler.py

import sys
import time
import traceback
from contextlib import redirect_stderr
from importlib import import_module
from typing import Any, Dict, Union


def handle(
    data: Dict, secrets: Dict, function_call_info: Dict
) -> Union[Any, Dict[Any, Any]]:
    """Handler function for deploying models to CDF

    Args:
        data (Dict): model payload
        secrets (Dict): Client secrets to be used by the service
        function_call_info (Dict): dictionary containing function id and whether the function call is scheduled

    Returns:
        Union[Any, Dict[Any, Any]]: Function call response
    """
    try:
        with redirect_stderr(sys.stdout):
            import warnings

            import akerbp.mlops.cdf.helpers as cdf
            from akerbp.mlops.core.config import ENV_VARS
            from akerbp.mlops.core.logger import get_logger

            def customwarn(message, category, filename, lineno, file=None, line=None):
                sys.stdout.write(
                    warnings.formatwarning(message, category, filename, lineno)
                )

            warnings.showwarning = customwarn

            service_name = ENV_VARS.service_name
            service = import_module(f"akerbp.mlops.services.{service_name}").service

            logger = get_logger(__name__)
            cdf.client_secrets = secrets
            logger.info("Prediction request received, starting model prediction")
            logger.info(
                "Setting up CDF Client with access to Data, Files and Functions"
            )
            cdf.set_up_cdf_client(context="read")
            logger.info("Set up complete")
            if data:
                logger.info("Calling model using provided payload")
                start = time.time()
                output = service(data, secrets)
                elapsed = time.time() - start
                logger.info(f"Model call complete. Duration: {elapsed:.2f} s")
            else:
                logger.info("Calling model with empty payload")
                output = dict(status="ok")
                logger.info("Model call complete")
            logger.info("Querying metadata from the function call")
            function_call_metadata = cdf.get_function_call_response_metadata(
                function_call_info["function_id"]
            )
            logger.info("Function call metadata obtained")
            logger.info("Writing function call metadata to response")
            output.update(dict(metadata=function_call_metadata))
            logger.info("Function call metadata successfully written to response")
            return output
    except Exception:
        trace = traceback.format_exc()
        error_message = ""
        try:
            error_message = f"{service_name} service failed.\n{trace}"
            logger.critical(error_message)
        except UnboundLocalError:
            if not error_message:
                error_message = "Service failed. \n{trace}"
            pass  # Unable to log error just return error message
        return dict(status="error", error_message=error_message)
