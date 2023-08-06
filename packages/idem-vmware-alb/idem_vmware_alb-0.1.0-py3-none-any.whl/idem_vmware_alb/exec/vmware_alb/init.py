def __init__(hub):
    hub.exec.vmware_alb.ENDPOINT_URLS = ["/api"]
    # The default is the first in the list
    hub.exec.vmware_alb.DEFAULT_ENDPOINT_URL = "/api"

    # This enables acct profiles that begin with "vmware_alb" for vmware_alb modules
    hub.exec.vmware_alb.ACCT = ["vmware_alb"]

    def _get_version_sub(ctx, *args, **kwargs):
        ctx.acct.get("api_version", "latest")
        return hub.exec.vmware_alb

    # Get the version sub dynamically from the ctx variable/acct
    # hub.pop.sub.dynamic(hub.exec.vmware_alb, _get_version_sub)
