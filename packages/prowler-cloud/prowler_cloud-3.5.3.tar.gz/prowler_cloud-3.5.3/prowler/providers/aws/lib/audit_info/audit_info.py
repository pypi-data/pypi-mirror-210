from boto3 import session
from botocore.config import Config

from prowler.providers.aws.lib.audit_info.models import AWS_Assume_Role, AWS_Audit_Info

# Default Current Audit Info
current_audit_info = AWS_Audit_Info(
    original_session=None,
    audit_session=session.Session(
        profile_name=None,
        botocore_session=None,
    ),
    # Default standard retrier config
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html
    session_config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    audited_account=None,
    audited_user_id=None,
    audited_partition=None,
    audited_identity_arn=None,
    profile=None,
    profile_region=None,
    credentials=None,
    assumed_role_info=AWS_Assume_Role(
        role_arn=None,
        session_duration=None,
        external_id=None,
    ),
    audit_resources=None,
    audited_regions=None,
    organizations_metadata=None,
    audit_metadata=None,
)
