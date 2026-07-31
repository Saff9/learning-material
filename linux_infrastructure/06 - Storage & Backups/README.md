# 06 - Storage & Backups

> **Phase:** 1 (Core Linux) · **Time:** ~4 weeks · **Difficulty:** ⭐⭐⭐

## What it is
**Storage and backup** are the pillars of reliable Linux systems. This module covers:
- Understanding disk anatomy (partitions, filesystems, RAID)
- Managing storage with LVM (Logical Volume Manager) and snapshots
- Implementing software RAID
- Encrypting disks with LUKS
- Creating reliable backups (full, incremental, differential)
- Using common backup tools (`tar`, `rsync`, `duplicity`, `restic`)
- Cloud storage basics (object stores, syncing)

Why you need it:
- **Data safety** – hardware failures are inevitable.
- **Flexibility** – resize, snapshot, and replicate storage on‑the‑fly.
- **Recovery** – restoring systems quickly after failures.
- **Compliance** – many regulations require secure, verifiable backups.

## Core concepts — detailed

### 1. Disk anatomy
- **Mbr vs. Gpt** – Master Boot Record (legacy) vs. GUID Partition Table (modern).
- **Partitions** – logical slices of a disk.
- **Filesystems** – ext4 (default), XFS (high performance), btrfs (snapshots, RAID).
  ```bash
  # Create a filesystem (example: ext4 on /dev/sda1)
  sudo mkfs.ext4 /dev/sda1
  ```

### 2. LVM (Logical Volume Manager)
LVM abstracts physical disks into virtual volumes for flexible resizing.

**Workflow:**
```bash
# 1. Create Physical Volumes (PVs)
sudo pvcreate /dev/sdb
sudo pvcreate /dev/sdc

# 2. Create Volume Group (VG)
sudo vgcreate data_vg /dev/sdb /dev/sdc

# 3. Create Logical Volume (LV)
sudo lvcreate -L 10G -n mylv data_vg

# Format and mount
sudo mkfs.ext4 /dev/data_vg/mylv
sudo mount /dev/data_vg/mylv /mnt/point
```

**Key commands:**
- `pvdisplay`, `vgdisplay`, `lvdisplay` (info)
- `lvextend` (resize)
- `lvremove` (delete)

### 3. LVM snapshots (read‑only copies for backup/testing)
```bash
# Create snapshot of /home (size matters)
sudo lvcreate -L 5G --snapshot /dev/data_vg/home 
    --name home_snapshot

# Mount snapshot
sudo mount /dev/data_vg/home_snapshot /mnt/home_backup
```

### 4. Software RAID (mdadm)
Common levels:
- **RAID 0** – striping (speed, no redundancy)
- **RAID 1** – mirroring (redundancy, single disk failure OK)
- **RAID 5** – striping + distributed parity
- **RAID 10** – combination (striped mirrors)

**Example (RAID1 with two disks):**
```bash
# Create RAID array
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

# Create filesystem on the array
sudo mkfs.ext4 /dev/md0

# Mount
sudo mount /dev/md0 /mnt/array

# Save config (in /etc/mdadm/)
sudo mdadm --detail --scan >> /etc/mdadm/mdadm.conf
```

### 5. Disk encryption with LUKS
**Creating an encrypted volume:**
```bash
# Create a loop device for testing (remove real device for production)
sudo cryptsetup -v lucreenc /dev/sdd

# Set password (interactive)
sudo cryptsetup -v luksFormat /dev/sdd

# Open (mount) the encrypted device
sudo cryptsetup open /dev/sdd cryptvol

# Create filesystem inside (example ext4)
sudo mkfs.ext4 /dev/mapper/cryptvol

# Mount
sudo mount /dev/mapper/cryptvol /mnt/encrypted
```

### 6. Backups – strategy & tools
#### Full backup (entire dataset) – `tar`
```bash
sudo tar -cvf /backups/home_full_$(date +%F).tar /home
```

#### Incremental backup – `rsync`
```bash
# Sync directory to a backup location (only changes)
sudo rsync -av --delete /home/ /backups/home_incremental/
```

#### Advanced backups – `duplicity` (tar+gpg)
```bash
sudo apt install duplicity

# Full backup (encrypted, compressed)
sudo duplicity full /home s3://bucket/home_full/$(date +%Y%m%d)

# Incremental backup (delta only)
sudo duplicity inc s3://bucket/home_full/$(date +%Y%m%d) s3://bucket/home_full/previous
```

#### Modern backup – `restic`
```bash
sudo apt install restic

# Initialize repository (AWS S3 example)
sudo restic init --repo s3:s3.amazonaws.com/myrepo

# Backup home (with password)
sudo restic backup --repo s3:s3.amazonaws://myrepo /home
```

### 7. Cloud object storage basics
- **AWS S3** (`aws s3 cp`), **GCS** (`gsutil cp`), **Azure Blob** (`az storage blob upload`)
- Use `rclone` for cross‑cloud sync: `rclone sync local_dir s3:bucket/`

## Free resources

1. **LVM Official Docs:** https://man7.org/linux/man-pages/man8/lvm.8.html
2. **Software RAID (mdadm) docs:** https://man7.org/linux/man-pages/man8/mdadm.8.html
3. **LUKS Guide (Cryptsetup):** https://en.wikipedia.org/wiki/Linux Unified Key Setup
4. **BackuP Tools:**
   - **tar** man page: https://man7.org/linux/man-pages/man1/tar.1.html
   - **rsync** docs: https://download.samba.org/rsync/rsync.html
   - **duplicity** GitHub: https://github.com/duplicity-ng/duplicity-ng
   - **restic** docs: https://restic.net/
5. **Tutorial:** https://www.tutorialspoint.com/linux_system_administration/linux_system_administration_storage_management.htm
6. **Overview:** https://www.linux.com/training-tutorials/storage-management-linux/
7. **Cloud storage:** https://docs.aws.amazon.com/s3/ (S3 basics)

## Practice labs (run in safe sandbox, use test directories)

### Lab 1: LVM basics
```bash
# Create PVs, VG, LV (example on loop devices for safety)
LOOP1=$(sudo losetup -f /dev/loop; sudo fdimage /dev/zero ${LOOP1}:$(echo 1G > /dev/null))
sudo pvcreate ${LOOP1}
sudo vgcreate test_vg ${LOOP1}
sudo lvcreate -L 512M -n webroot test_vg
sudo mkfs.ext4 /dev/test_vg/webroot
sudo mkdir -p /mnt/webapp
sudo mount /dev/test_vg/webroot /mnt/webapp
```

### Lab 2: LVM snapshot
```bash
# Create a snapshot of /mnt/webapp (size matters)
sudo lvcreate -L 256M --snapshot /dev/test_vg/webroot --name webroot_snapsudo mount /dev/test_vg/webroot_snapshot /mnt/webroot_backup
```

### Lab 3: Software RAID (simulate with loop devices)
```bash
# Create two loop devices as RAID1 mirror
sudo losetup -f /dev/loop; LOOP_A=$(sudo losetup -f /dev/loop)
sudo losetup -f /dev/loop; LOOP_B=$(sudo losetup -f /dev/loop)
sudo fdimage /dev/zero ${LOOP_A}:$(echo 1G > /dev/null)
sudo fdimage /dev/zero ${LOOP_B}:$(echo 1G > /dev/null)
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 ${LOOP_A} ${LOOP_B}
sudo mkfs.ext4 /dev/md0
sudo mkdir -p /mnt/raid1
sudo mount /dev/md0 /mnt/raid1
```

### Lab 4: LUKS encryption
```bash
# Use a test file instead of real disk
TEST_DISK=$(sudo losetup -f /dev/loop; sudo fdimage /dev/zero ${TEST_DISK}:$(echo 500M > /dev/null))
sudo cryptsetup -v luksFormat ${TEST_DISK}
sudo cryptsetup open ${TEST_DISK} cryptvol
sudo mkfs.ext4 /dev/mapper/cryptvol
sudo mkdir -p /mnt/encrypted
sudo mount /dev/mapper/cryptvol /mnt/encrypted
```

### Lab 5: Backup with `tar`
```bash
# Full backup of /etc
sudo tar -cvf /backups/etc_backup_$(date +%F).tar /etc
```

### Lab 6: Incremental backup with `rsync`
```bash
# Sync /var/log daily
sudo rsync -av --delete /var/log/ /backups/log_incremental/
```

## Self‑check (can you…)
- [ ] Explain differences between MBR and GPT, partitions and filesystems
- [ ] Create a logical volume with LVM and resize it
- [ ] Configure a software RAID 1 array
- [ ] Encrypt a disk (or test device) with LUKS
- [ ] Perform a full backup (`tar`) and incremental backup (`rsync`)
- [ ] Compare backup tools (`tar`, `rsync`, `duplicity`, `restic`) and choose appropriately

## Progress
- [ ] Completed LVM basics (PV → VG → LV creation, mount)
- [ ] Done LVM snapshot (create and mount)
- [ ] Performed RAID creation (informational)
- [ ] Explored LUKS encryption (setup and mount)
- [ ] Created backups with `tar` (full) and `rsync` (incremental)

## Next
→ [[07 - Security & Auditing]]
