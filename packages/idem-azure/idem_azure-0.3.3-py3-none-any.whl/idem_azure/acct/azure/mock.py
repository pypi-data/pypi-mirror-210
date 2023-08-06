from typing import Any
from typing import Dict


async def gather(hub, profiles) -> Dict[str, Any]:
    """
    To use mock azure endpoint, provide the endpoint_url in the credentials file.

    Example:
    .. code-block:: yaml

        azure.mock:
          profile_name:
            client_id: Azure client id "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            secret: Azure client secret "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            subscription_id: Azure subscription id "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
            tenant: Azure tenant id "cccccccc-cccc-cccc-cccc-cccccccccccc"
            endpoint_url: "azure mock endpoint aaaa.com"
    """
    sub_profiles = {}
    for profile, ctx in profiles.get("azure.mock", {}).items():
        sub_profiles[profile] = ctx
    return sub_profiles
