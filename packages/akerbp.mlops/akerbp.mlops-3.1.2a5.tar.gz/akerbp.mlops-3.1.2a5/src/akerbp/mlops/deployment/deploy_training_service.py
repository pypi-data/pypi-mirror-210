# This can be run after package has been installed
def main() -> None:
    import os

    os.environ["SERVICE_NAME"] = "training"
    import akerbp.mlops.deployment.deploy as deploy

    deploy.main()


if __name__ == "__main__":
    main()
