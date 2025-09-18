import os
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

def create_interactive_image_table(base_folder, output_html):
    """
    Create an interactive HTML table with hover tooltips showing bigger images.
    Same layout as the PDF version but with interactive hover effects.
    """
    
    # Load Excel data
    excel_path = r"C:\Users\Leandre\Github\LOD2\Adresses_de_test.xlsx"
    df = pd.read_excel(excel_path)
    excel_data = {}
    for _, row in df.iterrows():
        image_name = str(row['ID'])
        if pd.notna(row['ID']):
            excel_data[image_name] = {
                'address': str(row['Adresse']) if pd.notna(row['Adresse']) else '',
                'coordinates': str(row['Lat, Lon (mercato)']) if pd.notna(row['Lat, Lon (mercato)']) else '',
                'typology': str(row['Typologie urbaine, complexité toit, hauteur']) if pd.notna(row['Typologie urbaine, complexité toit, hauteur']) else '',
                'description': str(row['Description du cas particulier']) if pd.notna(row['Description du cas particulier']) else '',
                'manual_change': row['Recours à un changement manuel des nuages de points']
            }
    
    # Get all folders (excluding the script file)
    folders = [f for f in os.listdir(base_folder) 
               if os.path.isdir(os.path.join(base_folder, f)) and f != '__pycache__']
    
    # Sort folders to put google_earth_images first
    if 'google_earth_images' in folders:
        folders.remove('google_earth_images')
        folders.insert(0, 'google_earth_images')
    
    # Get all image names from the first folder
    first_folder = folders[0]
    image_names = [f for f in os.listdir(os.path.join(base_folder, first_folder)) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    image_names.sort()
    
    # Parse folder names for detailed descriptions
    def parse_folder_name(folder_name):
        if folder_name == 'google_earth_images':
            return 'Google Earth'
        elif folder_name.startswith('cd'):
            try:
                cd_pos = folder_name.find('cd') + 2
                cf_pos = folder_name.find('cf')
                pdk_pos = folder_name.find('pdk')
                pmp_pos = folder_name.find('pmp')
                eps_pos = folder_name.find('eps')
                
                ceil_density = folder_name[cd_pos:cf_pos]
                complexity_factor = folder_name[cf_pos+2:pdk_pos]
                plane_detect_k = folder_name[pdk_pos+3:pmp_pos]
                plane_min_points = folder_name[pmp_pos+3:eps_pos]
                epsilon = folder_name[eps_pos+3:]
                
                cf_float = float(complexity_factor) / 10
                eps_float = float(epsilon) / 10
                
                return f"Ceil Density: {ceil_density}<br>Complexity Factor: {cf_float}<br>Plane Detect K: {plane_detect_k}<br>Plane Min Points: {plane_min_points}<br>Epsilon: {eps_float}"
            except (ValueError, IndexError):
                return folder_name
        else:
            return folder_name
    
    # Convert images to base64 (both small and large versions)
    def image_to_base64(image_path, max_size=(800, 800)):
        try:
            img = Image.open(image_path)
            
            # Special handling for Google Earth images - make them square
            if 'google_earth_images' in image_path:
                img_width, img_height = img.size
                min_dim = min(img_width, img_height)
                left = (img_width - min_dim) // 2
                top = (img_height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                img = img.crop((left, top, right, bottom))
            
            # Resize for display
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            return None
    
    def image_to_base64_tooltip(image_path, max_size=(1200, 1200)):
        try:
            img = Image.open(image_path)
            
            # Special handling for Google Earth images - make them square
            if 'google_earth_images' in image_path:
                img_width, img_height = img.size
                min_dim = min(img_width, img_height)
                left = (img_width - min_dim) // 2
                top = (img_height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                img = img.crop((left, top, right, bottom))
            
            # Resize for tooltip (larger)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            return None
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Image Comparison Table</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            
            .table-container {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                max-width: 100%;
                overflow-x: auto;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: {len(folders) * 200 + 300}px;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }}
            
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
                position: sticky;
                top: 0;
                z-index: 10;
            }}
            
            .row-number-col {{
                width: 50px;
                background-color: #f8f9fa;
                text-align: center;
                font-weight: bold;
            }}
            
            .image-name-col {{
                width: 300px;
                background-color: #f8f9fa;
            }}
            
            .image-cell {{
                text-align: center;
                position: relative;
                width: 400px;
                height: 300px;
            }}
            
            .image-cell img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
                cursor: pointer;
                transition: transform 0.2s ease;
            }}
            
            .image-cell img:hover {{
                transform: scale(3);
                z-index: 1000;
                position: relative;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
                border-radius: 8px;
            }}
            
            .image-cell img.selected {{
                border: 4px solid #dc3545 !important;
                border-radius: 8px;
                box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.3);
            }}
            
            .image-cell img.selected:hover {{
                border: 4px solid #dc3545 !important;
                transform: scale(3);
                z-index: 1000;
                position: relative;
                box-shadow: 0 8px 24px rgba(220, 53, 69, 0.5);
                border-radius: 8px;
            }}
            
            
            .manual-change {{
                background-color: #fff3cd !important;
            }}
            
            .excel-data {{
                font-size: 12px;
                color: #666;
                margin-top: 5px;
            }}
            
            .excel-data div {{
                margin-bottom: 2px;
            }}
            
            .folder-header {{
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
            }}
            
            .image-name-header {{
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                padding: 10px;
            }}
            
            .column-number-header {{
                font-size: 12px;
                font-weight: bold;
                text-align: center;
                padding: 5px;
                background-color: #e9ecef;
                color: #495057;
            }}
        </style>
    </head>
    <body>
        <h1>Interactive Image Comparison Table</h1>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th class="image-name-header">Image Name</th>
    """
    
    # Add column numbers row
    for col_number in range(1, len(folders) + 1):
        html_content += f'                        <th class="column-number-header">{col_number}</th>\n'
    
    html_content += """                    </tr>
                    <tr>
                        <th class="image-name-header">Image Name</th>
    """
    
    # Add folder headers
    for folder_name in folders:
        display_name = parse_folder_name(folder_name)
        html_content += f'                        <th class="folder-header">{display_name}</th>\n'
    
    html_content += """                    </tr>
                </thead>
                <tbody>
    """
    
    # Add rows
    for image_name in image_names:
        image_name_text = image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        
        # Check if this row needs manual change background
        manual_change_class = ""
        if image_name_text in excel_data:
            manual_change_value = excel_data[image_name_text]['manual_change']
            if manual_change_value == 1.0:
                manual_change_class = "manual-change"
        
        html_content += f'                    <tr class="{manual_change_class}">\n'
        
        # Image name column
        html_content += f'                        <td class="image-name-col">\n'
        html_content += f'                            <strong>{image_name_text}</strong>\n'
        
        # Add Excel data if available
        if image_name_text in excel_data:
            data = excel_data[image_name_text]
            html_content += '                            <div class="excel-data">\n'
            if data['address']:
                html_content += f'                                <div><strong>Addr:</strong> {data["address"]}</div>\n'
            if data['coordinates']:
                html_content += f'                                <div><strong>Coord:</strong> {data["coordinates"]}</div>\n'
            if data['typology']:
                html_content += f'                                <div><strong>Type:</strong> {data["typology"]}</div>\n'
            if data['description']:
                html_content += f'                                <div><strong>Desc:</strong> {data["description"]}</div>\n'
            html_content += '                            </div>\n'
        
        html_content += '                        </td>\n'
        
        # Image columns
        for folder_name in folders:
            folder_path = os.path.join(base_folder, folder_name)
            image_path = os.path.join(folder_path, image_name)
            
            html_content += '                        <td class="image-cell">\n'
            
            if os.path.exists(image_path):
                # Convert small image to base64
                img_small = image_to_base64(image_path, (800, 800))
                
                if img_small:
                    # Create unique ID for each image
                    image_id = f"img_{folder_name}_{image_name.replace('.', '_')}"
                    html_content += f'''                            <img id="{image_id}" 
                                 src="{img_small}" 
                                 style="max-width: 400px; max-height: 300px; object-fit: contain;"
                                 alt="{image_name}"
                                 onclick="toggleSelection('{image_id}')">\n'''
                else:
                    html_content += f'                            <div>Error loading image</div>\n'
            else:
                html_content += '                            <div>Missing</div>\n'
            
            html_content += '                        </td>\n'
        
        html_content += '                    </tr>\n'
    
    html_content += """                </tbody>
            </table>
        </div>
        
        <script>
            // Function to toggle image selection
            function toggleSelection(imageId) {
                const img = document.getElementById(imageId);
                const isSelected = img.classList.contains('selected');
                
                if (isSelected) {
                    // Remove selection
                    img.classList.remove('selected');
                    localStorage.removeItem(imageId);
                } else {
                    // Add selection
                    img.classList.add('selected');
                    localStorage.setItem(imageId, 'selected');
                }
            }
            
            // Function to restore selections from localStorage
            function restoreSelections() {
                const images = document.querySelectorAll('img[id^="img_"]');
                images.forEach(img => {
                    const imageId = img.id;
                    if (localStorage.getItem(imageId) === 'selected') {
                        img.classList.add('selected');
                    }
                });
            }
            
            // Restore selections when page loads
            document.addEventListener('DOMContentLoaded', restoreSelections);
            
            // Optional: Add keyboard shortcut to clear all selections (Ctrl+Shift+C)
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                    const selectedImages = document.querySelectorAll('img.selected');
                    selectedImages.forEach(img => {
                        img.classList.remove('selected');
                        localStorage.removeItem(img.id);
                    });
                    console.log('All selections cleared');
                }
            });
        </script>
        
    </body>
    </html>
    """
    
    # Write HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Interactive HTML table created: {output_html}")
    print(f"Found {len(folders)} folders and {len(image_names)} images")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in the images_test_tiles directory or need to navigate to it
    if os.path.basename(script_dir) == "images_test_tiles":
        base_folder = script_dir
        # Output to parent directory (project root)
        output_html = os.path.join(os.path.dirname(script_dir), "interactive_image_table.html")
    else:
        # Try to find images_test_tiles folder relative to script location
        images_test_tiles_path = os.path.join(script_dir, "images_test_tiles")
        if os.path.exists(images_test_tiles_path):
            base_folder = images_test_tiles_path
            # Output to project root (script_dir)
            output_html = os.path.join(script_dir, "interactive_image_table.html")
        else:
            print("Error: Cannot find images_test_tiles directory")
            print("Script location:", script_dir)
            print("Expected to find 'images_test_tiles' folder here or in parent directory")
            exit(1)
    
    # Verify google_earth_images exists
    google_earth_path = os.path.join(base_folder, "google_earth_images")
    if not os.path.exists(google_earth_path):
        print("Error: Cannot find 'google_earth_images' folder")
        print("Base folder:", base_folder)
        print("Expected to find 'google_earth_images' folder here")
        exit(1)
    
    print(f"Running from: {os.getcwd()}")
    print(f"Script location: {script_dir}")
    print(f"Base folder: {base_folder}")
    print(f"Output file: {output_html}")
    
    create_interactive_image_table(base_folder, output_html)
