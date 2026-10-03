# Module 9: Networking Commands

## Introduction

The terminal is your window into the network! Whether you're troubleshooting a slow connection, downloading files, or checking if a website is up, networking commands are essential tools in your arsenal.

In this module, we'll cover:
- Checking your network configuration
- Testing connectivity
- Downloading files
- Inspecting network traffic
- Remote connections with SSH

---

## `ip` and `ifconfig` — Network Interfaces

### `ip` (Modern — Recommended)

```bash
ip addr                    # Show all network interfaces and IPs
ip addr show eth0          # Show specific interface
ip link                    # Show interface status (up/down)
ip route                   # Show routing table
ip neigh                   # Show ARP table (neighbor devices)
```

### `ifconfig` (Legacy)

```bash
ifconfig                   # Show all interfaces
ifconfig eth0              # Show specific interface
```

> 💡 **Note**: `ifconfig` is deprecated on many modern systems. Use `ip` instead!

### Understanding the Output

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
    inet6 ::1/128 scope host
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
    link/ether aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.100/24 brd 192.168.1.255 scope global dynamic eth0
    inet6 fe80::... scope link
```

| Part | Meaning |
|------|---------|
| `lo` | Loopback interface (localhost, 127.0.0.1) |
| `eth0` | Ethernet interface (wired connection) |
| `wlan0` | Wireless interface (WiFi) |
| `inet` | IPv4 address |
| `inet6` | IPv6 address |
| `link/ether` | MAC address |
| `UP` | Interface is active |

---

## `ping` — Test Connectivity

```bash
ping google.com             # Send packets to google.com
ping -c 4 google.com        # Send exactly 4 packets
ping -i 2 google.com        # Wait 2 seconds between packets
ping -s 1024 google.com     # Send larger packets (1024 bytes)
```

**Understanding ping output:**

```
PING google.com (142.250.80.46) 56(84) bytes of data.
64 bytes from ...: icmp_seq=1 ttl=117 time=15.3 ms
64 bytes from ...: icmp_seq=2 ttl=117 time=14.8 ms
```

| Field | Meaning |
|-------|---------|
| `icmp_seq` | Sequence number |
| `ttl` | Time To Live (how many hops the packet can survive) |
| `time` | Round-trip time in milliseconds |

Press `Ctrl + C` to stop pinging.

---

## `curl` — Transfer Data from URLs

`curl` is incredibly versatile for downloading and interacting with web services.

### Download a File

```bash
curl -O https://example.com/file.zip        # Save with original filename
curl -o myfile.zip https://example.com/file.zip  # Save with custom name
curl -L -o file.zip https://bit.ly/short     # Follow redirects
```

### View Headers

```bash
curl -I https://google.com                  # Show response headers only
curl -v https://google.com                  # Verbose (show everything)
```

### Send Data (POST Requests)

```bash
curl -X POST -d "name=John&age=25" https://api.example.com/submit
curl -X POST -H "Content-Type: application/json" -d '{"name":"John"}' https://api.example.com/submit
```

### Download with Progress

```bash
curl -# -O https://example.com/largefile.zip    # Show progress bar
curl -C - -O https://example.com/largefile.zip  # Resume interrupted download
```

### Common `curl` Options

| Option | Meaning |
|--------|---------|
| `-O` | Save with original filename |
| `-o file` | Save with custom filename |
| `-L` | Follow redirects |
| `-I` | Show headers only |
| `-v` | Verbose output |
| `-s` | Silent (no progress) |
| `-S` | Show errors even in silent mode |
| `-f` | Fail silently on HTTP errors |
| `-H` | Add custom header |
| `-d` | Send POST data |
| `-X` | Specify HTTP method |
| `-u` | User authentication |
| `-k` | Allow insecure SSL connections |

---

## `wget` — Download Files

`wget` is great for downloading files, especially recursively.

### Basic Download

```bash
wget https://example.com/file.zip
wget -O myfile.zip https://example.com/file.zip
```

### Resume Downloads

```bash
wget -c https://example.com/largefile.zip
```

### Download in Background

```bash
wget -b https://example.com/largefile.zip
```

### Download Entire Websites (Be Careful!)

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent https://example.com/
```

### Common `wget` Options

| Option | Meaning |
|--------|---------|
| `-O file` | Output filename |
| `-c` | Continue partial download |
| `-b` | Background download |
| `-q` | Quiet mode |
| `--limit-rate=200k` | Limit download speed |
| `--user=USER --password=PASS` | Authentication |

---

## `nslookup` and `dig` — DNS Lookup

### `nslookup`

```bash
nslookup google.com             # Find IP address of domain
nslookup 8.8.8.8                # Reverse lookup (IP to domain)
```

### `dig` (More Detailed)

```bash
dig google.com                  # Full DNS information
dig +short google.com           # Just the IP
dig google.com A                # Only A records (IPv4)
dig google.com MX               # Mail server records
dig google.com NS               # Name server records
dig @8.8.8.8 google.com        # Use specific DNS server
```

---

## `traceroute` and `tracepath` — Trace the Route

See the path your packets take to reach a destination:

```bash
traceroute google.com
tracepath google.com            # Doesn't require root (usually)
```

Each line shows a "hop" — a router your packet passes through.

---

## `netstat` and `ss` — Network Statistics

### `ss` (Modern — Recommended)

```bash
ss -tuln                       # Show listening TCP and UDP ports
ss -tunap                      # Show all connections with processes
ss -s                          # Socket statistics summary
```

### `netstat` (Legacy)

```bash
netstat -tuln                  # Show listening ports
netstat -anp                   # Show all connections with PIDs
```

### Understanding Port Output

```
State    Recv-Q   Send-Q   Local Address:Port   Peer Address:Port   Process
LISTEN   0        128      0.0.0.0:22          0.0.0.0:*           users:(("sshd",pid=1234,fd=3))
```

| Field | Meaning |
|-------|---------|
| `LISTEN` | Waiting for connections |
| `ESTAB` | Established connection |
| `Local Address:Port` | Your computer's IP and port |
| `Peer Address:Port` | Remote computer's IP and port |
| `0.0.0.0:22` | Listening on all interfaces, port 22 (SSH) |

**Common Ports:**

| Port | Service |
|------|---------|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |
| 21 | FTP |
| 25 | SMTP (email) |
| 53 | DNS |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 8080 | Alternative HTTP |

---

## `nc` (netcat) — The Swiss Army Knife

`nc` is a versatile networking tool for reading/writing network connections.

### Test if a Port is Open

```bash
nc -zv google.com 80           # Check if port 80 is open
nc -zv google.com 443          # Check if port 443 is open
nc -zv localhost 3000          # Check local port 3000
```

### Create a Simple Server

```bash
nc -l 1234                     # Listen on port 1234
# In another terminal:
nc localhost 1234              # Connect to port 1234
# Now you can type messages back and forth!
```

### Send Data

```bash
echo "GET / HTTP/1.1\r\nHost: google.com\r\n\r\n" | nc google.com 80
```

---

## `ssh` — Secure Shell (Remote Login)

`ssh` lets you securely log into remote computers over the network.

### Basic Login

```bash
ssh username@remote-server.com
ssh user@192.168.1.100
```

### With a Specific Port

```bash
ssh -p 2222 user@server.com
```

### Run a Command Remotely

```bash
ssh user@server.com "ls -la"
ssh user@server.com "df -h"
```

### Copy Files with `scp`

```bash
scp file.txt user@server.com:/home/user/           # Upload
scp user@server.com:/home/user/file.txt ./         # Download
scp -r folder/ user@server.com:/home/user/         # Upload directory
scp -P 2222 file.txt user@server.com:/home/user/   # Custom port
```

### SSH Keys (Passwordless Login)

```bash
ssh-keygen                       # Generate a key pair
ssh-copy-id user@server.com      # Copy public key to server
ssh user@server.com              # Now login without password!
```

---

## `telnet` — Basic Network Testing

```bash
telnet google.com 80           # Test connection to port 80
```

> ⚠️ **Note**: `telnet` is unencrypted. Use `ssh` or `nc` instead for anything sensitive!

---

## `whois` — Domain Information

```bash
whois google.com               # Get domain registration info
```

---

## `host` — Simple DNS Lookup

```bash
host google.com                # Find IP address
host 142.250.80.46             # Reverse lookup
```

---

## Practice Exercises 🎯

### Exercise 1: Know Your Network
1. Run `ip addr` — what's your IP address?
2. Run `ip route` — what's your default gateway?
3. Run `ss -tuln` — what ports are listening on your machine?

### Exercise 2: Connectivity Testing
1. Ping google.com: `ping -c 4 google.com`
2. What's the average response time?
3. Trace the route: `traceroute google.com`
4. How many hops does it take?

### Exercise 3: Web Exploration
1. Check headers of a website: `curl -I https://google.com`
2. Download a file with curl: `curl -O https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore`
3. Check DNS records: `dig +short google.com`
4. Find the IP of your router: `ip route | grep default`

### Exercise 4: Port Scanning (Local Only!)
1. Check if port 22 (SSH) is open: `nc -zv localhost 22`
2. Check if port 80 is open: `nc -zv localhost 80`
3. List all listening ports: `ss -tuln`
4. What services are running on your machine?

---

## Key Takeaways

- ✅ `ip addr` shows your network interfaces and IP addresses
- ✅ `ping` tests basic connectivity to a host
- ✅ `curl` and `wget` download files and interact with web services
- ✅ `dig` and `nslookup` perform DNS lookups
- ✅ `traceroute` shows the network path to a destination
- ✅ `ss` and `netstat` show open ports and network connections
- ✅ `nc` tests ports and creates simple network connections
- ✅ `ssh` securely connects to remote machines; `scp` copies files

---

## Next Up

In **Module 10**, we'll dive into **shell scripting** — writing programs that the shell can execute! This is where you go from "using the terminal" to "programming the terminal"! 🚀

> 📝 **Homework**: 
> 1. Find your IP address and default gateway
> 2. Ping 3 different websites and compare response times
> 3. Use `curl` to check the headers of your favorite website
> 4. Try `ssh` if you have access to a remote server (or set one up!)
