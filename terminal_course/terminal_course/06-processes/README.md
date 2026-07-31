# Module 6: Managing Processes

## Introduction

Every time you run a command or open a program, your computer starts a **process**. Understanding how to view, manage, and control processes is essential for any terminal user.

In this module, you'll learn to:
- See what's running on your computer
- Start and stop processes
- Run things in the background
- Manage system resources

---

## What Is a Process?

A **process** is a running instance of a program. When you type `ls`, the shell starts a process that runs the `ls` program, shows output, and then exits.

Every process has:
- A **PID** (Process ID) — a unique number
- A **parent process** (usually the shell)
- **Resources** — memory, CPU time, open files
- A **state** — running, sleeping, stopped, zombie

---

## Viewing Processes

### 1. `ps` — Process Status

```bash
ps              # Show your current shell's processes
ps aux          # Show ALL processes on the system (detailed)
ps -ef          # Another way to show all processes
ps aux | grep firefox   # Find a specific process
```

**Understanding `ps aux` output:**

```
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
user     12345  0.1  0.5  12345  6789 pts/0    S+   10:00   0:01 bash
```

| Column | Meaning |
|--------|---------|
| `USER` | Who owns the process |
| `PID` | Process ID (unique number) |
| `%CPU` | CPU usage percentage |
| `%MEM` | Memory usage percentage |
| `VSZ` | Virtual memory size |
| `RSS` | Resident memory size (actual RAM used) |
| `TTY` | Terminal associated with the process |
| `STAT` | Process state |
| `START` | When it started |
| `TIME` | CPU time used |
| `COMMAND` | The command that started it |

### Process States (STAT column)

| Code | Meaning |
|------|---------|
| `R` | Running |
| `S` | Sleeping (waiting for something) |
| `T` | Stopped |
| `Z` | Zombie (finished but not cleaned up) |
| `D` | Uninterruptible sleep |
| `+` | Foreground process |
| `s` | Session leader |
| `l` | Multi-threaded |

### 2. `top` — Interactive Process Viewer

```bash
top
```

Shows a live, updating list of processes sorted by CPU usage.

**Navigation in `top`:**
- `q` — Quit
- `k` — Kill a process (enter PID)
- `r` — Renice a process (change priority)
- `Space` — Update immediately
- `h` — Help
- `M` — Sort by memory
- `P` — Sort by CPU (default)
- `1` — Show individual CPU cores

### 3. `htop` — Better Top (If Installed)

```bash
htop
```

A more user-friendly, colorful version of `top` with mouse support!

Install it:
```bash
sudo apt install htop    # Ubuntu/Debian
brew install htop        # macOS
```

---

## Finding Processes

### Find by Name with `pgrep`

```bash
pgrep firefox           # Get PID of firefox
pgrep -l firefox        # Get PID and name
pgrep -a firefox        # Get PID and full command
```

### Find by Name with `pidof`

```bash
pidof firefox           # Get PID(s) of firefox
```

### Search with `ps` and `grep`

```bash
ps aux | grep firefox
```

> 💡 **Tip**: The `grep` process itself will appear in the output! You can filter it out: `ps aux | grep firefox | grep -v grep`

---

## Controlling Processes

### 1. Running in the Background (`&`)

Add `&` at the end of a command to run it in the background:

```bash
firefox &
```

The terminal shows a job number and PID, then returns to the prompt immediately.

### 2. `jobs` — See Background Jobs

```bash
jobs
```

Shows jobs running in the background in your current shell.

### 3. `fg` — Bring to Foreground

```bash
fg              # Bring most recent job to foreground
fg %1           # Bring job number 1 to foreground
```

### 4. `bg` — Send to Background

If you stopped a foreground job with `Ctrl + Z`, you can resume it in the background:

```bash
bg              # Resume most recent job in background
bg %1           # Resume job 1 in background
```

### 5. Stopping a Foreground Process (`Ctrl + Z`)

Press `Ctrl + Z` to **pause** (suspend) a running foreground process. It doesn't kill it — it just stops it. You can resume it with `fg` or `bg`.

### 6. Killing Processes (`kill`)

```bash
kill 12345              # Send SIGTERM (polite "please stop") to PID 12345
kill -9 12345           # Send SIGKILL (force kill, cannot be ignored)
kill -15 12345          # Same as default (SIGTERM)
killall firefox         # Kill all processes named "firefox"
pkill firefox           # Same as killall
```

**Signal Numbers:**

| Signal | Number | Meaning |
|--------|--------|---------|
| `SIGHUP` | 1 | Hang up (terminal closed) |
| `SIGINT` | 2 | Interrupt (same as Ctrl+C) |
| `SIGKILL` | 9 | Force kill (cannot be caught or ignored) |
| `SIGTERM` | 15 | Terminate (polite request to stop) |
| `SIGSTOP` | 19 | Stop (same as Ctrl+Z) |
| `SIGCONT` | 18 | Continue (resume a stopped process) |

**When to use what:**
- First try `kill PID` (SIGTERM) — polite
- If that doesn't work, `kill -9 PID` (SIGKILL) — force
- `killall` and `pkill` kill by name instead of PID

### 7. `nice` and `renice` — Change Priority

```bash
nice -n 10 firefox      # Start firefox with lower priority
renice 5 -p 12345       # Change priority of running process
```

Priority ranges from -20 (highest) to 19 (lowest). Default is 0.

---

## Process Management Workflow

Here's a typical workflow:

```bash
# 1. Start a long-running command
sleep 100

# 2. Oops, it's taking too long. Press Ctrl+Z to pause it
# [1]+  Stopped                 sleep 100

# 3. Check your jobs
jobs
# [1]+  Stopped                 sleep 100

# 4. Resume it in the background
bg %1

# 5. Check it's running
jobs
# [1]+  Running                 sleep 100 &

# 6. Find its PID
pgrep sleep
# 12345

# 7. Kill it
kill 12345

# 8. Verify it's gone
jobs
# [1]+  Terminated              sleep 100
```

---

## Running Commands That Survive Logout

### `nohup` — No Hang Up

```bash
nohup long-running-command &
```

The process keeps running even if you close the terminal. Output goes to `nohup.out`.

### `disown`

```bash
long-running-command &
disown
```

Removes the job from the shell's job table so it won't be killed when you exit.

### `tmux` and `screen` — Terminal Multiplexers

These are advanced tools that let you:
- Run multiple terminal sessions in one window
- Detach and reattach to sessions
- Keep processes running after you disconnect

```bash
tmux new -s mysession    # Create a new session
tmux detach              # Detach (keep running in background)
tmux attach -t mysession # Reattach later
```

---

## System Resource Monitoring

### `free` — Memory Usage

```bash
free -h       # Human-readable memory info
```

### `df` — Disk Free Space

```bash
df -h         # Human-readable disk usage
```

### `du` — Directory Usage

```bash
du -sh ~      # Total size of home directory
du -h --max-depth=1 ~   # Size of each folder in home
```

### `uptime` — System Load

```bash
uptime
```

Shows how long the system has been running and the load average.

---

## Practice Exercises 🎯

### Exercise 1: Process Detective
1. Run `ps aux` and look at the output
2. Find the PID of your shell (hint: `echo $$`)
3. Run `top` and watch it for 30 seconds
4. Press `q` to quit
5. Run `htop` if you have it installed

### Exercise 2: Background Jobs
1. Run: `sleep 300 &` (sleeps for 5 minutes in background)
2. Check with `jobs`
3. Bring it to foreground with `fg`
4. Press `Ctrl + Z` to stop it
5. Check `jobs` again
6. Resume in background with `bg`
7. Find its PID with `pgrep sleep`
8. Kill it with `kill`

### Exercise 3: The Unkillable Process
1. Run: `sleep 1000 &`
2. Try to kill it politely: `kill <PID>`
3. Check if it's still there with `ps`
4. If it's still there, force kill: `kill -9 <PID>`
5. Verify it's gone

### Exercise 4: System Health Check
1. Run `free -h` — how much RAM do you have free?
2. Run `df -h` — how much disk space is left?
3. Run `uptime` — how long has your computer been running?
4. Run `ps aux | wc -l` — how many processes are running?

---

## Key Takeaways

- ✅ `ps aux` shows all processes; `top` shows live process info
- ✅ Every process has a unique PID
- ✅ `&` runs commands in the background
- ✅ `Ctrl + Z` pauses, `fg` brings to front, `bg` resumes in background
- ✅ `kill PID` stops a process; `kill -9 PID` forces it
- ✅ `killall` and `pkill` kill by process name
- ✅ `nohup`, `tmux`, and `screen` keep processes running after logout
- ✅ `free`, `df`, `du`, `uptime` monitor system resources

---

## Next Up

In **Module 7**, we'll learn about **pipes and redirection** — one of the most powerful features of the terminal! You'll learn to chain commands together and control where output goes.

> 📝 **Homework**: 
> 1. Open `top` and identify the 5 processes using the most CPU
> 2. Practice starting, stopping, and killing background jobs
> 3. Check your system's memory and disk usage
