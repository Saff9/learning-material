# Module 22: POSIX System Calls

## Introduction to POSIX

POSIX (Portable Operating System Interface) is a family of standards specified by the IEEE Computer Society for maintaining compatibility between operating systems. Writing POSIX-compliant C code ensures that your programs will run on Unix-like operating systems like Linux, macOS, and BSD.

System calls are the interface between your application and the operating system kernel. When you need to interact with hardware, files, or other processes, you ask the kernel to do it for you via a system call.

## 1. File I/O (`open`, `read`, `write`, `close`)

While the C Standard Library provides `fopen`, `fread`, etc., these are built on top of lower-level POSIX system calls. These lower-level calls use integer **file descriptors** instead of `FILE *` streams.

Standard file descriptors:
- `0`: Standard Input (stdin)
- `1`: Standard Output (stdout)
- `2`: Standard Error (stderr)

### `open()`
Opens a file and returns a file descriptor.
```c
#include <fcntl.h>   // For open flags
#include <unistd.h>  // For read, write, close

// Open for writing, create if it doesn't exist, truncate to 0 length if it does.
// Permissions: rw-r--r-- (0644 in octal)
int fd = open("output.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
if (fd == -1) {
    perror("open failed"); // Prints the error
    return 1;
}
```

### `write()` and `read()`
`write` sends bytes to a file descriptor; `read` retrieves them.
```c
const char *msg = "Hello POSIX\n";
// Write to the file
ssize_t bytes_written = write(fd, msg, 12);

// Read from a file
char buffer[100];
int fd_in = open("input.txt", O_RDONLY);
ssize_t bytes_read = read(fd_in, buffer, sizeof(buffer) - 1);
if (bytes_read > 0) {
    buffer[bytes_read] = '\0'; // Null-terminate if treating as a string
}
```

### `close()`
Always close file descriptors when done to free kernel resources.
```c
close(fd);
close(fd_in);
```

## 2. Process Management (`fork`, `wait`, `exec`)

### `fork()`
`fork()` creates a new process by duplicating the calling process. The new process is the **child**, and the caller is the **parent**.
- Returns `0` to the child process.
- Returns the child's Process ID (PID) to the parent.
- Returns `-1` on failure.

```c
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>

pid_t pid = fork();

if (pid == -1) {
    perror("fork failed");
} else if (pid == 0) {
    // Child process
    printf("I am the child. My PID is %d\n", getpid());
} else {
    // Parent process
    printf("I am the parent. Child PID is %d\n", pid);
}
```

### `wait()` and `waitpid()`
Parents should wait for their children to finish to collect their exit status and prevent "zombie" processes.
```c
#include <sys/wait.h>

int status;
// Wait for any child to terminate
pid_t terminated_pid = wait(&status);

if (WIFEXITED(status)) {
    printf("Child %d exited with status %d\n", terminated_pid, WEXITSTATUS(status));
}
```

### `exec()` family
The `exec` family of functions replaces the current process image with a new process image. It's how one program launches another.
```c
#include <unistd.h>

// Child process executing "ls -l"
if (fork() == 0) {
    char *args[] = {"ls", "-l", NULL};
    execvp("ls", args);
    // If execvp succeeds, this line is NEVER reached!
    perror("execvp failed");
    return 1;
}
```

## 3. Inter-Process Communication (`pipe`)

### `pipe()`
A pipe creates a unidirectional data channel that can be used for interprocess communication, usually between a parent and child.
- `fd[0]` is the read end.
- `fd[1]` is the write end.

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

int main() {
    int fd[2];
    if (pipe(fd) == -1) {
        perror("pipe");
        return 1;
    }

    pid_t pid = fork();
    if (pid == 0) {
        // Child: writes to pipe
        close(fd[0]); // Close unused read end
        char *msg = "Message from child";
        write(fd[1], msg, strlen(msg) + 1);
        close(fd[1]); // Close write end when done
    } else {
        // Parent: reads from pipe
        close(fd[1]); // Close unused write end
        char buffer[100];
        read(fd[0], buffer, sizeof(buffer));
        printf("Parent received: %s\n", buffer);
        close(fd[0]); // Close read end
        wait(NULL);   // Wait for child
    }
    return 0;
}
```

## Practice Problems

### Problem 22.1: Simple Shell
Use `fork`, `execvp`, and `wait` to create a simple shell that loops, prompts the user for a command (like `ls` or `date`), and executes it.

### Problem 22.2: IPC with Pipes
Create a program where the parent generates an array of numbers, sends them to the child via a pipe, and the child computes and prints their sum.
\n\n## Deep Dive: POSIX System Calls\n\nPOSIX system calls like `fork()`, `exec()`, `wait()`, `pipe()`, `open()`, `read()`, `write()`, and `close()` allow C programs to interact directly with the operating system for process control, file I/O, and inter-process communication.\n