import os

from increment_package_version import get_current_version, increment_version


def test_get_current_version() -> None:
    _ = get_current_version()


def test_get_current_version_return_zero_pre_release_number():
    version = increment_version(version_to_test="0.1.0", commit_msg="prerelease")
    pre_release_number = version.split("a")[1]
    assert pre_release_number == "0"


def test_get_current_version_return_incremented_pre_release_number():
    version = increment_version(version_to_test="0.1.0a0", commit_msg="prerelease")
    pre_release_number = version.split("a")[1]
    assert pre_release_number == "1"


def test_increment_version_major_increment_in_test():
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    expected_new_version = f"{major+1}.0.0a0"
    commit_msg = "This is a major update with breaking changes, in test environment"
    new_version = increment_version(version_to_test=version, commit_msg=commit_msg)
    assert new_version == expected_new_version


def test_increment_version_minor_increment_in_test():
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    expected_new_version = f"{major}.{int(minor)+1}.0a0"
    commit_msg = "This is a minor update without breaking changes, in test environment"
    new_version = increment_version(version_to_test=version, commit_msg=commit_msg)
    assert new_version == expected_new_version


def test_increment_version_patch_increment_in_test():
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    expected_new_version = f"{major}.{minor}.{int(patch)+1}a0"
    commit_msg = "This is a patch with a bugfix"
    new_version = increment_version(version_to_test=version, commit_msg=commit_msg)
    assert new_version == expected_new_version


def test_increment_version_major_increment_in_prod():
    os.environ["MODEL_ENV"] = "test"
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    commit_msg = "This is a major update with breaking changes, in prod environment"
    incremented_version = increment_version(
        version_to_test=version, commit_msg=commit_msg
    )
    os.environ["MODEL_ENV"] = "prod"
    new_version_in_prod = increment_version(version_to_test=incremented_version)
    expected_new_version = f"{major+1}.0.0"
    assert new_version_in_prod == expected_new_version


def test_increment_version_minor_increment_in_prod():
    os.environ["MODEL_ENV"] = "test"
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    commit_msg = "This is a minor update with breaking changes, in prod environment"
    incremented_version = increment_version(
        version_to_test=version, commit_msg=commit_msg
    )
    os.environ["MODEL_ENV"] = "prod"
    new_version_in_prod = increment_version(version_to_test=incremented_version)
    expected_new_version = f"{major}.{minor+1}.0"
    assert new_version_in_prod == expected_new_version


def test_increment_version_patch_increment_in_prod():
    os.environ["MODEL_ENV"] = "test"
    version = "0.1.0"
    major, minor, patch = list(map(int, version.split(".")))
    commit_msg = "This is just a patch in prod"
    incremented_version = increment_version(
        version_to_test=version, commit_msg=commit_msg
    )
    os.environ["MODEL_ENV"] = "prod"
    new_version_in_prod = increment_version(version_to_test=incremented_version)
    expected_new_version = f"{major}.{minor}.{patch+1}"
    assert new_version_in_prod == expected_new_version
