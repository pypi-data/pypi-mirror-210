import base64
import re
from typing import Any
from typing import Dict


BASE_URL = "/api"


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    Generate token with basic auth

    Example:
    .. code-block:: yaml

        vmware_alb:
            default:
                username: "admin"
                password: "password"
                controller: "10.65.11.14"
                api_version: "22.1.2"
                endpoint_url: 'https://10.65.11.14/'
                tenant: "admin"
    """

    sub_profiles = {}
    for (
        profile,
        ctx,
    ) in profiles.get("vmware_alb", {}).items():
        endpoint_url = ctx.get("endpoint_url")

        if not re.search(BASE_URL, endpoint_url):
            endpoint_url = "".join((endpoint_url.rstrip("/"), BASE_URL))

        creds = f"{ctx.get('username')}:{ctx.get('password')}"
        sub_profiles[profile] = dict(
            endpoint_url=endpoint_url,
            headers={
                "X-Avi-Tenant": ctx.get("tenant", None),
                "X-Avi-Version": ctx.get("api_version", None),
                "Authorization": f"Basic {base64.b64encode(creds.encode('utf-8')).decode('ascii')}",
            },
        )
    return sub_profiles
