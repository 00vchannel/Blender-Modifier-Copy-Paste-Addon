# Blender Modifier Copy Paste and Remove Specifically 

A simple Blender 4.1+ add-on that lets you easily copy multiple specific modifiers to all selected objects, supporting both single and multiple modifier operations.

![Image](https://github.com/user-attachments/assets/d811f0d8-ff34-4847-82a6-7eb7edaf3ff5)

- Support multiple objects pasting

![Image](https://github.com/user-attachments/assets/25d03420-1bab-4194-b2ed-38bda16dc7f8)

- Support Remove specific modifier now!

![Image](https://github.com/user-attachments/assets/883a8a26-bd87-489a-ac89-bbc1391e8546)

## Features

- Copy single modifiers with precise control
- Copy multiple specific modifiers at once with checkbox selection
- Paste all copied modifiers to any object with a single click
- Special handling for complex modifier properties
- Proper copying of vector values, colors, and object references
- Intuitive UI in its own dedicated sidebar panel
- Helpful feedback showing which modifiers are currently copied

## How to Use

### Download from GitHub

- Click the green "Code" button on this page
- Select "Download ZIP"
- Extract the ZIP file

### Install the add-on

- In Blender: Edit > Preferences > Add-ons > Install
- Select the extracted `Modifier0w0 addon.py` file
- Enable the add-on (check the box)

### Use the add-on

**Copying modifiers:**
- Select an object with modifiers in Object Mode
- Open the sidebar with N key and find "Modifier Copy Paste" tab
- Choose "Copy Multiple Modifiers" to select several specific modifiers using checkboxes
- Choose "Copy Single Modifier" for just one modifier

**Pasting modifiers:**
- Select a target object
- Click "Paste All Modifiers" to apply all copied modifiers to another object

## Advanced Usage

- Select only the modifiers you need by using the checkbox interface
- The add-on shows a list of currently copied modifiers in the panel
- Special handling for referenced objects and vertex groups
- Warnings for modifier types that may need manual adjustment after pasting

## Requirements

- Blender 4.1 or newer
