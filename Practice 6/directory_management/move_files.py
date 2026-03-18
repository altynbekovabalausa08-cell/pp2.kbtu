
import os
import shutil

os.makedirs("folder_a", exist_ok=True)
os.makedirs("folder_b", exist_ok=True)

file_path = os.path.join("folder_a", "demo.txt")
with open(file_path, "w") as f:
    f.write("This file will be copied and moved.")

shutil.copy(file_path, os.path.join("folder_b", "demo_copy.txt"))
print("File copied to folder_b/demo_copy.txt")

shutil.move(file_path, os.path.join("folder_b", "demo_moved.txt"))
print("File moved to folder_b/demo_moved.txt")