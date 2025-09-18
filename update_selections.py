#!/usr/bin/env python3
"""
Script to update the selections.json file with selected image IDs.
Usage: python update_selections.py [image_id1] [image_id2] ...
"""

import json
import sys
import os

def update_selections(selected_image_ids):
    """
    Update the selections.json file with the provided image IDs.
    """
    selections_file = "selections.json"
    
    # Load existing selections
    try:
        if os.path.exists(selections_file):
            with open(selections_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"selected_images": []}
    except Exception as e:
        print(f"Error loading existing selections: {e}")
        data = {"selected_images": []}
    
    # Update with new selections
    data["selected_images"] = selected_image_ids
    
    # Write back to file
    try:
        with open(selections_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Updated {selections_file} with {len(selected_image_ids)} selected images")
        return True
    except Exception as e:
        print(f"Error writing selections file: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_selections.py [image_id1] [image_id2] ...")
        print("Example: python update_selections.py img_folder1_image1.png img_folder2_image2.png")
        return
    
    selected_image_ids = sys.argv[1:]
    success = update_selections(selected_image_ids)
    
    if success:
        print("Selections updated successfully!")
        print("Now run: python images_test_tiles/make_interactive_table.py")
        print("to regenerate the HTML with the new selections.")
    else:
        print("Failed to update selections.")

if __name__ == "__main__":
    main()
