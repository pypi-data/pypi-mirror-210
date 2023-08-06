# This can be run after package has been installed
def main():
    import os

    os.environ["SERVICE_NAME"] = "prediction"
    import akerbp.mlops.deployment.deploy as deploy

    deploy.main()
