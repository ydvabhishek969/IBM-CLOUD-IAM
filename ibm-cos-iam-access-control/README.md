# IBM Cloud IAM: Secure Access Control for Cloud Object Storage (COS)

Implements **least-privilege access control** for an IBM Cloud Object Storage bucket
using IBM Cloud IAM **access groups**, **service IDs**, and **bucket-scoped policies**.
Includes automated provisioning (Python SDK), an alternative Infrastructure-as-Code
version (Terraform), and a verification script that *proves* the policies work.

## Architecture

```
 Service ID (reader) ──member──▶ Access Group: cos-readers ──policy: Reader──┐
                                                                             ├─▶ COS bucket (only this bucket)
 Service ID (writer) ──member──▶ Access Group: cos-writers ──policy: Writer──┘
        │
        └── API key ──▶ IAM token (OAuth) ──▶ COS S3-compatible API
```

| Identity | Role   | LIST | GET | PUT | DELETE |
|----------|--------|:----:|:---:|:---:|:------:|
| Reader   | Reader |  ✅  | ✅  | ❌  |   ❌   |
| Writer   | Writer |  ✅  | ✅  | ✅  |   ✅   |

## Project structure

```
src/cos_iam/
  config.py       # env-based settings + CRN parsing
  iam_manager.py  # access groups, service IDs, policies (IBM Platform Services SDK)
  cos_client.py   # ibm_boto3 client using IAM API-key (OAuth) auth
  verify.py       # allow/deny verification matrix
  __main__.py     # CLI
terraform/        # same design as IaC
tests/            # unit tests (no cloud calls)
```

## Prerequisites
- IBM Cloud account, a COS instance and an existing bucket
- Python 3.9+
- An **admin** API key (IAM Administrator + Manager on COS) – used only for setup

## Quick start (Python)

```bash
git clone https://github.com/<you>/ibm-cos-iam-access-control.git
cd ibm-cos-iam-access-control
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in values

export PYTHONPATH=src
python -m cos_iam setup     # create groups, service IDs, policies, API keys
python -m cos_iam verify    # run allow/deny checks (wait ~1 min after setup)
python -m cos_iam cleanup   # remove everything created
```

Expected output of `verify`:
```
PASS  reader  LIST    expected=allow got=allow
PASS  reader  UPLOAD  expected=deny  got=deny
PASS  writer  UPLOAD  expected=allow got=allow
...
ALL CHECKS PASSED
```

## Quick start (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
export TF_VAR_ibmcloud_api_key=<admin key>
terraform init && terraform plan && terraform apply
```

## Security practices demonstrated
- **Least privilege**: policies scoped to a single bucket, not the whole service
- **Group-based access**: permissions attach to groups, never individual users
- **Service IDs** for applications instead of personal API keys
- **No secrets in git**: `.env`, `.secrets/`, and tfstate are gitignored
- Idempotent setup (re-running reuses existing groups/service IDs)

## Ideas for extension
- Add a `Manager` admin group with MFA enforced
- Context-based restrictions (allow only specific IPs/VPCs)
- Trusted profiles for compute identities (no long-lived API keys)
- Activity Tracker / audit logging of access events
- Rotate service ID API keys on a schedule

## Notes
- IAM policy changes can take up to ~1 minute to propagate.
- API keys are only shown once at creation; they are saved to `.secrets/keys.json` (mode 600).
- Review IBM's docs for the latest SDK versions: https://cloud.ibm.com/docs/cloud-object-storage

## License
MIT
