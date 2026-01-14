# Blender Mesh Snapshots

## WARNING: THIS IS STILL IN DEVELOPMENT AND THIS VERSION IS ONLY AN ALPHA VERSION, USE AT YOUR OWN RISK

A Blender addon that allows you to save and restore mesh states with ease.

## Requirements
- **Blender**: Version 5.0.1

## Features

- **Save Snapshots**: Capture complete mesh states at any point
- **Restore States**: Return to any previous snapshot instantly
- **Snapshot Management**: Delete individual snapshots or clear all at once
- **Efficient Storage**: Compact JSON file format
- **Detailed Information**: View statistics for each snapshot (vertices, faces, file size)
- **Customizable**: Configure storage location, limits, and UI preferences

## Installation

### Method 1: Install via ZIP (Recommended)
1. Download all files maintaining the folder structure
2. Compress the `mesh_history_manager` folder into a ZIP file
3. In Blender: `Edit → Preferences → Add-ons → Install`
4. Select the ZIP file
5. Enable the addon by checking the checkbox

### Method 2: Manual Installation
1. Locate your Blender addons folder
2. Copy the complete `mesh_history_manager` zip into the addons directory
3. Restart Blender
4. Enable in `Edit → Preferences → Add-ons`

## How to Use
1. Open the sidebar (press `N` key)
2. Navigate to the "Mesh History" tab
3. Select a mesh object
4. Click "Save Snapshot" to capture the current state
5. Make modifications to your mesh
6. Use the restore button (↻) to return to any saved snapshot
7. Use the delete button (🗑️) to remove unwanted snapshots

If you enconter any issues please report.

Special thanks to:
 - My wonderfull GF <3 (she asked me to do it because it would help her)
