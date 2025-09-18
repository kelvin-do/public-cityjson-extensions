#!/usr/bin/env python3
"""
Script to process selectedimages.txt and update selections.json
"""

import json
import os

def process_selected_images():
    """
    Read selectedimages.txt and extract image IDs to update selections.json
    """
    selected_images_file = "selectedimages.txt"
    selections_file = "selections.json"
    
    if not os.path.exists(selected_images_file):
        print(f"Error: {selected_images_file} not found")
        return False
    
    # Read the file and extract image IDs (every odd line)
    selected_image_ids = []
    with open(selected_images_file, 'r') as f:
        lines = f.readlines()
    
    for i in range(0, len(lines), 2):  # Every odd line (0, 2, 4, ...)
        if i < len(lines):
            image_id = lines[i].strip()
            if image_id:
                selected_image_ids.append(image_id)
    
    print(f"Found {len(selected_image_ids)} selected images")
    
    # Create selections data
    selections_data = {
        "selected_images": selected_image_ids
    }
    
    # Write to selections.json
    try:
        with open(selections_file, 'w') as f:
            json.dump(selections_data, f, indent=2)
        print(f"Updated {selections_file} with {len(selected_image_ids)} selected images")
        return True
    except Exception as e:
        print(f"Error writing selections file: {e}")
        return False

if __name__ == "__main__":
    success = process_selected_images()
    if success:
        print("\nSelections processed successfully!")
        print("Now run: python images_test_tiles/make_interactive_table.py")
        print("to regenerate the HTML with the pre-selected images.")
    else:
        print("Failed to process selections.")
