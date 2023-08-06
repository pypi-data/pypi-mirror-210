from typing import Any
from typing import Dict

from dict_tools.data import NamespaceDict


async def gather(hub, profile: Dict[str, Any]):
    identity_ctx = NamespaceDict(acct=profile)
    return {
        "attribute_value": identity_ctx["acct"]["subscription_id"],
        "attribute_key": "subscription_id",
        "provider": "AZURE",
    }
    return {}
