import glob
import os
import shutil
import subprocess

# Define the source and destination paths
source_main_py = 'main.py'
source_src_folder = 'src'
destination_folder = 'sentient_blobs'

app_name = 'sentient_blobs'
title = 'Sentient Blobs'
icon = 'favicon.png'

# Create the destination folder if it doesn't exist
os.makedirs(destination_folder, exist_ok=True)

# Copy main.py to the destination folder
shutil.copy(source_main_py, destination_folder)
shutil.copy('settings.py', destination_folder)
shutil.copy('config-feedforward.txt', destination_folder)
shutil.copy('requirements.txt', destination_folder)

# Copy the src folder to the destination folder
# Create winners folder if it doesn't exist
os.makedirs(os.path.join(destination_folder, 'winners'), exist_ok=True)
# Instead of using shutil.copytree, we'll manually copy the src folder to ensure we have more control
# and can easily modify or add to this process in the future.
# Get a list of all files in the source_src_folder
files = glob.glob(os.path.join('winners', '*'))

# Sort the files based on their creation time in descending order
files.sort(key=os.path.getctime, reverse=True)

# Get the last 100 files
latest_files = files[:100]

# Copy the latest files to the destination folder
for file in latest_files:
    shutil.copy(file, os.path.join(destination_folder, file))

shutil.copytree(source_src_folder, os.path.join(destination_folder, 'src'), dirs_exist_ok=True)

# To ensure compatibility and to handle different operating systems, we'll use subprocess.call()
# This allows us to specify the command and arguments as a list, making it more portable.
subprocess.call(['pygbag', '--build', destination_folder])

# Move sentient_blobs/build folder to root folder
shutil.move('sentient_blobs/build', 'build')

# Delete the destination folder
shutil.rmtree(destination_folder)