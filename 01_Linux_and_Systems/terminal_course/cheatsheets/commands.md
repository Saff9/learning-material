# Terminal Command Cheatsheet

## Navigation

| Command | Description |
|---------|-------------|
| `pwd` | Print working directory |
| `ls` | List files |
| `ls -la` | List all files with details |
| `cd <dir>` | Change directory |
| `cd ~` | Go to home directory |
| `cd ..` | Go up one level |
| `cd -` | Go to previous directory |

## File Operations

| Command | Description |
|---------|-------------|
| `touch <file>` | Create empty file |
| `cat <file>` | Display file contents |
| `less <file>` | View file page by page |
| `head -n 10 <file>` | Show first 10 lines |
| `tail -n 10 <file>` | Show last 10 lines |
| `cp <src> <dst>` | Copy file |
| `cp -r <src> <dst>` | Copy directory |
| `mv <src> <dst>` | Move/rename file |
| `rm <file>` | Remove file |
| `rm -r <dir>` | Remove directory |
| `mkdir <dir>` | Create directory |
| `mkdir -p <path>` | Create nested directories |
| `rmdir <dir>` | Remove empty directory |

## Text Editing

| Command | Description |
|---------|-------------|
| `nano <file>` | Edit with nano |
| `vim <file>` | Edit with vim |
| `echo "text" > file` | Write text to file |
| `echo "text" >> file` | Append text to file |

## Permissions

| Command | Description |
|---------|-------------|
| `chmod 755 <file>` | Set permissions to rwxr-xr-x |
| `chmod 644 <file>` | Set permissions to rw-r--r-- |
| `chmod +x <file>` | Make file executable |
| `chown user <file>` | Change owner |
| `chgrp group <file>` | Change group |

## Processes

| Command | Description |
|---------|-------------|
| `ps aux` | Show all processes |
| `top` | Interactive process viewer |
| `htop` | Better process viewer |
| `kill <pid>` | Kill process |
| `killall <name>` | Kill by name |
| `pkill <name>` | Kill by pattern |
| `&` | Run in background |
| `fg` | Bring to foreground |
| `bg` | Send to background |
| `jobs` | List background jobs |

## Pipes & Redirection

| Command | Description |
|---------|-------------|
| `cmd > file` | Redirect stdout to file |
| `cmd >> file` | Append stdout to file |
| `cmd 2> file` | Redirect stderr to file |
| `cmd &> file` | Redirect both to file |
| `cmd1 | cmd2` | Pipe stdout to stdin |
| `cmd < file` | Redirect stdin from file |

## Searching

| Command | Description |
|---------|-------------|
| `find . -name "*.txt"` | Find files by name |
| `grep "pattern" file` | Search in file |
| `grep -r "pattern" .` | Recursive search |
| `grep -i "pattern" file` | Case-insensitive search |
| `locate <name>` | Fast file search |
| `which <cmd>` | Find command location |

## Networking

| Command | Description |
|---------|-------------|
| `ip addr` | Show IP addresses |
| `ping <host>` | Test connectivity |
| `curl <url>` | Transfer data from URL |
| `wget <url>` | Download file |
| `ssh user@host` | Remote login |
| `scp file user@host:/path` | Copy file over SSH |
| `ss -tuln` | Show listening ports |

## System Info

| Command | Description |
|---------|-------------|
| `whoami` | Current user |
| `date` | Current date/time |
| `uptime` | System uptime |
| `free -h` | Memory usage |
| `df -h` | Disk usage |
| `du -sh <dir>` | Directory size |
| `uname -a` | System information |

## Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete |
| `↑` / `↓` | Command history |
| `Ctrl + C` | Stop current command |
| `Ctrl + D` | Exit |
| `Ctrl + L` | Clear screen |
| `Ctrl + A` | Start of line |
| `Ctrl + E` | End of line |
| `Ctrl + U` | Clear to start |
| `Ctrl + K` | Clear to end |
| `Ctrl + W` | Delete word |
| `Ctrl + R` | Search history |
| `!!` | Repeat last command |
| `!$` | Last argument |
