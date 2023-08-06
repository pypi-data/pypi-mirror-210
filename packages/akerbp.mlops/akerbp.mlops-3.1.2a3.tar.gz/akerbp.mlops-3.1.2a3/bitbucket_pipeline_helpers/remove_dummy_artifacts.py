import os

import akerbp.mlops.model_manager as mm
from akerbp.mlops.cdf.helpers import delete_file

mm.setup()
env = os.environ["MODEL_ENV"]
model_name = "mlopsdemo"
version = mm.get_latest_model_in_env(model_name, env)
delete_file(id={"external_id": f"{model_name}/{env}/{version}"})
