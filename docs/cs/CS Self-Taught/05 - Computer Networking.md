# 05 - Computer Networking

> **Phase:** 2 (Core Engineering) · **Time:** ~4–5 weeks · **Difficulty:** ⭐⭐

## What it is
**Networking** is how computers exchange data — the protocols and layers that move a request from your browser to a server on the other side of the world and back.

## Why it matters
- Almost all modern software is **networked** (web, APIs, cloud, mobile).
- Debugging "it won't connect" requires knowing the layers.
- Foundation for web dev, security, and distributed systems.
- Frequent interview topic.

## The layers (TCP/IP model)
| Layer | Job | Examples |
|---|---|---|
| **Application** | Talks to apps | HTTP, DNS, FTP, SMTP |
| **Transport** | End-to-end delivery | TCP, UDP |
| **Internet** | Routing across networks | IP |
| **Link** | Local network hop | Ethernet, Wi-Fi |

(The OSI 7-layer model is the more detailed teaching version; TCP/IP is what's used in practice.)

## Core concepts — detailed

### IP (Internet Protocol)
- Every device has an **IP address** (IPv4 like `192.168.1.1`, IPv6 longer).
- **Packets** are routed hop-by-hop toward the destination.

### TCP vs UDP
- **TCP** — reliable, ordered, connection-based (web, email, APIs).
- **UDP** — fast, no guarantees (video calls, games, DNS).

### DNS (Domain Name System)
- Translates human names (`google.com`) → IP addresses.
- Cached at multiple levels (browser, OS, resolver).

### HTTP / HTTPS
- **Request/Response** model: client sends a request, server replies.
- Methods: `GET`, `POST`, `PUT`, `DELETE`.
- **Status codes:** 2xx success, 3xx redirect, 4xx client error, 5xx server error.
- **HTTPS** = HTTP over **TLS** (encrypted).

### TLS / SSL
- Encrypts data in transit using certificates (public/private keys).
- Why "S" matters: without it, traffic is readable by anyone on the path.

### Ports & sockets
- A **port** identifies a service (80 = HTTP, 443 = HTTPS, 22 = SSH).
- A **socket** = IP + port + protocol (an endpoint).

## Deep Dive: Network Protocols & Architecture
- **Transport Layer Deep Dive:**
  - *TCP Congestion Control*: Slow Start, Congestion Avoidance, Fast Retransmit, Fast Recovery.
  - *Multiplexing*: Using source/destination ports to differentiate application traffic.
- **Modern Web Protocols:**
  - *HTTP/2*: Multiplexing over a single TCP connection, server push, header compression (HPACK).
  - *HTTP/3*: Built on QUIC (UDP), eliminates TCP Head-of-Line blocking, faster handshakes.
  - *WebSockets*: Full-duplex, persistent connection for real-time apps.
- **Security & Encryption:**
  - *TLS Handshake*: Asymmetric encryption to securely exchange a symmetric session key.
  - *DNS/DNSSEC*: Domain Name System resolution and its secure counterpart.

## Network Troubleshooting Tools
- `ping`, `traceroute` (ICMP paths)
- `netstat` / `ss` (active connections)
- `tcpdump` / `Wireshark` (packet sniffing)
- `dig` (DNS lookups)

## Free resources
- **TeachYourselfCS — Networking**: https://teachyourselfcs.com/
- **freeCodeCamp — Computer Networking**: https://www.freecodecamp.org/news/computer-networking-how-applications-talk-over-the-internet/
- **GeeksforGeeks — Computer Networks**: https://www.geeksforgeeks.org/computer-networks/
- **Cloudflare — How the Internet Works (free explainers)**: https://www.cloudflare.com/learning/
- **Wireshark** — free packet analyzer to see real traffic: https://www.wireshark.org/

## Practice / hands-on
1. `ping google.com` — see DNS + ICMP.
2. `curl -v https://example.com` — watch the HTTP exchange.
3. `traceroute` — see the hops.
4. Open **Wireshark**, load a page, inspect packets.
5. Build a tiny HTTP server (Python `http.server` or from scratch).

## Self-check (can you…)
- [ ] Explain TCP vs UDP with examples
- [ ] Describe what DNS does, step by step
- [ ] Explain HTTPS / TLS in plain words
- [ ] Use `curl`/`ping` to debug a connection

## Progress
- [ ] Understand the TCP/IP layers
- [ ] Explain DNS + HTTP/HTTPS
- [ ] Used networking CLI tools
- [ ] Built a small server

## Next
→ [[06 - Software Engineering & Git]]
