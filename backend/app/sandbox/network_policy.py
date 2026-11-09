import ipaddress
import urllib.parse
from enum import Enum
from typing import List, Tuple, Optional


class NetworkPolicyMode(str, Enum):
    DENY_ALL = "DENY_ALL"
    ALLOWLIST = "ALLOWLIST"
    APPROVED_DOMAINS = "APPROVED_DOMAINS"


class NetworkPolicy:
    """Network policy manager for sandboxed code execution."""

    BLOCKED_IP_NETWORKS = [
        ipaddress.ip_network("127.0.0.0/8"),       # Loopback
        ipaddress.ip_network("10.0.0.0/8"),        # RFC1918 Private
        ipaddress.ip_network("172.16.0.0/12"),     # RFC1918 Private
        ipaddress.ip_network("192.168.0.0/16"),    # RFC1918 Private
        ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Metadata
        ipaddress.ip_network("::1/128"),           # IPv6 Loopback
        ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local
        ipaddress.ip_network("fe80::/10"),         # IPv6 Link-local
    ]

    BLOCKED_HOSTNAMES = {
        "localhost", "loopback", "metadata", "metadata.google.internal",
        "169.254.169.254", "kubernetes.default.svc"
    }

    def __init__(
        self,
        mode: NetworkPolicyMode = NetworkPolicyMode.DENY_ALL,
        allowed_domains: Optional[List[str]] = None
    ):
        self.mode = mode
        self.allowed_domains = set(allowed_domains or [])

    def validate_destination(self, target: str) -> Tuple[bool, str]:
        """Validate destination host/URL against security rules. Returns (allowed, reason)."""
        if self.mode == NetworkPolicyMode.DENY_ALL:
            return False, "NETWORK_DENIED: All network access is strictly prohibited by policy."

        # Parse target
        if "://" in target:
            parsed = urllib.parse.urlparse(target)
            host = parsed.hostname or ""
        else:
            host = target.split(":")[0].split("/")[0]

        host_lower = host.lower().strip()

        # Check blocked hostnames
        if host_lower in self.BLOCKED_HOSTNAMES or host_lower.endswith(".local") or host_lower.endswith(".internal"):
            return False, f"NETWORK_DENIED: Access to internal hostname '{host}' is strictly forbidden."

        # Check IP address restrictions
        try:
            ip_obj = ipaddress.ip_address(host_lower)
            for net in self.BLOCKED_IP_NETWORKS:
                if ip_obj in net:
                    return False, f"NETWORK_DENIED: Access to private/local IP range '{ip_obj}' is forbidden."
        except ValueError:
            # Target is a domain name
            pass

        # Check allowed domains
        if self.mode in (NetworkPolicyMode.ALLOWLIST, NetworkPolicyMode.APPROVED_DOMAINS):
            if "*" in self.allowed_domains:
                return True, "Allowed by wildcard policy."
            if any(host_lower == d or host_lower.endswith("." + d) for d in self.allowed_domains):
                return True, f"Domain '{host_lower}' is in allowlist."
            return False, f"NETWORK_DENIED: Domain '{host_lower}' is not in approved domain allowlist."

        return False, "NETWORK_DENIED: Destination failed security check."
