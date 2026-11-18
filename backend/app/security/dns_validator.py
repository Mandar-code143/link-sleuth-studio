"""DNS resolution and IP range validation for SSRF defense."""

import ipaddress
import socket
from typing import List, Tuple


# Cloud metadata destinations and internal names
BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.internal",
    "169.254.169.254",
    "instance-data",
}

# Explicit prohibited networks
PROHIBITED_NETWORKS = [
    # IPv4 Private & Loopback
    ipaddress.ip_network("0.0.0.0/8"),          # "This" network
    ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space (CGNAT)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link Local / Cloud metadata
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay Anycast
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),      # Network Interconnect Device Benchmark
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for future use
    ipaddress.ip_network("255.255.255.255/32"), # Limited Broadcast
    # IPv6 Prohibited
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped (will check mapped IPv4 separately)
    ipaddress.ip_network("64:ff9b::/96"),       # IPv4/IPv6 translation
    ipaddress.ip_network("100::/64"),           # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),      # Documentation
    ipaddress.ip_network("fc00::/7"),           # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-Local
    ipaddress.ip_network("ff00::/8"),           # Multicast
]


class SSRFSecurityError(ValueError):
    """Raised when an IP or DNS destination violates SSRF security boundaries."""
    pass


def is_ip_prohibited(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Checks if an IP address belongs to any prohibited, private, or loopback range."""
    # Check native attributes
    if (
        ip.is_loopback
        or ip.is_private
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_reserved
    ):
        return True

    # Check for IPv4-mapped IPv6 address
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        mapped_ip = ip.ipv4_mapped
        return is_ip_prohibited(mapped_ip)

    # Check explicit network definitions
    for network in PROHIBITED_NETWORKS:
        # Avoid checking IPv4 network against IPv6 address without mapping
        if network.version == ip.version and ip in network:
            return True

    return False


def resolve_and_validate_hostname(hostname: str) -> List[Tuple[str, int]]:
    """
    Resolves hostname to IP addresses and rigorously validates each against SSRF rules.
    
    Fails closed: if ANY resolved IP record is private or prohibited, the entire request
    is rejected to prevent mixed DNS exploitation.
    
    Returns:
        List of (ip_address_str, address_family)
        
    Raises:
        SSRFSecurityError if any IP is prohibited or resolution fails.
    """
    clean_host = hostname.lower().strip(".")
    if clean_host in BLOCKED_HOSTNAMES:
        raise SSRFSecurityError(f"Prohibited cloud metadata hostname '{hostname}'.")

    # If it's already an IP literal
    try:
        ip = ipaddress.ip_address(clean_host.strip("[]"))
        if is_ip_prohibited(ip):
            raise SSRFSecurityError(f"Target IP address '{ip}' is in a prohibited private or local network range.")
        family = socket.AF_INET6 if ip.version == 6 else socket.AF_INET
        return [(str(ip), family)]
    except ValueError:
        pass

    # Resolve via socket.getaddrinfo (supports IPv4 and IPv6)
    try:
        addrinfo = socket.getaddrinfo(
            clean_host,
            None,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as e:
        raise SSRFSecurityError(f"DNS resolution failed for hostname '{hostname}': {e}")

    if not addrinfo:
        raise SSRFSecurityError(f"No DNS records found for hostname '{hostname}'.")

    validated_ips: List[Tuple[str, int]] = []
    seen = set()

    for item in addrinfo:
        family, socktype, proto, canonname, sockaddr = item
        ip_str = sockaddr[0]

        if ip_str in seen:
            continue
        seen.add(ip_str)

        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            raise SSRFSecurityError(f"Invalid resolved IP '{ip_str}' for hostname '{hostname}'.")

        # STRICT SSRF BOUNDARY: Fail closed on mixed records
        if is_ip_prohibited(ip_obj):
            raise SSRFSecurityError(
                f"Hostname '{hostname}' resolved to prohibited private IP address '{ip_str}'. Fetching is blocked."
            )

        validated_ips.append((ip_str, family))

    if not validated_ips:
        raise SSRFSecurityError(f"No valid public IP addresses found for hostname '{hostname}'.")

    return validated_ips
