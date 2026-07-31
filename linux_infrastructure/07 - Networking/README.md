# 07 - Networking

> **Phase:** 1 (Core Linux) · **Time:** ~4 weeks · **Difficulty:** ⭐⭐⭐

## What it is
**Networking** in Linux refers to how computers communicate with each other and access the internet. It encompasses:

- **IP addressing and subnetting** (IPv4, IPv6)
- **Network layers and protocols** (OSI model, TCP/IP stack)
- **Core services** (DNS, DHCP, HTTP/HTTPS, SSH, FTP)
- **Linux networking tools** (`ip`, `netstat`, `ss`, `nmap`, `traceroute`, `dig`)
- **Firewalls and security policies** (iptables, ufw, nftables)
- **Cloud and virtualization networking** (AWS VPC, Docker networking, OpenStack)
- **Troubleshooting and monitoring** (tcpdump, Wireshark, `journalctl` for network logs)

Why it matters:
- **Internet connectivity** is essential for almost all applications and services.
- **Local networking** (LAN/WAN, VLAN, subnets) is required for internal workloads.
- **Security**—understanding network traffic helps detect anomalies and block threats.
- **DevOps**—containers, cloud, CI/CD rely heavily on networking.
- **Career**—network knowledge is a staple in sysadmin and cloud roles.

## Core concepts — detailed

### 1. OSI vs. TCP/IP layers
| Layer | OSI name | TCP/IP name | Primary protocols |
|---|---|---|---|
| 1 | Physical | Link | Ethernet, Wi-Fi, PPP |
| 2 | Data Link | Network Access | MAC addresses, Ethernet framing |
| 3 | Network | Internet | IP (v4/v6), ICMP, routing |
| 4 | Transport | Transport | TCP, UDP, SCTP |
| 5 | Session | Session (application-level) | NetBIOS, SIP, RPC |
| 6 | Presentation | Presentation | SSL/TLS, JSON, XML |
| 7 | Application | Application | HTTP, DNS, FTP, SSH |

> In practice, the TCP/IP model is more commonly used in Linux.

### 2. IP addressing
#### IPv4 basics
- **IPv4 format:** `a.b.c.d` (32‑bit, dotted‑decimal).
- **Classes:** A (`.0‑126`), B (`128‑191`), C (`192‑223`), D (`224‑239` multicast), E (`240‑255` experimental).
- **Private ranges:** `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`.
- **Subnetting:** CIDR notation `x.x.x.x/prefix`.
  - `/24` = 256 addresses (254 usable).
  - `/30` = 4 addresses (2 usable) for point‑to‑point links.

#### IPv6 basics
- **128‑bit**, eight groups of hex, colon‑separated.
- `::1` = loopback, `fe80::/10` = link‑local.
- Stateless Address Autoconfiguration (SLAAC) and DHCPv6.

**Quick commands to inspect IPv4/IPv6:**
```bash
ip addr show            # list interfaces with IPs
ip -6 addr show        # IPv6 only
```

### 3. Core network services tools
- **DNS (Domain Name System):** resolves hostnames to IPs.
  - Client side: `dig`, `nslookup`, `host`.\n  - Server side: `bind`, `pdns-recursor`.
- **DHCP (Dynamic Host Configuration Protocol):** assigns IPs dynamically.
  - Server: `dhcpd`, `dnsmasq`.
  - Client: `dhclient`, `dhclient.conf`.
- **HTTP/HTTPS:** web traffic, using `curl`, `wget`, `apache2`, `nginx`.
- **SSH (Secure Shell):** secure remote login, key‑based auth.
- **FTP/SFTP/FTPS:** file transfer, with security extensions.

### 4. Linux networking CLI tools
| Tool | Purpose | Typical use |
|---|---|---|
| `ip` | Configure interfaces, routes, neighbors | `ip route add default via 192.168.1.1` |
| `netstat` (legacy) | Show network statistics | `netstat -tulnp` |
| `ss` (socket statistics) | Modern, faster replacement | `ss -tulnp` |
| `nmap` | Port scanning & host discovery | `nmap localhost` |
| `traceroute` / `traceroute6` | Trace path to a remote host | `traceroute 8.8.8.8` |
| `dig` / `host` | DNS queries | `dig example.com` |
| `tcpdump` | Capture and analyze packets | `tcpdump -i eth0 -c 10` |
| `journalctl` | System logs (including network events) | `journalctl -u systemd-networkd` |

### 5. Firewall management
#### iptables (legacy, still widely used)
```bash
# List rules (filter table)
sudo iptables -L -n --line-numbers

# Allow SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Drop DROP all other inbound (with caution)
sudo iptables -A INPUT -j DROP

# Save rules (requires `iptables-persistent` on Debian/Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

#### UFW (Uncomplicated Firewall) – user‑friendly wrapper (Ubuntu/Debian)
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Deny incoming, allow outgoing default (default behavior)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable
sudo ufw enable
```

#### nftables (successor to iptables)
Modern, netfilter‑based.

### 6. Cloud and virtualization networking
- **Docker networking:** bridge (`bridge`), host‑network, macvlan.
- **Kubernetes networking:** overlay CNI (Flannel, Calico, Weave).
- **AWS VPC:** subnets, route tables, internet gateway, security groups.
- **Google Cloud VPC:** VPC-native, shared‑VPC, Cloud NAT.
- **Azure VNet:** subnets, gateways, network security groups.

### 7. Troubleshooting and monitoring
- **DNS resolution test:** `dig google.com`, `nslookup google.com`.
- **Connectivity test:** `ping -c 4 8.8.8.8`, `traceroute 8.8.8.8`.
- **Port open:** `nc -zv localhost 80`.
- **Log inspection:** `grep "ERROR" /var/log/syslog`, `journalctl -u sshd`.

## Free resources — curated for self‑learners

1. **Linux Networking Guide (Man Pages):** https://man7.org/linux/man-pages/man7/ip.7.html
2. **Microsoft Docs: Networking in Linux:** https://learn.microsoft.com/en-us/windows/wsl/networking
3. **DigitalOcean: Networking Basics in Linux:** https://www.digitalocean.com/community/tutorials/linux-networking-basics
4. **OverTheWire: Bandit (Wargame) – practice IP addressing and permissions:** https://overthewire.org/wargames/bandit/
5. **The Linux Server Bible (Chapter 15 – Networking):** Free chapter preview on GitHub.
6. **Docker Networking Docs:** https://docs.docker.com/network/ (bridge, host, macvlan)
7. **Network World: Linux networking cheat sheet:** https://www.networkworld.com/article/2074072/linux-networks-cheat-sheet.html
8. **IPv6 Tutorial:** https://www.ipv6anywhere.net/tutorial/

## Practice labs (run as root or with sudo, in safe test environment)

### Lab 1: Interface inspection and IP configuration
```bash
# Show interfaces and their IPs
sudo ip addr show

# Configure an IP on a dummy interface (for testing)
sudo ip addr add 192.168.100.100/24 dev dummy0 2>/dev/null || echo "dummy0 not existing"
```

### Lab 2: DNS resolution
```bash
# Query a domain via DNS
sudo dig facebook.com +short

# Trace routing to a remote server
sudo traceroute 8.8.8.8
```

### Lab 3: Simple SSH server/client test
```bash
# Start a temporary SSH server (for testing only)
# (install openssh-server first: sudo apt install openssh-server)
# Then: sudo service ssh start

# Connect from another terminal (replace with container IP)
# ssh user@<server_ip> "whoami"
```

### Lab 4: Firewall rules (iptables)
```bash
# Drop incoming ICMP (ping) from outside (optional, may affect ping within)
sudo iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# Allow HTTP (port 80) and SSH (port 22)
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# List rules
sudo iptables -L -n --line-numbers
```

### Lab 5: Docker networking
```bash
# Create a bridge network
sudo docker network create --driver bridge mynet

# Run a container on that network
sudo docker run -d --name web1 --network mynet -p 8080:80 nginx

# Inspect network
sudo docker network inspect mynet
```

### Lab 6: Monitoring with journalctl
```bash
# Journal logs for network services
sudo journalctl -u systemd-networkd -b -f

# Filter for SSH login attempts
sudo journalctl -u sshd -b | grep "Failed password"
```

## Self‑check (can you…)
- [ ] Explain OSI vs. TCP/IP layers and when each is used
- [ ] Configure a static IP on a loopback interface
- [ ] Perform DNS queries (`dig`, `nslookup`) and trace routes
- [ ] List, configure, and reset iptables/ufw rules safely
- [ ] Create a Docker network and start a container on it
- [ ] Inspect logs with `journalctl` for network‑related issues

## Progress
- [ ] Completed interface inspection and IP configuration
- [ ] Configured DNS queries and routing
- [ ] Set up firewall rules (iptables or UFW)
- [ ] Explored Docker networking (bridge, containers)
- [ ] Monitored logs with `journalctl`

## Next
→ [[08 - Containers]]
