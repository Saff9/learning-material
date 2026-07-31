# Module 5: File Permissions & Ownership

## Introduction

Have you ever tried to open a file and gotten a "Permission Denied" error? Or wondered why some files you can edit and others you can't? That's what this module is all about!

Understanding permissions is essential for:
- Security (keeping your files safe)
- Running programs and scripts
- Working on shared systems
- Being a competent Linux user

---

## The Linux Permission Model

Linux is a **multi-user system**. Multiple people can use the same computer, and permissions control what each person can do.

There are three types of users for every file:

| User Type | Symbol | Description |
|-----------|--------|-------------|
| **Owner** | `u` | The user who created the file |
| **Group** | `g` | A group of users (like "students" or "developers") |
| **Others** | `o` | Everyone else on the system |

And there are three types of permissions:

| Permission | Symbol | For Files | For Directories |
|------------|--------|-----------|-----------------|
| **Read** | `r` | View contents | List files inside |
| **Write** | `w` | Modify contents | Create/delete files inside |
| **Execute** | `x` | Run as a program | Enter the directory |

---

## Reading Permission Strings

Remember `ls -l` from Module 2? Let's look at it again:

```bash
ls -l
```

```
-rw-r--r-- 1 user group 1234 Jul 21 10:00 myfile.txt
drwxr-xr-x 2 user group 4096 Jul 21 10:00 myfolder
```

Let's break down `-rw-r--r--`:

```
-  rw-  r--  r--
│  │    │    │
│  │    │    └── Others permissions (r--)
│  │    └─────── Group permissions (r--)
│  └──────────── Owner permissions (rw-)
└─────────────── File type (- = file, d = directory)
```

| Position | Meaning |
|----------|---------|
| 1st char | File type: `-` = file, `d` = directory, `l` = link |
| 2-4 | Owner permissions (`rwx`) |
| 5-7 | Group permissions (`rwx`) |
| 8-10 | Others permissions (`rwx`) |

### Examples

| Permission String | Meaning |
|-------------------|---------|
| `-rw-r--r--` | Owner can read/write, group can read, others can read |
| `-rwxr-xr-x` | Owner can do everything, group/others can read and execute |
| `-rw-------` | Only owner can read/write, nobody else can do anything |
| `drwxr-xr-x` | Directory: owner full control, group/others can enter and list |
| `-rwxrwxrwx` | Everyone can do everything (dangerous!) |

---

## Changing Permissions with `chmod`

`chmod` = **Change Mode** (change permissions)

There are two ways to use `chmod`: **symbolic mode** and **numeric mode**.

### Method 1: Symbolic Mode

```bash
chmod u+x myscript.sh    # Add execute permission for owner
chmod g-w myfile.txt     # Remove write permission for group
chmod o+r myfile.txt     # Add read permission for others
chmod a+x myscript.sh    # Add execute for all (owner, group, others)
```

**Symbols:**
- `u` = user (owner)
- `g` = group
- `o` = others
- `a` = all (u + g + o)

**Operators:**
- `+` = add permission
- `-` = remove permission
- `=` = set exact permission

**Examples:**

```bash
chmod u=rwx,g=rx,o=r myfile.txt    # Set exact permissions
chmod a+r myfile.txt               # Add read for everyone
chmod u+x,g+x myscript.sh          # Add execute for owner and group
chmod o-wx myfile.txt              # Remove write and execute for others
```

### Method 2: Numeric Mode (Octal)

This is the faster way once you learn it! Each permission has a number:

| Permission | Value |
|------------|-------|
| Read (`r`) | 4 |
| Write (`w`) | 2 |
| Execute (`x`) | 1 |
| No permission | 0 |

You add the numbers together for each user type:

| Permission | Calculation | Number |
|------------|-------------|--------|
| `rwx` | 4 + 2 + 1 | 7 |
| `rw-` | 4 + 2 + 0 | 6 |
| `r-x` | 4 + 0 + 1 | 5 |
| `r--` | 4 + 0 + 0 | 4 |
| `-wx` | 0 + 2 + 1 | 3 |
| `-w-` | 0 + 2 + 0 | 2 |
| `--x` | 0 + 0 + 1 | 1 |
| `---` | 0 + 0 + 0 | 0 |

Then you specify three digits: **owner, group, others**.

```bash
chmod 755 myscript.sh    # rwxr-xr-x
chmod 644 myfile.txt     # rw-r--r--
chmod 700 secret.txt     # rwx------ (only owner can access)
chmod 777 everything.txt  # rwxrwxrwx (everyone can do everything)
```

### Common Permission Patterns

| Command | Permission | Use Case |
|---------|------------|----------|
| `chmod 644 file` | `rw-r--r--` | Normal text files |
| `chmod 755 script` | `rwxr-xr-x` | Executable scripts/programs |
| `chmod 600 secret` | `rw-------` | Private files (passwords, keys) |
| `chmod 777 file` | `rwxrwxrwx` | **Avoid!** Too permissive |
| `chmod 755 dir` | `drwxr-xr-x` | Normal directories |

---

## Changing Ownership with `chown`

`chown` = **Change Owner**

> ⚠️ You usually need to be root (admin) to change ownership!

```bash
sudo chown newuser myfile.txt          # Change owner
sudo chown newuser:newgroup myfile.txt # Change owner and group
sudo chown :newgroup myfile.txt        # Change only group
sudo chown -R newuser myfolder/        # Recursive (for directories)
```

### Changing Group with `chgrp`

```bash
sudo chgrp developers myfile.txt
```

---

## Special Permissions

There are three special permissions that go beyond the basics:

### 1. SetUID (`s` on owner execute)

When set on an executable, it runs with the **owner's** permissions, not the user's.

```bash
chmod u+s myprogram
chmod 4755 myprogram    # 4 = setUID
```

Example: The `passwd` command needs root permissions to change passwords, but regular users can run it because it has SetUID.

### 2. SetGID (`s` on group execute)

For executables: runs with the **group's** permissions.
For directories: new files inherit the directory's group.

```bash
chmod g+s mydirectory
chmod 2755 mydirectory  # 2 = setGID
```

### 3. Sticky Bit (`t` on others execute)

On directories: only the owner can delete their own files, even if others have write permission.

```bash
chmod +t mydirectory
chmod 1755 mydirectory  # 1 = sticky bit
```

Example: `/tmp` has the sticky bit so users can't delete each other's files.

### Special Permission Numbers

| Number | Special Permission |
|--------|-------------------|
| 4 | SetUID |
| 2 | SetGID |
| 1 | Sticky Bit |

They go in front of the regular three digits:
```bash
chmod 4755 file    # SetUID + rwxr-xr-x
chmod 2755 dir     # SetGID + rwxr-xr-x
chmod 1777 dir     # Sticky bit + rwxrwxrwx
```

---

## Checking Your Identity

```bash
whoami          # Your username
id              # Your user ID, group ID, and all groups
groups          # All groups you belong to
```

---

## The `umask` Command

`umask` sets the **default permissions** for new files and directories.

```bash
umask           # Show current umask (usually 0022 or 0002)
```

Default file permissions = `666` minus umask
Default directory permissions = `777` minus umask

Example with umask `0022`:
- New files: `666 - 022 = 644` (`rw-r--r--`)
- New directories: `777 - 022 = 755` (`rwxr-xr-x`)

---

## Practice Exercises 🎯

### Exercise 1: Permission Detective
1. Go to your home directory
2. Run `ls -la`
3. Identify the permissions on:
   - Your `.bashrc` file
   - Your `Desktop` directory
   - A file you created
4. What can "others" do with your `.bashrc`?

### Exercise 2: Permission Practice
1. Create a file: `touch secret.txt`
2. Check its permissions with `ls -l`
3. Make it readable only by you: `chmod 600 secret.txt`
4. Verify with `ls -l`
5. Try to make it executable: `chmod 700 secret.txt`
6. Create a script file: `touch myscript.sh`
7. Make it executable for everyone: `chmod 755 myscript.sh`
8. Verify

### Exercise 3: Symbolic vs Numeric
1. Create `test1.txt`
2. Set permissions using symbolic mode: `chmod u=rwx,g=rx,o=r test1.txt`
3. Check with `ls -l` — what number is that?
4. Create `test2.txt`
5. Set the SAME permissions using numeric mode
6. Verify they match!

### Exercise 4: The Permission Puzzle
Figure out what `chmod` command you need for each:

| Desired Permission | Command |
|-------------------|---------|
| `rwxr-x---` | `chmod ??? file` |
| `rw-rw-r--` | `chmod ??? file` |
| `rwx------` | `chmod ??? file` |
| `r--r--r--` | `chmod ??? file` |

---

## Key Takeaways

- ✅ Three user types: Owner (`u`), Group (`g`), Others (`o`)
- ✅ Three permissions: Read (`r`=4), Write (`w`=2), Execute (`x`=1)
- ✅ `ls -l` shows permissions in the format `drwxr-xr-x`
- ✅ `chmod` changes permissions: symbolic (`u+x`) or numeric (`755`)
- ✅ `chown` changes owner; `chgrp` changes group
- ✅ Special permissions: SetUID (4), SetGID (2), Sticky Bit (1)
- ✅ `umask` controls default permissions for new files

---

## Next Up

In **Module 6**, we'll learn about **processes** — how to see what programs are running, how to start and stop them, and how to manage your system's resources!

> 📝 **Homework**: 
> 1. Check permissions on 10 files in your home directory
> 2. Create a file and practice changing its permissions with both symbolic and numeric modes
> 3. Make a script executable and try to run it (we'll learn how in the next modules!)
