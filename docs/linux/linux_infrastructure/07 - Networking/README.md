# 07 - Comprehensive Linux Networking Architecture & System Administration

> **Phase:** 1 (Core Linux) · **Time:** ~4 weeks · **Difficulty:** ⭐⭐⭐  
> **Target Audience:** Systems Administrators, DevOps Engineers, Site Reliability Engineers (SREs), and Network Engineers.

---

## Table of Contents
1. [Architecture & Network Foundations](#1-architecture--network-foundations)
   - [OSI 7-Layer vs. TCP/IP 4-Layer Model](#osi-7-layer-vs-tcpip-4-layer-model)
   - [Frame, Packet & Segment Header Structures](#frame-packet--segment-header-structures)
   - [Linux Kernel Network Stack & Netfilter Architecture](#linux-kernel-network-stack--netfilter-architecture)
2. [IP Addressing, Subnetting & IPv6 Masterclass](#2-ip-addressing-subnetting--ipv6-masterclass)
   - [IPv4 Subnetting, Math & CIDR Reference](#ipv4-subnetting-math--cidr-reference)
   - [IPv6 Architecture & SLAAC vs. DHCPv6](#ipv6-architecture--slaac-vs-dhcpv6)
3. [Modern Interface Management with `iproute2`](#3-modern-interface-management-with-iproute2)
   - [Legacy vs. Modern Tooling Migration Guide](#legacy-vs-modern-tooling-migration-guide)
   - [`ip` Command Suite Complete Reference](#ip-command-suite-complete-reference)
4. [Cross-Distribution Persistent Network Configuration](#4-cross-distribution-persistent-network-configuration)
   - [Ubuntu/Debian: Netplan (`/etc/netplan/`)](#ubuntudebian-netplan-etcnetplan)
   - [RHEL/CentOS/Rocky/Fedora: NetworkManager (`nmcli`)](#rhelcentosrockyfedora-networkmanager-nmcli)
   - [Arch/Minimal Server: `systemd-networkd`](#archminimal-server-systemd-networkd)
5. [Advanced Routing, Namespaces, Bonding & VLANs](#5-advanced-routing-namespaces-bonding--vlans)
   - [IP Forwarding & Static Routing](#ip-forwarding--static-routing)
   - [Policy-Based Routing (PBR)](#policy-based-routing-pbr)
   - [Linux Network Namespaces (`ip netns`)](#linux-network-namespaces-ip-netns)
   - [Network Interface Bonding (LACP/Active-Backup)](#network-interface-bonding-lacpactive-backup)
   - [802.1Q VLAN Tagging & Linux Bridging](#8021q-vlan-tagging--linux-bridging)
6. [Core Infrastructure Services Configuration](#6-core-infrastructure-services-configuration)
   - [DNS Architecture: `/etc/resolv.conf`, `systemd-resolved`, & BIND9/Dnsmasq](#dns-architecture-etcresolvconf-systemd-resolved--bind9dnsmasq)
   - [DHCP Client & Server Management](#dhcp-client--server-management)
   - [Production SSH Hardening & Tunneling](#production-ssh-hardening--tunneling)
   - [NTP / Time Synchronization (`chrony`)](#ntp--time-synchronization-chrony)
7. [Linux Firewalls & Packet Filtering](#7-linux-firewalls--packet-filtering)
   - [`iptables` Deep Dive: Tables, Chains & Stateful NAT](#iptables-deep-dive-tables-chains--stateful-nat)
   - [`nftables`: Modern Netfilter Framework](#nftables-modern-netfilter-framework)
   - [UFW & Firewalld Abstractions](#ufw--firewalld-abstractions)
8. [Container & Cloud Virtualization Networking](#8-container--cloud-virtualization-networking)
   - [Docker Network Drivers & iptables NAT Plumbing](#docker-network-drivers--iptables-nat-plumbing)
   - [Kubernetes CNI Fundamentals](#kubernetes-cni-fundamentals)
   - [Cloud VPC Networking Concepts](#cloud-vpc-networking-concepts)
9. [System Administration Diagnostics & Kernel Tuning](#9-system-administration-diagnostics--kernel-tuning)
   - [Layer-by-Layer Troubleshooting Workflow](#layer-by-layer-troubleshooting-workflow)
   - [Packet Capture Masterclass (`tcpdump` & `tshark`)](#packet-capture-masterclass-tcpdump--tshark)
   - [Production Network Troubleshooting Table](#production-network-troubleshooting-table)
   - [Kernel Network Stack Tuning (`sysctl.conf`)](#kernel-network-stack-tuning-sysctlconf)
10. [Production Hands-On Labs](#10-production-hands-on-labs)
    - [Lab 1: Multi-Interface Network Config with Netplan & NetworkManager](#lab-1-multi-interface-network-config-with-netplan--networkmanager)
    - [Lab 2: Virtual Router & Isolated Namespaces with NAT](#lab-2-virtual-router--isolated-namespaces-with-nat)
    - [Lab 3: Production Firewall Hardening & Fail2ban Integration](#lab-3-production-firewall-hardening--fail2ban-integration)
    - [Lab 4: Deep Packet Capture & Traffic Analysis](#lab-4-deep-packet-capture--traffic-analysis)
    - [Lab 5: Enterprise LACP Bonding & VLAN Trunking](#lab-5-enterprise-lacp-bonding--vlan-trunking)
    - [Lab 6: Lightweight DNS & DHCP Infrastructure with Dnsmasq](#lab-6-lightweight-dns--dhcp-infrastructure-with-dnsmasq)
11. [Curated Learning Resources](#11-curated-learning-resources)
12. [Self-Check & Skill Verification](#12-self-check--skill-verification)

---

## 1. Architecture & Network Foundations

### OSI 7-Layer vs. TCP/IP 4-Layer Model

Networking in Linux relies on standardized layered models. Data travels down the stack at the sending host (encapsulation) and up the stack at the receiving host (decapsulation).

```
          OSI 7-LAYER MODEL                       TCP/IP 4-LAYER STACK
+-----------------------------------+     +-----------------------------------+
| 7. Application (HTTP, SSH, DNS)   | \   |                                   |
| 6. Presentation (TLS, ASCII, JSON)|  +--| Application Layer                 |
| 5. Session (RPC, Sockets)         | /   | (Data / Payload)                  |
+-----------------------------------+     +-----------------------------------+
| 4. Transport (TCP, UDP, SCTP)     | --->| Transport Layer (Segments/Datagrams)
+-----------------------------------+     +-----------------------------------+
| 3. Network (IPv4, IPv6, ICMP)     | --->| Internet / Network Layer (Packets)|
+-----------------------------------+     +-----------------------------------+
| 2. Data Link (Ethernet, VLAN)     | \   | Network Access / Link Layer       |
| 1. Physical (Copper, Fiber, PHY)  |  +--| (Frames / Bits)                   |
+-----------------------------------+     +-----------------------------------+
```

| Layer (TCP/IP) | Data Unit (PDU) | Key Protocols & Technologies | Linux Subsystem / Drivers |
|---|---|---|---|
| **Application** | Data / Message | HTTP/HTTPS, SSH, DNS, NTP, gRPC | User space applications, Sockets API (`sys_socket`) |
| **Transport** | Segment (TCP) / Datagram (UDP) | TCP, UDP, SCTP, QUIC | Kernel TCP/UDP stack (`net/ipv4/tcp.c`), Socket Buffers (`sk_buff`) |
| **Internet** | Packet | IPv4, IPv6, ICMP, ARP (L2/L3 bridge), IPsec | Routing Engine, Netfilter hooks, IPsec (XFRM) |
| **Link / Access** | Frame | Ethernet (802.3), Wi-Fi (802.11), VLAN (802.1Q), LACP | Network Interface Card (NIC) Drivers (`e1000e`, `ixgbe`), eBPF/XDP |

---

### Frame, Packet & Segment Header Structures

Understanding packet encapsulation is critical when analyzing captures with `tcpdump` or Wireshark.

```
+-----------------------------------------------------------------------------------+
| Ethernet II Header | IPv4 Packet Header  | TCP Segment Header  | Application Data |
| (14 Bytes)         | (20-60 Bytes)       | (20-60 Bytes)       | (Payload)        |
+--------------------+---------------------+---------------------+------------------+
| Dest MAC | Src MAC | Src IP  | Dest IP   | Src Port | Dest Port| HTTP / SSH Data  |
| (6 B)    | (6 B)   | (4 B)   | (4 B)     | (2 B)    | (2 B)    |                  |
+--------------------+---------------------+---------------------+------------------+
```

#### Key Fields:
- **Ethernet Header (14 B):** Preamble, Destination MAC, Source MAC, EtherType (`0x0800` = IPv4, `0x86DD` = IPv6, `0x0806` = ARP).
- **IPv4 Header (20 B min):** Version, IHL, TOS/DiffServ, Total Length, TTL (Time to Live), Protocol (`6` = TCP, `17` = UDP, `1` = ICMP), Source IP, Destination IP.
- **TCP Header (20 B min):** Source Port, Destination Port, Sequence Number, Ack Number, Flags (SYN, ACK, FIN, RST, PSH, URG), Window Size, Checksum.

---

### Linux Kernel Network Stack & Netfilter Architecture

The Linux kernel processes incoming packet buffers (`sk_buff`) through a series of internal hooks before reaching sockets or being forwarded.

```
                        INCOMING PACKET (nic rx)
                                  |
                                  v
                       [ PREROUTING Hook ]  <-- (raw, mangle, nat tables)
                                  |
                                  v
                           /-------------\
                          / Routing Decision \
                          \------------------/
                            /              \
           (Destination = Local)       (Destination != Local)
                         /                    \
                        v                      v
           [ INPUT Hook ]             [ FORWARD Hook ] <-- (mangle, filter)
                  |                            |
                  v                            v
           Local Socket               [ POSTROUTING Hook ] <-- (mangle, nat)
                  |                            |
                  v                            v
             Application                 OUTGOING PACKET (nic tx)
                  ^                            ^
                  |                            |
           Local Application                   |
                  |                            |
                  v                            |
           [ OUTPUT Hook ] --------------------+ <-- (raw, mangle, nat, filter)
```

- **Socket Layer:** Provides the standard BSD sockets interface (`socket()`, `bind()`, `listen()`, `accept()`, `connect()`).
- **Netfilter:** Kernel framework providing hooks (`PREROUTING`, `INPUT`, `FORWARD`, `OUTPUT`, `POSTROUTING`) for `iptables` and `nftables`.
- **XDP (eBPF):** eXtended Data Path allows processing packets directly inside the NIC driver prior to `sk_buff` allocation for line-rate packet filtering and DDoS mitigation.

---

## 2. IP Addressing, Subnetting & IPv6 Masterclass

### IPv4 Subnetting, Math & CIDR Reference

IPv4 addresses are 32-bit integers divided into a Network portion and a Host portion using a subnet mask.

#### Subnet Calculation Math
For a subnet `192.168.10.0/26`:
- **Subnet Mask:** `/26` = 26 ones followed by 6 zeros = `255.255.255.192`
- **Total Addresses:** $2^{(32 - 26)} = 2^6 = 64$
- **Usable Host Addresses:** $64 - 2 = 62$ (subtract Network Address and Broadcast Address)
- **Network ID:** `192.168.10.0`
- **First Usable Host:** `192.168.10.1`
- **Last Usable Host:** `192.168.10.62`
- **Broadcast Address:** `192.168.10.63`

#### Quick CIDR Reference Table
| CIDR | Subnet Mask | Total IPs | Usable IPs | Typical Use Case |
|---|---|---|---|---|
| `/32` | `255.255.255.255` | 1 | 1 (Host) | Loopback / Single Host route |
| `/30` | `255.255.255.252` | 4 | 2 | Point-to-Point WAN link |
| `/29` | `255.255.255.248` | 8 | 6 | Small public IP block |
| `/28` | `255.255.255.240` | 16 | 14 | Small DMZ subnet |
| `/27` | `255.255.255.224` | 32 | 30 | Container pod node range |
| `/24` | `255.255.255.0` | 256 | 254 | Standard LAN / Subnet |
| `/23` | `255.255.250.0` | 512 | 510 | Medium office LAN |
| `/16` | `255.255.0.0` | 65,536 | 65,534 | Cloud VPC network |
| `/8` | `255.0.0.0` | 16,777,216 | 16,777,214 | Large Enterprise internal block |

#### Reserved Private & Special IPv4 Blocks (RFCs)
- **RFC 1918 Private Ranges:**
  - `10.0.0.0/8` (`10.0.0.0` – `10.255.255.255`)
  - `172.16.0.0/12` (`172.16.0.0` – `172.31.255.255`)
  - `192.168.0.0/16` (`192.168.0.0` – `192.168.255.255`)
- **RFC 6598 Carrier-Grade NAT (CGNAT):** `100.64.0.0/10`
- **RFC 3927 Link-Local (APIPA):** `169.254.0.0/16`
- **RFC 1122 Loopback:** `127.0.0.0/8`
- **RFC 5771 Multicast:** `224.0.0.0/4`

---

### IPv6 Architecture & SLAAC vs. DHCPv6

IPv6 uses 128-bit addresses represented as eight 16-bit hexadecimal blocks separated by colons.

#### Addressing Rules & Shortening
- Rule 1: Leading zeros in a block can be omitted (`00ab` -> `ab`).
- Rule 2: Consecutive blocks of zeros can be replaced by `::` once per address.
- Example: `2001:0db8:0000:0000:0000:ff00:0042:8329` -> `2001:db8::ff00:42:8329`

#### Address Types & Scopes
- **Loopback:** `::1/128`
- **Link-Local:** `fe80::/10` (automatically generated per interface, non-routable beyond local segment).
- **Global Unicast Address (GUA):** `2001::/3` or `2000::/3` (publicly routable internet IPs).
- **Unique Local Address (ULA):** `fc00::/7` / `fd00::/7` (private local addresses, equivalent to RFC 1918).
- **Multicast:** `ff00::/8` (`ff02::1` = All Nodes, `ff02::2` = All Routers).

#### Autoconfiguration (SLAAC vs Stateful DHCPv6)
1. **SLAAC (Stateless Address Autoconfiguration):** Host listens for ICMPv6 Router Advertisement (RA) messages sent by local router, grabs the network prefix (`/64`), and computes host ID using EUI-64 or random privacy extensions (RFC 4941).
2. **Stateful DHCPv6:** Central server manages and leases IPv6 addresses and options (DNS, NTP) similarly to IPv4 DHCP.

---

## 3. Modern Interface Management with `iproute2`

### Legacy vs. Modern Tooling Migration Guide

> [!WARNING]
> Legacy tools (`ifconfig`, `netstat`, `arp`, `route`) are deprecated in modern Linux distributions. They rely on old kernel ioctl calls and lack support for modern networking features like namespaces, policy routing, and detailed socket statistics. Use the `iproute2` suite (`ip`, `ss`).

| Legacy Command | Modern `iproute2` / `ss` Equivalent | Task Description |
|---|---|---|
| `ifconfig` | `ip addr show` / `ip link show` | View network interface configurations |
| `ifconfig eth0 up` | `ip link set dev eth0 up` | Bring interface up |
| `ifconfig eth0 192.168.1.50/24` | `ip addr add 192.168.1.50/24 dev eth0` | Assign IP address to interface |
| `route -n` | `ip route show` | Display kernel routing table |
| `route add default gw 192.168.1.1` | `ip route add default via 192.168.1.1` | Set default gateway |
| `arp -an` | `ip neighbor show` / `ip neigh` | Display ARP cache table |
| `netstat -tulnp` | `ss -tulnp` | List listening TCP/UDP sockets with PIDs |
| `netstat -r` | `ip route` | View active routes |
| `iptunnel` | `ip tunnel` | Manage IP tunnels (GRE, SIT) |

---

### `ip` Command Suite Complete Reference

```bash
# ==============================================================================
# 1. LINK MANAGEMENT (ip link)
# ==============================================================================

# List all physical and virtual network interfaces with operational status
ip link show

# Display detailed statistics (bytes, packets, errors, dropped) for interface eth0
ip -s link show dev eth0

# Enable (bring up) or disable (bring down) a network interface
sudo ip link set dev eth0 up
sudo ip link set dev eth0 down

# Change MTU (Maximum Transmission Unit) to 9000 bytes for Jumbo Frames support
sudo ip link set dev eth0 mtu 9000

# Change MAC address (hardware address) of an interface
sudo ip link set dev eth0 down
sudo ip link set dev eth0 address 52:54:00:12:34:56
sudo ip link set dev eth0 up

# Create a virtual Ethernet pair (veth) for container/namespace interconnects
sudo ip link add veth-host type veth peer name veth-guest

# Delete a virtual interface link
sudo ip link delete dev veth-host

# ==============================================================================
# 2. ADDRESS MANAGEMENT (ip addr)
# ==============================================================================

# View all assigned IPv4 and IPv6 addresses
ip addr show

# View IPv4 addresses only for a specific interface
ip -4 addr show dev eth0

# Add a secondary IP address to an interface
sudo ip addr add 10.0.0.50/24 dev eth0

# Assign an IP address with a specific broadcast address and label
sudo ip addr add 192.168.1.100/24 broadcast 192.168.1.255 dev eth0 label eth0:1

# Remove an IP address from an interface
sudo ip addr del 10.0.0.50/24 dev eth0

# Flush all IP addresses assigned to a specific interface
sudo ip addr flush dev eth0

# ==============================================================================
# 3. ROUTING TABLE MANAGEMENT (ip route)
# ==============================================================================

# Display the main kernel routing table
ip route show

# View routing decisions for a specific destination IP address
ip route get 8.8.8.8

# Add a static network route via gateway
sudo ip route add 172.16.0.0/11 via 192.168.1.1 dev eth0

# Add a default gateway route
sudo ip route add default via 192.168.1.1 dev eth0

# Replace or modify an existing route
sudo ip route change default via 192.168.1.254 dev eth0

# Delete a static route
sudo ip route del 172.16.0.0/16

# ==============================================================================
# 4. NEIGHBOR / ARP MANAGEMENT (ip neighbor)
# ==============================================================================

# Display ARP cache entries (IPv4 MAC address mappings)
ip neighbor show

# Flush all ARP cache entries for interface eth0
sudo ip neighbor flush dev eth0

# Add a static ARP entry (prevents ARP spoofing)
sudo ip neighbor add 192.168.1.50 lladdr 00:11:22:33:44:55 dev eth0

# Delete an ARP table entry
sudo ip neighbor del 192.168.1.50 dev eth0
```

---

## 4. Cross-Distribution Persistent Network Configuration

### Ubuntu/Debian: Netplan (`/etc/netplan/`)

Netplan uses YAML declaration files to configure underlying network renderers (`systemd-networkd` or `NetworkManager`).

#### Static IP Configuration (`/etc/netplan/01-netcfg.yaml`)
```yaml
# /etc/netplan/01-netcfg.yaml
# Netplan configuration for Ubuntu/Debian systems using systemd-networkd renderer
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      dhcp6: no
      addresses:
        - 192.168.1.50/24
        - "2001:db8:1::50/64"
      routes:
        - to: default
          via: 192.168.1.1
          metric: 100
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
          - "2606:4700:4700::1111"
        search:
          - internal.domain.com
```

#### Management Commands:
```bash
# Validate YAML syntax and safely test netplan configuration (reverts after 120s if unconfirmed)
sudo netplan try

# Apply the netplan configuration immediately
sudo netplan apply

# Debug netplan configuration generation
sudo netplan --debug apply
```

---

### RHEL/CentOS/Rocky/Fedora: NetworkManager (`nmcli`)

`NetworkManager` is the standard network daemon for RHEL family distributions.

#### `nmcli` Production Commands:
```bash
# Show summary status of network devices
nmcli device status

# List all configured network connections
nmcli connection show

# Create a static IPv4 connection named "eth0-static"
sudo nmcli connection add type ethernet con-name eth0-static ifname eth0 \
  ip4 192.168.1.60/24 gw4 192.168.1.1

# Modify connection DNS servers and search domains
sudo nmcli connection modify eth0-static ipv4.dns "8.8.8.8 1.1.1.1"
sudo nmcli connection modify eth0-static ipv4.dns-search "corp.local"

# Set IP allocation method to manual (static)
sudo nmcli connection modify eth0-static ipv4.method manual

# Activate the static connection profile
sudo nmcli connection up eth0-static

# Reload all configuration files from disk
sudo nmcli connection reload
```

---

### Arch/Minimal Server: `systemd-networkd`

`systemd-networkd` is a lightweight native network configuration daemon built into systemd.

#### Persistent Configuration File (`/etc/systemd/network/20-wired.network`)
```ini
# /etc/systemd/network/20-wired.network
[Match]
Name=eth0

[Network]
Address=192.168.1.70/24
Gateway=192.168.1.1
DNS=1.1.1.1
DNS=8.8.8.8
Domains=infra.local
NTP=pool.ntp.org

[Route]
Destination=10.10.0.0/16
Gateway=192.168.1.254
Metric=50
```

#### Service Management:
```bash
# Enable and start systemd-networkd and systemd-resolved services
sudo systemctl enable --now systemd-networkd
sudo systemctl enable --now systemd-resolved

# Check network state overview
networkctl status
```

---

## 5. Advanced Routing, Namespaces, Bonding & VLANs

### IP Forwarding & Static Routing

To act as a router or gateway, Linux must enable kernel IP forwarding.

```bash
# Check current IP forwarding state (0 = disabled, 1 = enabled)
sysctl net.ipv4.ip_forward

# Enable IP forwarding persistently in sysctl
echo "net.ipv4.ip_forward = 1" | sudo tee /etc/sysctl.d/99-ip-forward.conf
sudo sysctl --system

# Verify static route insertion with explicit metric
sudo ip route add 10.200.0.0/16 via 192.168.1.254 dev eth0 metric 10
```

---

### Policy-Based Routing (PBR)

Policy-based routing allows routing traffic based on source address, port, or packet marks instead of just destination address.

```bash
# Step 1: Register a new custom routing table name in /etc/iproute2/rt_tables
echo "200 custom_table" | sudo tee -a /etc/iproute2/rt_tables

# Step 2: Add routes to the custom routing table
sudo ip route add 10.0.0.0/24 dev eth1 table custom_table
sudo ip route add default via 10.0.0.1 dev eth1 table custom_table

# Step 3: Define a routing policy rule matching traffic originating from 192.168.1.100
sudo ip rule add from 192.168.1.100/32 table custom_table pref 1000

# Step 4: Display all registered routing policy rules
ip rule show

# Step 5: Flush routing cache to force instant evaluation
sudo ip route flush cache
```

---

### Linux Network Namespaces (`ip netns`)

Network namespaces provide isolated instances of the Linux network stack (interfaces, routing tables, firewall rules, sockets).

```
+-----------------------------------------------------------------------+
| DEFAULT HOST NAMESPACE                                                |
|                                                                       |
|  Physical Interface (eth0)         veth-host (192.168.50.1/24)        |
|  [ 192.168.1.50/24 ]               |                                  |
+------------------------------------+----------------------------------+
                                     |
                             Virtual Cable (veth pair)
                                     |
+------------------------------------+----------------------------------+
| ISOLATED NAMESPACE (ns-app)        |                                  |
|                                    v                                  |
|                            veth-guest (192.168.50.2/24)              |
|                            Loopback (lo: 127.0.0.1)                  |
+-----------------------------------------------------------------------+
```

```bash
# Create a new network namespace named "ns-app"
sudo ip netns add ns-app

# List all network namespaces on the host
ip netns list

# Create a virtual Ethernet (veth) cable pair
sudo ip link add veth-host type veth peer name veth-guest

# Move one end of the veth pair into the "ns-app" namespace
sudo ip link set veth-guest netns ns-app

# Configure IP address on host end
sudo ip addr add 192.168.50.1/24 dev veth-host
sudo ip link set dev veth-host up

# Configure IP address and loopback inside "ns-app" namespace
sudo ip netns exec ns-app ip link set dev lo up
sudo ip netns exec ns-app ip addr add 192.168.50.2/24 dev veth-guest
sudo ip netns exec ns-app ip link set dev veth-guest up

# Add default route inside the namespace pointing to host veth end
sudo ip netns exec ns-app ip route add default via 192.168.50.1

# Verify connectivity from namespace to host
sudo ip netns exec ns-app ping -c 3 192.168.50.1

# Clean up namespace and links
sudo ip netns del ns-app
```

---

### Network Interface Bonding (LACP/Active-Backup)

Bonding aggregates multiple physical interfaces into a single logical interface for redundancy or throughput expansion.

#### Bonding Modes:
- **Mode 0 (balance-rr):** Round-robin packet transmission (requires switch support).
- **Mode 1 (active-backup):** Only one slave active; second takes over on link failure.
- **Mode 4 (802.3ad LACP):** Dynamic Link Aggregation (requires LACP switch configuration).

```bash
# Create bonding master interface using iproute2
sudo ip link add name bond0 type bond mode 802.3ad miimon 100 lacp_rate fast

# Bind physical interfaces (eth1, eth2) as slaves to bond0
sudo ip link set dev eth1 down
sudo ip link set dev eth2 down
sudo ip link set dev eth1 master bond0
sudo ip link set dev eth2 master bond0

# Assign IP to master bond interface and bring up links
sudo ip addr add 10.10.10.50/24 dev bond0
sudo ip link set dev bond0 up
sudo ip link set dev eth1 up
sudo ip link set dev eth2 up

# View bonding status from procfs
cat /proc/net/bonding/bond0
```

---

### 802.1Q VLAN Tagging & Linux Bridging

#### 802.1Q VLAN Tagging
```bash
# Create VLAN sub-interface (VLAN ID 100) on physical NIC eth0
sudo ip link add link eth0 name eth0.100 type vlan id 100

# Assign IP and activate VLAN sub-interface
sudo ip addr add 172.16.100.10/24 dev eth0.100
sudo ip link set dev eth0.100 up
```

#### Linux Software Bridging
```bash
# Create software bridge "br0"
sudo ip link add name br0 type bridge

# Attach interfaces to bridge
sudo ip link set dev eth1 master br0
sudo ip link set dev eth2 master br0

# Assign IP to bridge interface and activate all interfaces
sudo ip addr add 192.168.100.1/24 dev br0
sudo ip link set dev br0 up
sudo ip link set dev eth1 up
sudo ip link set dev eth2 up

# Inspect bridge status and connected ports
bridge link show br0
```

---

## 6. Core Infrastructure Services Configuration

### DNS Architecture: `/etc/resolv.conf`, `systemd-resolved`, & BIND9/Dnsmasq

Linux resolves hostnames to IP addresses using `/etc/nsswitch.conf` and `/etc/resolv.conf`.

#### `/etc/nsswitch.conf` (Name Service Switch)
```ini
# Specifies lookup order for hostname resolution
hosts:          files dns mdns4_minimal [NOTFOUND=return]
```

#### Modern `systemd-resolved` Management
```bash
# Inspect active DNS servers and resolution state
resolvectl status

# Query DNS hostname directly using systemd-resolved stub
resolvectl query backend-server.internal

# Flush systemd-resolved DNS cache
sudo resolvectl flush-caches
```

---

### DHCP Client & Server Management

#### DHCP Client (`dhclient`)
```bash
# Release current DHCP IPv4 lease on eth0
sudo dhclient -r eth0

# Request new DHCP lease on eth0 with verbose logging
sudo dhclient -v eth0
```

#### Dnsmasq DNS & DHCP Server (`/etc/dnsmasq.conf`)
```ini
# /etc/dnsmasq.conf - Combined DNS forwarder and DHCP server
interface=eth1
dhcp-range=192.168.50.100,192.168.50.200,255.255.255.0,12h
dhcp-option=option:router,192.168.50.1
dhcp-option=option:dns-server,192.168.50.1,8.8.8.8
domain=lan.local
dhcp-host=aa:bb:cc:dd:ee:ff,static-server,192.168.50.10,infinite
```

---

### Production SSH Hardening & Tunneling

#### Hardened `/etc/ssh/sshd_config` Configuration
```ini
# /etc/ssh/sshd_config - Production Hardening Directives
Port 2222
Protocol 2
PermitRootLogin no
MaxAuthTries 3
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding yes
ClientAliveInterval 300
ClientAliveCountMax 2
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com
```

#### SSH Port Forwarding & Tunneling Workflows
```bash
# 1. Local Port Forwarding: Forward local port 8080 to remote DB server (10.0.0.5:5432) via SSH bastion
ssh -L 8080:10.0.0.5:5432 user@ssh-bastion.example.com -N -f

# 2. Remote Port Forwarding: Expose local service running on port 3000 to public server port 9000
ssh -R 9000:localhost:3000 user@public-server.example.com -N -f

# 3. Dynamic SOCKS5 Proxy: Route arbitrary browser/app traffic through SSH tunnel
ssh -D 1080 user@ssh-gateway.example.com -N -f
```

---

### NTP / Time Synchronization (`chrony`)

Accurate network time synchronization is crucial for security protocols (TLS, Kerberos), database clustering, and log correlation.

#### `/etc/chrony/chrony.conf`
```ini
# Server pool configuration
pool pool.ntp.org iburst maxsources 4

# Store time drift rate
driftfile /var/lib/chrony/drift

# Allow step correction during initial startup if drift > 1s
makestep 1.0 3

# Log directory
logdir /var/log/chrony
```

```bash
# Check chrony synchronization tracking status
chronyc tracking

# List active NTP time sources and synchronization stats
chronyc sources -v
```

---

## 7. Linux Firewalls & Packet Filtering

### `iptables` Deep Dive: Tables, Chains & Stateful NAT

`iptables` inspects and filters IPv4 traffic using predefined tables and chains.

#### Packet Traversal Rules:
- **filter Table:** `INPUT`, `FORWARD`, `OUTPUT` (Default firewall operations).
- **nat Table:** `PREROUTING` (DNAT), `POSTROUTING` (SNAT/Masquerade), `OUTPUT`.
- **mangle Table:** Packet modification (TTL, TOS, QoS markers).

```bash
# ==============================================================================
# STATEFUL FIREWALL HARDENING BASELINE
# ==============================================================================

# 1. Set default policies to DROP for inbound and forwarded traffic
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# 2. Allow unrestricted loopback traffic
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

# 3. Accept established and related connections (Stateful tracking)
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 4. Allow incoming SSH (port 22) and HTTPS (port 443)
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -m conntrack --ctstate NEW -j ACCEPT

# 5. Rate-limit ICMP Ping requests (max 1 per sec, burst 5) to prevent flood
sudo iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s --limit-burst 5 -j ACCEPT

# ==============================================================================
# NAT & PORT FORWARDING (ROUTER ROLE)
# ==============================================================================

# Enable MASQUERADE for outbound internet traffic leaving eth0 (dynamic public IP)
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Forward incoming traffic on port 80 to internal server 192.168.1.10:80 (DNAT)
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to-destination 192.168.1.10:80
sudo iptables -A FORWARD -p tcp -d 192.168.1.10 --dport 80 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT

# Save iptables rules persistently (Debian/Ubuntu)
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

### `nftables`: Modern Netfilter Framework

`nftables` replaces `iptables`, `ip6tables`, `arptables`, and `ebptables` with a unified syntax and higher kernel performance.

#### Production `/etc/nftables.conf` Script
```nftables
#!/usr/sbin/nft -f

# Flush existing ruleset
flush ruleset

table inet filter {
    chain input {
        type filter hook input priority filter; policy drop;

        # Accept loopback
        iifname "lo" accept

        # Accept established and related traffic
        ct state established,related accept

        # Drop invalid connections
        ct state invalid drop

        # Accept SSH (22) and HTTPS (443)
        tcp dport { 22, 443 } ct state new accept

        # Accept ICMP / ICMPv6
        meta l4proto { icmp, ipv6-icmp } accept
    }

    chain forward {
        type filter hook forward priority filter; policy drop;
    }

    chain output {
        type filter hook output priority filter; policy accept;
    }
}
```

```bash
# Load ruleset from file
sudo nft -f /etc/nftables.conf

# Display current atomic ruleset
sudo nft list ruleset
```

---

### UFW & Firewalld Abstractions

#### UFW (Uncomplicated Firewall - Ubuntu)
```bash
# Set defaults
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow services by port and protocol
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Limit SSH connections to mitigate brute force attacks
sudo ufw limit 22/tcp

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

#### Firewalld (RHEL / CentOS / Rocky)
```bash
# Assign interface to public zone
sudo firewall-cmd --zone=public --add-interface=eth0 --permanent

# Open HTTP and HTTPS services
sudo firewall-cmd --zone=public --add-service=http --permanent
sudo firewall-cmd --zone=public --add-service=https --permanent

# Reload ruleset to activate changes
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

---

## 8. Container & Cloud Virtualization Networking

### Docker Network Drivers & iptables NAT Plumbing

Docker automatically manages network interfaces and iptables rules for container isolation and port binding.

```
+-------------------------------------------------------------------+
| HOST OS                                                           |
|                                                                   |
|   Physical NIC (eth0)         Docker Bridge (docker0)             |
|   [ 192.168.1.50 ]             [ 172.17.0.1/16 ]                   |
|         ^                            ^                            |
|         | (NAT / iptables)           |                            |
|         +----------------------------+                            |
|                                      |                            |
|                            veth Pair Interconnect                 |
|                                      |                            |
|                                      v                            |
|                          Container Network Namespace              |
|                          [ eth0: 172.17.0.2/16 ]                  |
|                          App Service (e.g. Nginx :80)             |
+-------------------------------------------------------------------+
```

#### Docker Network Management Commands:
```bash
# List all active Docker network drivers
docker network ls

# Create a custom bridge network with specific subnet
docker network create --driver bridge --subnet 172.28.0.0/16 --gateway 172.28.0.1 app-net

# Run container attached to custom network with host port binding (8080 -> 80)
docker run -d --name web-app --network app-net -p 8080:80 nginx:alpine

# Inspect container IP assignment and network details
docker network inspect app-net
```

---

### Kubernetes CNI Fundamentals

Kubernetes offloads pod networking to CNI (Container Network Interface) plugins (e.g., Calico, Flannel, Cilium).

#### Core Kubernetes Networking Requirements:
1. **Pod-to-Pod Communication:** Every Pod gets a unique IP; Pods communicate across nodes without NAT.
2. **Node-to-Pod Communication:** Nodes communicate directly with all Pods.
3. **Service Proxying (`kube-proxy`):** Translates Virtual ClusterIPs to individual Pod IPs using `iptables` or `IPVS` load balancing.

---

### Cloud VPC Networking Concepts

- **Virtual Private Cloud (VPC):** Logically isolated virtual network defined in cloud providers (AWS, GCP, Azure).
- **Security Groups vs. NACLs:**
  - *Security Groups:* Stateful firewall applied at the Instance/ENI layer.
  - *Network ACLs (NACLs):* Stateless subnet-level barrier processed sequentially.
- **VPC Peering & Transit Gateways:** Connects disparate VPC networks across accounts or regions without internet traversal.

---

## 9. System Administration Diagnostics & Kernel Tuning

### Layer-by-Layer Troubleshooting Workflow

Always diagnose network failures systematically from physical layers up to application layers:

```
[ Layer 1: Physical/Link ] --> ip link / ethtool eth0
         |
         v
[ Layer 2: Neighbor/ARP ]  --> ip neighbor show
         |
         v
[ Layer 3: IP & Routing ]  --> ip addr / ip route / ping 8.8.8.8
         |
         v
[ Layer 4: Socket/Ports ]  --> ss -tulnp / nc -zv host port
         |
         v
[ Layer 7: Application ]   --> curl -vvv / dig domain / journalctl
```

---

### Packet Capture Masterclass (`tcpdump` & `tshark`)

`tcpdump` captures raw network packets for low-level protocol inspection.

```bash
# Capture 100 packets on eth0, disable hostname resolution (-n), print verbose timestamp
sudo tcpdump -i eth0 -n -c 100 -vvv

# Filter: Capture HTTP/HTTPS traffic to/from host 192.168.1.100
sudo tcpdump -i eth0 -n "host 192.168.1.100 and (port 80 or port 443)"

# Capture TCP SYN packets (connection initializations) only
sudo tcpdump -i eth0 -n "tcp[tcpflags] & (tcp-syn) != 0"

# Capture DNS requests and dump packet payloads in ASCII and Hex (-X)
sudo tcpdump -i eth0 -n -X -s 0 "udp port 53"

# Save capture stream to a PCAP file for offline analysis in Wireshark
sudo tcpdump -i eth0 -n -w /tmp/capture.pcap "tcp port 80"

# Read back saved PCAP file using tshark command line filter
tshark -r /tmp/capture.pcap -Y "http.request.method == GET"
```

---

### Production Network Troubleshooting Table

| Symptom / Error | Root Cause Hypothesis | Verification / Diagnostic Command | Resolution Command / Strategy |
|---|---|---|---|
| `Destination Host Unreachable` | Missing gateway route or broken local ARP resolution | `ip route get <IP>`<br>`ip neighbor show` | Add missing route with `ip route add`<br>Check interface state `ip link set dev <if> up` |
| `Connection refused` | Target service not listening or firewall dropping SYN-ACK | `ss -tulnp \| grep <port>`<br>`nc -zv <IP> <port>` | Start service (`systemctl start <svc>`) or check firewall rules (`iptables -L -n`) |
| Hostname lookup takes 10+ seconds then times out | Unresponsive primary DNS server in `/etc/resolv.conf` | `dig @<DNS_IP> example.com`<br>`time host google.com` | Update `/etc/resolv.conf` with responsive resolver or fix `systemd-resolved` config |
| Packet loss / High latency under load | NIC buffer overrun, duplex mismatch, or MTU mismatch | `ip -s link show dev eth0`<br>`ethtool eth0` | Adjust ring buffer (`ethtool -G eth0 rx 4096 tx 4096`) or lower MTU (`ip link set dev eth0 mtu 1460`) |
| TCP connection hangs during large file uploads | Path MTU Discovery (PMTUD) blocked by firewall ICMP filtering | `ping -M do -s 1472 <IP>` | Allow ICMP Type 3 Code 4 (Fragmentation Needed) in firewall rules |

---

### Kernel Network Stack Tuning (`sysctl.conf`)

High-throughput Linux servers (web proxies, databases, k8s nodes) require kernel network stack optimization under heavy socket load.

#### `/etc/sysctl.d/99-network-performance.conf`
```ini
# Increase maximum socket receive and send buffer sizes for high bandwidth
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# Increase default TCP window buffer allocation: min, default, max
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# Increase maximum backlog queue length for incoming connections
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 16384

# Enable TCP SYN Cookies to protect against SYN Flood DDoS attacks
net.ipv4.tcp_syncookies = 1

# Reuse TIME_WAIT sockets for outgoing connections when safe
net.ipv4.tcp_tw_reuse = 1

# Expand local ephemeral port range for outgoing client connections
net.ipv4.ip_local_port_range = 1024 65535
```

```bash
# Apply sysctl settings without rebooting
sudo sysctl --system
```

---

## 10. Production Hands-On Labs

### Lab 1: Multi-Interface Network Config with Netplan & NetworkManager

#### Objective:
Configure dual network interfaces on a system (Interface 1: DHCP internet access; Interface 2: Static internal management network `10.50.0.100/24`).

#### Tasks & Commands:

```bash
# 1. Identify active network interfaces
ip link show

# 2. Configure Netplan (Ubuntu/Debian)
sudo cat << 'EOF' | sudo tee /etc/netplan/02-dual-nic.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
    eth1:
      dhcp4: false
      addresses:
        - 10.50.0.100/24
EOF

sudo netplan apply

# 3. Verify static IP configuration on eth1
ip -4 addr show dev eth1
```

---

### Lab 2: Virtual Router & Isolated Namespaces with NAT

#### Objective:
Create an isolated network namespace (`isolated-ns`), connect it via a veth pair to the host, enable IP forwarding, and configure iptables MASQUERADE NAT so the namespace can ping internet IPs (`8.8.8.8`).

```bash
# Step 1: Enable IP Forwarding on host
sudo sysctl -w net.ipv4.ip_forward=1

# Step 2: Create namespace and veth pair
sudo ip netns add isolated-ns
sudo ip link add veth-host type veth peer name veth-ns
sudo ip link set veth-ns netns isolated-ns

# Step 3: Assign IPs and bring interfaces UP
sudo ip addr add 172.20.0.1/24 dev veth-host
sudo ip link set veth-host up

sudo ip netns exec isolated-ns ip addr add 172.20.0.2/24 dev veth-ns
sudo ip netns exec isolated-ns ip link set dev veth-ns up
sudo ip netns exec isolated-ns ip link set dev lo up

# Step 4: Configure default routing inside namespace
sudo ip netns exec isolated-ns ip route add default via 172.20.0.1

# Step 5: Setup MASQUERADE NAT on host outbound interface (eth0)
sudo iptables -t nat -A POSTROUTING -s 172.20.0.0/24 -o eth0 -j MASQUERADE
sudo iptables -A FORWARD -i veth-host -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o veth-host -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Step 6: Test internet connectivity from inside isolated namespace
sudo ip netns exec isolated-ns ping -c 4 8.8.8.8
```

---

### Lab 3: Production Firewall Hardening & Fail2ban Integration

#### Objective:
Build an iptables ruleset that drops all default inbound connections, permits SSH/HTTP/HTTPS, rate-limits SSH, and prevents unauthorized port scanning.

```bash
# 1. Flush existing rules
sudo iptables -F
sudo iptables -X

# 2. Default drop policy
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# 3. Allow loopback and established connections
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 4. Allow SSH with connection rate limiting (max 4 new connections per minute per IP)
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set --name SSH_CHECK
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 --name SSH_CHECK -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT

# 5. Allow HTTP and HTTPS
sudo iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT

# 6. Save rule state
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

### Lab 4: Deep Packet Capture & Traffic Analysis

#### Objective:
Capture and analyze DNS queries and HTTP connections live using `tcpdump`, filtering specific fields.

```bash
# 1. Open Terminal 1: Start tcpdump monitoring port 53 (DNS)
sudo tcpdump -i any -n -vvv "udp port 53"

# 2. Open Terminal 2: Perform DNS lookup
dig api.github.com

# 3. Capture raw payload of HTTP requests to a local file
sudo tcpdump -i eth0 -n -s 0 -w /tmp/http_traffic.pcap "tcp port 80"

# 4. Inspect captured HTTP packets using tshark CLI filters
tshark -r /tmp/http_traffic.pcap -Y "http.request" -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
```

---

### Lab 5: Enterprise LACP Bonding & VLAN Trunking

#### Objective:
Combine two interfaces (`eth1`, `eth2`) into an 802.3ad LACP bond (`bond0`), and create a VLAN sub-interface for VLAN 20.

```bash
# 1. Create Bond master interface
sudo ip link add name bond0 type bond mode 802.3ad lacp_rate fast

# 2. Add physical slaves
sudo ip link set eth1 down
sudo ip link set eth2 down
sudo ip link set eth1 master bond0
sudo ip link set eth2 master bond0

# 3. Bring bond interface UP
sudo ip link set bond0 up

# 4. Add VLAN 20 sub-interface on top of bond0
sudo ip link add link bond0 name bond0.20 type vlan id 20
sudo ip addr add 10.20.0.50/24 dev bond0.20
sudo ip link set dev bond0.20 up

# 5. Verify bond and VLAN state
cat /proc/net/bonding/bond0
ip addr show dev bond0.20
```

---

### Lab 6: Lightweight DNS & DHCP Infrastructure with Dnsmasq

#### Objective:
Deploy `dnsmasq` as a combined local DNS server and DHCP server for a local subnet `192.168.100.0/24`.

```bash
# 1. Install dnsmasq
sudo apt-get update && sudo apt-get install -y dnsmasq

# 2. Write custom configuration
sudo cat << 'EOF' | sudo tee /etc/dnsmasq.d/lab-dnsmasq.conf
# Bind to specific internal interface
interface=eth1
domain-needed
bogus-priv

# DHCP Lease Pool Configuration
dhcp-range=192.168.100.50,192.168.100.150,255.255.255.0,24h
dhcp-option=option:router,192.168.100.1
dhcp-option=option:dns-server,192.168.100.1

# Static IP Reservations
dhcp-host=52:54:00:ab:cd:ef,db-node-01,192.168.100.20,infinite

# Upstream DNS Forwarders
server=1.1.1.1
server=8.8.8.8
EOF

# 3. Restart and test service
sudo systemctl restart dnsmasq
sudo systemctl status dnsmasq
```

---

## 11. Curated Learning Resources

1. **Linux Kernel Networking Documentation:** https://www.kernel.org/doc/html/latest/networking/
2. **Man7 iproute2 Linux Manual Pages:** https://man7.org/linux/man-pages/man8/ip.8.html
3. **Netfilter / iptables Documentation Project:** https://www.netfilter.org/documentation/
4. **DigitalOcean Linux Networking Tutorials:** https://www.digitalocean.com/community/tutorials/linux-networking-basics
5. **Red Hat Enterprise Linux 9 Networking Guide:** https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_managing_networking/
6. **Wireshark & tcpdump Packet Analysis Index:** https://www.wireshark.org/docs/wsug_html/

---

## 12. Self-Check & Skill Verification

### Core Knowledge Audit
- [ ] Can you contrast the 7-layer OSI model against the 4-layer TCP/IP architecture?
- [ ] Can you calculate network IDs, broadcast addresses, and usable IPs for `/27`, `/29`, and `/30` subnets?
- [ ] Can you explain the difference between IPv6 Link-Local (`fe80::/10`) and Global Unicast (`2000::/3`) addresses?
- [ ] Can you map legacy commands (`ifconfig`, `route`, `arp`, `netstat`) to their modern `iproute2` equivalents (`ip addr`, `ip route`, `ip neighbor`, `ss`)?

### Operational & Administrative Skills
- [ ] Can you write persistent static network configurations in Netplan, NetworkManager (`nmcli`), and `systemd-networkd`?
- [ ] Can you create, interconnect, and route traffic between isolated Linux Network Namespaces using `veth` pairs?
- [ ] Can you configure active-backup or LACP 802.3ad network interface bonding in Linux?
- [ ] Can you configure stateful firewall rules with `iptables` and `nftables` that drop invalid traffic and implement MASQUERADE NAT?
- [ ] Can you isolate network performance issues using `tcpdump`, `ss`, `mtr`, and `ip -s link` under heavy socket loads?

---

## Next Steps
→ Continue to [[08 - Containers]] to explore how network namespaces, bridges, and veth devices power modern containerization platforms like Docker and Podman.
