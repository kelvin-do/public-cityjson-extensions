import os
from reportlab.lib.pagesizes import A1
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import math
import pandas as pd

def create_image_comparison_table(base_folder, output_pdf):
    """
    Create an A2 landscape PDF table comparing images across multiple folders.
    Uses only the left half of the page, leaving right half free for additional columns.
    Each row represents an image name, each column represents a folder.
    Google Earth images are placed in the first column.
    Excel data is displayed under each image name.
    """
    
    # Load Excel data
    excel_path = r"C:\Users\Leandre\Github\LOD2\Adresses_de_test.xlsx"
    df = pd.read_excel(excel_path)
    
    # Create a dictionary mapping image names to their data
    excel_data = {}
    for _, row in df.iterrows():
        image_name = str(row['ID'])
        if pd.notna(row['ID']):  # Skip rows with no ID
            excel_data[image_name] = {
                'address': str(row['Adresse']) if pd.notna(row['Adresse']) else '',
                'coordinates': str(row['Lat, Lon (mercato)']) if pd.notna(row['Lat, Lon (mercato)']) else '',
                'typology': str(row['Typologie urbaine, complexité toit, hauteur']) if pd.notna(row['Typologie urbaine, complexité toit, hauteur']) else '',
                'description': str(row['Description du cas particulier']) if pd.notna(row['Description du cas particulier']) else '',
                'manual_change': row['Recours à un changement manuel des nuages de points']
            }
    
    # A1 landscape dimensions in points (1 point = 1/72 inch)
    # A1 landscape: width > height (WIDE format)
    a1_width, a1_height = A1  # A1 portrait dimensions
    page_width = a1_height   # Swap for landscape: height becomes width
    page_height = a1_width   # Swap for landscape: width becomes height
    margin = page_width * 0.02  # 2% of page width for margin
    
    # Use full A1 landscape width for the table
    table_width = page_width  # Use full A1 landscape width
    table_height = page_height  # Use full A1 landscape height
    
    # Get all folders (excluding the script file)
    folders = [f for f in os.listdir(base_folder) 
               if os.path.isdir(os.path.join(base_folder, f)) and f != '__pycache__']
    
    # Ensure google_earth_images is first
    if 'google_earth_images' in folders:
        folders.remove('google_earth_images')
        folders.insert(0, 'google_earth_images')
    
    # Get all image names from the first folder (they should all be the same)
    if not folders:
        print("No folders found!")
        return
    
    first_folder = os.path.join(base_folder, folders[0])
    image_names = sorted([f for f in os.listdir(first_folder) 
                         if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff"))])
    
    num_cols = len(folders) + 1  # +1 for image name column
    num_rows = len(image_names)
    
    print(f"Found {len(folders)} folders and {num_rows} images")
    print(f"Folders: {folders}")
    
    # Calculate available space and cell dimensions (using A3 dimensions on left half)
    available_width = table_width - 2 * margin
    available_height = table_height - 2 * margin
    
    # Reserve space for headers (folder names) - proportional to page height
    header_height = page_height * 0.08  # 8% of page height for headers
    available_height -= header_height
    
    # Image name column width (proportional to canvas width)
    image_name_col_width = page_width * 0.15  # 15% of page width for image names
    
    # Calculate column widths for full A1 landscape width
    folder_col_width = (available_width - image_name_col_width) / len(folders)
    
    cell_height = available_height / num_rows
    
    # Create PDF with A1 landscape dimensions
    c = canvas.Canvas(output_pdf, pagesize=(page_width, page_height))
    
    # Draw headers
    font_size = 6  # Readable font size for detailed parameters
    c.setFont("Helvetica", font_size)
    
    # Draw "Image Name" header for the first column
    x = margin
    y = page_height - margin - header_height
    c.drawString(x + 5, y + 5, "Image Name")
    
    # Draw folder headers
    for i, folder_name in enumerate(folders):
        x = margin + image_name_col_width + i * folder_col_width
        
        y = page_height - margin - header_height
        
        # Calculate available width for text (with proportional padding)
        text_padding = page_width * 0.01  # 1% of page width for padding
        text_available_width = folder_col_width - 2 * text_padding
        
        # Parse folder names and create detailed descriptions
        if folder_name == 'google_earth_images':
            display_name = 'Google Earth'
        elif folder_name.startswith('cd'):
            # Parse folder name: cd20cf05pdk5pmp30eps03
            # Extract parameters
            try:
                # Find positions of parameter markers
                cd_pos = folder_name.find('cd') + 2
                cf_pos = folder_name.find('cf')
                pdk_pos = folder_name.find('pdk')
                pmp_pos = folder_name.find('pmp')
                eps_pos = folder_name.find('eps')
                
                # Extract values
                ceil_density = folder_name[cd_pos:cf_pos]
                complexity_factor = folder_name[cf_pos+2:pdk_pos]
                plane_detect_k = folder_name[pdk_pos+3:pmp_pos]
                plane_min_points = folder_name[pmp_pos+3:eps_pos]
                epsilon = folder_name[eps_pos+3:]
                
                # Convert to proper formats
                cf_float = float(complexity_factor) / 10  # 05 -> 0.5
                eps_float = float(epsilon) / 10  # 02 -> 0.2
                
                # Create detailed description
                display_name = f"Ceil Density: {ceil_density}\nComplexity Factor: {cf_float}\nPlane Detect K: {plane_detect_k}\nPlane Min Points: {plane_min_points}\nEpsilon: {eps_float}"
                
            except (ValueError, IndexError):
                # Fallback to original name if parsing fails
                display_name = folder_name
        else:
            display_name = folder_name
            
        # Draw multi-line text for detailed descriptions (left-aligned)
        if '\n' in display_name:
            # Multi-line text for detailed parameters
            lines = display_name.split('\n')
            line_height = font_size + 2  # Better spacing for readability
            start_y = y + header_height - 8  # Start from top of header area
            
            for i, line in enumerate(lines):
                # Left-align the text with proportional padding
                c.drawString(x + text_padding, start_y - i * line_height, line)
        else:
            # Single line text (left-aligned) with proportional padding
            c.drawString(x + text_padding, y + 5, display_name)
    
    # Draw image names in first column and images in other columns
    for row, image_name in enumerate(image_names):
        y = page_height - margin - header_height - (row + 1) * cell_height
        image_name_text = image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        
        # Check if this row needs light orange background
        needs_background = False
        if image_name_text in excel_data:
            manual_change_value = excel_data[image_name_text]['manual_change']
            if manual_change_value == 1.0:  # Check for 1.0 (TRUE)
                needs_background = True
        
        # Draw light orange background for image name column only if needed
        if needs_background:
            c.setFillColorRGB(1.0, 0.9, 0.8)  # Very light orange
            c.rect(margin, y, image_name_col_width, cell_height, fill=1, stroke=0)
            c.setFillColorRGB(0, 0, 0)  # Reset to black for text
        
        # Draw image name and Excel data in first column
        x = margin
        c.setFont("Helvetica", 8)
        
        # Draw image name with proportional padding
        c.drawString(x + text_padding, y + cell_height - 10, image_name_text)
        
        # Draw Excel data if available
        if image_name_text in excel_data:
            data = excel_data[image_name_text]
            c.setFont("Helvetica", 4)  # Even smaller font for full data
            
            y_offset = cell_height - 25
            
            # Draw full address
            if data['address']:
                c.drawString(x + text_padding, y + y_offset, f"Addr: {data['address']}")
                y_offset -= 6
            
            # Draw full coordinates
            if data['coordinates']:
                c.drawString(x + text_padding, y + y_offset, f"Coord: {data['coordinates']}")
                y_offset -= 6
                
            # Draw full typology
            if data['typology']:
                c.drawString(x + text_padding, y + y_offset, f"Type: {data['typology']}")
                y_offset -= 6
                
            # Draw full description
            if data['description']:
                c.drawString(x + text_padding, y + y_offset, f"Desc: {data['description']}")
        
        # Draw images in other columns
        for col, folder_name in enumerate(folders):
            folder_path = os.path.join(base_folder, folder_name)
            image_path = os.path.join(folder_path, image_name)
            
            # Calculate position for image column
            x = margin + image_name_col_width + col * folder_col_width
            
            if os.path.exists(image_path):
                # Load and scale image
                try:
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    
                    # Special handling for Google Earth images - make them square
                    if folder_name == 'google_earth_images':
                        # Calculate square dimensions with much higher resolution
                        image_padding = page_width * 0.005  # 0.5% of page width for image padding
                        square_size = min(folder_col_width - image_padding, cell_height - image_padding)
                        
                        # Use much higher resolution for better quality
                        high_res_size = int(square_size * 4)  # Quadruple resolution for crisp results
                        
                        # Crop to square from center
                        min_dim = min(img_width, img_height)
                        left = (img_width - min_dim) // 2
                        top = (img_height - min_dim) // 2
                        right = left + min_dim
                        bottom = top + min_dim
                        
                        # Crop and resize to square with maximum quality
                        img_cropped = img.crop((left, top, right, bottom))
                        img_square = img_cropped.resize((high_res_size, high_res_size), Image.Resampling.LANCZOS)
                        
                        # Center square image in cell
                        img_x = x + (folder_col_width - square_size) / 2
                        img_y = y + (cell_height - square_size) / 2
                        
                        # Save temporary image with maximum quality settings
                        temp_path = f"temp_{row}_{col}.png"
                        img_square.save(temp_path, "PNG", optimize=False, compress_level=0)
                        c.drawImage(temp_path, img_x, img_y, 
                                  width=square_size, height=square_size)
                        
                        # Clean up temporary file
                        os.remove(temp_path)
                        
                    else:
                        # Regular scaling for other images
                        image_padding = page_width * 0.005  # 0.5% of page width for image padding
                        max_width = folder_col_width - image_padding
                        max_height = cell_height - image_padding
                        
                        scale = min(max_width / img_width, max_height / img_height)
                        
                        scaled_width = img_width * scale
                        scaled_height = img_height * scale
                        
                        # Center image in cell
                        img_x = x + (folder_col_width - scaled_width) / 2
                        img_y = y + (cell_height - scaled_height) / 2
                        
                        c.drawImage(image_path, img_x, img_y, 
                                  width=scaled_width, height=scaled_height)
                    
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    # Draw placeholder text
                    c.drawString(x + 5, y + cell_height/2, "Error")
            else:
                print(f"Image not found: {image_path}")
                # Draw placeholder text
                c.drawString(x + 5, y + cell_height/2, "Missing")
    
    c.save()
    print(f"PDF created: {output_pdf}")

# Usage
if __name__ == "__main__":
    base_folder = "."  # Current directory (images_test_tiles)
    output_pdf = "image_comparison_table.pdf"
    
    # Check if we're in the right directory
    if not os.path.exists("google_earth_images"):
        print("Error: Please run this script from the images_test_tiles directory")
        print("Current directory:", os.getcwd())
        print("Expected to find 'google_earth_images' folder here")
        exit(1)
    
    create_image_comparison_table(base_folder, output_pdf)
