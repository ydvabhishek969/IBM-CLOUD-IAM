import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cos_iam.config import ConfigError, guid_from_crn  # noqa: E402
from cos_iam.iam_manager import ROLE_CRNS, build_bucket_policy_payload  # noqa: E402

CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/abc123:11111111-2222-3333-4444-555555555555::"


def test_guid_from_crn():
    assert guid_from_crn(CRN) == "11111111-2222-3333-4444-555555555555"


def test_guid_from_bad_crn():
    with pytest.raises(ConfigError):
        guid_from_crn("not-a-crn")


def test_policy_is_scoped_to_one_bucket():
    attrs = {a["name"]: a["value"] for a in build_bucket_policy_payload("acct", "guid", "bkt")}
    assert attrs["resourceType"] == "bucket"
    assert attrs["resource"] == "bkt"
    assert attrs["serviceName"] == "cloud-object-storage"


def test_least_privilege_roles_exist():
    assert "Reader" in ROLE_CRNS and "Writer" in ROLE_CRNS
