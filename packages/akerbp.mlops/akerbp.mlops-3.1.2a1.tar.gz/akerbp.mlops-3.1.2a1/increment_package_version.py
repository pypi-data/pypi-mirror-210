import os
from subprocess import check_output


def get_current_version() -> str:
    """Get the current version of the package based on the latest release tag in git."""
    version = (
        check_output(["git", "describe", "--tags", "--abbrev=0"])
        .decode("ascii")
        .strip()
    )
    return version


def increment_version(
    version_to_test: str = "",
    commit_msg: str = "",
) -> str:
    """Increment version number by specifying type of update in the commit message.
    The function extracts the current version from a text file, examines the latest commit
    and increment the version number based on the content of the commit message and the environment.
    The updated version number is then updated in the text file keeping track of the current
    version of the package.

    The version number is tagged as a pre-release if the package is deployed in a test or dev environment.

    We increment the package version according to the following rules based on the commit message:
        - If commit message includes the word "major", increment MAJOR number
        - If commit message includes the word "minor", increment MINOR number
        - If commit message includes neither "major" nor "minor", increment PATCH number
        - Do not increment MAJOR, MINOR nor PATCH if the commit message includes the word "pre-release",
            only increment the pre-release number in this case to avoid unnecessary bumps.
    Returns:
        str: new version number
    """
    ENV = os.environ["MODEL_ENV"]
    if version_to_test:
        version = version_to_test
        commit_msg = commit_msg.strip().lower()
    else:
        version = get_current_version()
        commit_msg = (
            check_output(["git", "log", "-1", "--pretty=%B"]).decode().strip().lower()
        )
    if ENV == "prod":
        return version.split("a")[0]
    else:
        # Increment the package version based on the commit message in dev and test, and tag as pre-release
        major, minor, patch = version.split(".")
        if "a" in patch:
            is_pre_release = True
            patch, pre_release_version = patch.split("a")
        else:
            is_pre_release = False
            pre_release_version = None
        words_in_commit_msg = commit_msg.split()

        # Remove special characters from commit message
        for i, word in enumerate(words_in_commit_msg):
            alphanumeric = [char for char in word if char.isalnum()]
            word = "".join(alphanumeric)
            words_in_commit_msg[i] = word
        # Increment version based on commit message; Avoid incrementing if we specify to increment a pre-release
        if "prerelease" not in words_in_commit_msg:
            if "major" in words_in_commit_msg:
                major = str(int(major) + 1)
                minor, patch = "0", "0"
            elif "minor" in words_in_commit_msg:
                minor = str(int(minor) + 1)
                patch = "0"
            elif "patch" in words_in_commit_msg:
                patch = str(int(patch) + 1)
            else:
                raise ValueError(
                    "Commit message must include either major, minor, or patch keyword if prerelease is not in commit message!"
                )

        new_version = f"{major}.{minor}.{patch}"
        # Tag version number with pre-release, increment pre-release number
        new_version += "a"
        if is_pre_release and pre_release_version is not None:
            pre_release_version_ = int(pre_release_version) + 1
            new_version += str(pre_release_version_)
        else:
            new_version += "0"

        return new_version


if __name__ == "__main__":
    print(increment_version())
