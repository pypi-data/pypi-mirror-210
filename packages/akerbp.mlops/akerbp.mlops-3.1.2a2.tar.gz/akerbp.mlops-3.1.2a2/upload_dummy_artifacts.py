import os

import akerbp.mlops.model_manager as mm

model_name = "mlopsdemo"
folder_path = "model_artifact"
env = os.environ["MODEL_ENV"]
metadata = {"Description": "Dummy artifacts for mlops demo model"}

mm.setup()
folder_info = mm.upload_new_model_version(model_name, env, folder_path, metadata)
