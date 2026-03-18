import os
import shutil

source_file = "sample.txt"
backup_file = "sample_backup.txt"

if os.path.exists(source_file):
    shutil.copy(source_file, backup_file)
    print("Backup created:", backup_file)
else:
    print("Source file does not exist.")

if os.path.exists(backup_file):
    os.remove(backup_file)
    print("Backup file deleted safely.")
else:
    print("Backup file was not found.")