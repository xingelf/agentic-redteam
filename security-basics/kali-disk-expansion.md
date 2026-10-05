---
title: "Expanding a Kali VM Disk (VMware + GParted)"
tags: ["security-basics", "kali", "homelab"]
---

# Expanding a Kali VM Disk (VMware + GParted)

**TL;DR** — Growing the virtual disk in VMware is only half the job. The guest
still sees unallocated space stuck behind the swap/extended partition. The fix:
delete snapshots, expand the disk, remove swap and the extended partition in
GParted, grow the main partition, then recreate swap. This walks through 50 GB to
70 GB.

## Workflow

1. VMware: delete snapshots (required to unlock disk settings).
2. VMware: expand the physical disk to 70 GB.
3. Guest: remove the existing swap and extended partitions in GParted.
4. Guest: grow the primary partition and recreate swap.

## 1. Delete snapshots in VMware

VMware locks the Expand button while any snapshot exists.

1. Shut down the VM.
2. VM > Snapshot > Snapshot Manager.
3. Select snapshots and Delete (or Delete All to merge into the current state).

This merges the data. For a safety net, copy the whole VM folder to external
storage before you start.

## 2. Expand the physical disk

1. Virtual Machine Settings > Hard Disk.
2. Click Expand.
3. Set maximum disk size to 70 GB and confirm.
4. Wait for the success message.

## 3. Clear the partition barrier in GParted

Boot Kali. The extra 20 GB shows as unallocated but is usually stuck behind an
extended partition.

```bash
sudo apt update && sudo apt install -y gparted
sudo gparted
```

1. Right-click `linux-swap` and choose Swapoff (removes the lock icon).
2. Delete `linux-swap`.
3. Delete the `extended` partition (the light-blue frame).

You now have one block of unallocated space directly right of the main `ext4`
partition.

## 4. Grow the main partition and recreate swap

1. Right-click the primary `ext4` partition > Resize/Move. Drag the right edge
   out, but leave about 2048 MB unallocated at the end for swap. Apply.
2. Right-click the remaining unallocated space > New. Create as Primary, file
   system `linux-swap`. Add.
3. Click Apply All Operations (the checkmark) in the toolbar.

## 5. Verify

```bash
df -h      # disk space
free -h    # swap status
```

## Gotcha: boot delay after resize

Recreating swap changes its UUID, so `/etc/fstab` points at a swap device that no
longer exists and boot hangs waiting for it. Find the new UUID and update fstab:

```bash
sudo blkid                     # read the new swap UUID
sudo nano /etc/fstab           # replace the old swap UUID with the new one
```

Then take a fresh snapshot as your new baseline.

## Takeaway

Resizing a Linux VM disk is two jobs: give the VM more disk, then rearrange
partitions inside the guest so the main one can actually use it. The swap/extended
partition is the usual blocker, and the forgotten step is updating `/etc/fstab`
with the new swap UUID.
