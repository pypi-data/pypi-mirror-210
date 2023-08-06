import deprecation
from .python_util import execute


@deprecation.deprecated(
    deprecated_in="3.2", details="use infrastructure.CredentialsApi instead"
)
def gopass_field_from_path(path, field):
    credential = None
    if path and field:
        print("get field for: " + path + ", " + field)
        credential = execute(["gopass", "show", path, field])
    return credential


@deprecation.deprecated(
    deprecated_in="3.2", details="use infrastructure.CredentialsApi instead"
)
def gopass_password_from_path(path):
    credential = None
    if path:
        print("get password for: " + path)
        credential = execute(["gopass", "show", "--password", path])
    return credential
