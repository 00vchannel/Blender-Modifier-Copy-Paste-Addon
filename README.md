# Blender Modifier Copy Paste and Remove Specifically

A simple Blender 4.1+ add-on that lets you easily copy, paste, and remove multiple specific modifiers across all selected objects. The add-on supports both single and multiple modifier operations.

- **Support multiple objects pasting!** (27/02/2025)

![Image](https://github.com/user-attachments/assets/25d03420-1bab-4194-b2ed-38bda16dc7f8)

- **Support Remove specific modifier now!** (28/02/2025)

![Image](https://github.com/user-attachments/assets/883a8a26-bd87-489a-ac89-bbc1391e8546)

## Features

- Copy single modifiers with precise control
- Copy multiple specific modifiers at once with checkbox selection
- Paste all copied modifiers to any object with a single click
- **Remove specific modifiers from selected objects easily**
- Special handling for complex modifier properties
- Proper copying of vector values, colors, and object references
- Intuitive UI in its own dedicated sidebar panel
- Helpful feedback showing which modifiers are currently copied

## How to Use

### Download from GitHub

- Click the green **"Code"** button on this page
- Select **"Download ZIP"**
- Extract the ZIP file

### Install the Add-on

- In Blender: **Edit > Preferences > Add-ons > Install**
- Select the extracted `Modifier0w0 addon.py` file
- Enable the add-on (check the box)

### Using the Add-on

#### Copying Modifiers
- **Select** an object with modifiers in Object Mode.
- Open the sidebar with the **N key** and go to the **"Modifier0w0"** tab.
- Choose **"Copy Multiple Modifiers"** to select several specific modifiers using checkboxes.
- Alternatively, choose **"Copy Single Modifier"** to copy just one modifier.

#### Pasting Modifiers
- **Select** a target object.
- Click **"Paste All Modifiers"** to apply all copied modifiers to the target object.

#### Removing Specific Modifiers
- **Select** the object(s) from which you want to remove modifiers.
- In the **"Modifier0w0"** tab in the sidebar, navigate to the modifier list.
- Check the box next to each modifier you wish to remove.
- Click **"Remove Selected Modifiers"** to delete the chosen modifiers from all selected objects.
- **Note:** Removal is generally permanent. The add-on may display a warning prompt to prevent accidental deletion, so double-check your selections before confirming.

## Advanced Usage

- **Selective Modifier Management:** Use the checkbox interface to specifically choose which modifiers to copy or remove.
- **Live Feedback:** The add-on displays a list of currently copied modifiers on the panel.
- **Handling Complex Data:** Special care is taken for modifiers referencing objects, vertex groups, and other non-primitive types.
- **Compatibility Warnings:** Some modifier types may require manual adjustment after pasting or removing due to their unique properties.

## Requirements

- Blender 4.1 or newer
