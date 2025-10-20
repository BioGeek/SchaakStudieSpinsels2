import pymupdf
import re
from pathlib import Path
import os
import cv2
import numpy as np
from PIL import Image
import io


def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename by making it lowercase,
    removing special characters, and replacing spaces/hyphens with underscores.
    """
    name = name.lower()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s-]+', '_', name).strip('_')
    return name

def create_directory_structure(pdf_path, chapters_of_interest):
    """
    Parses the PDF to identify the structure of chapters and endgame studies.
    It returns the opened PDF document and a dictionary detailing the structure.

    Args:
        pdf_path (str): The path to the input PDF file.
        chapters_of_interest (list): A list of chapter names to process.

    Returns:
        tuple: A tuple containing the pymupdf.Document object and a structure dictionary.
    """
    doc = pymupdf.open(pdf_path)
    
    # Use the Table of Contents with chapter numbering
    toc = {
        "Manke Maljutka's": (1, 35),
        "Maljutka's": (2, 67),
        "Mini - Studies": (3, 121),
        "Miniaturen": (4, 207),
        "Bijna - Miniaturen": (5, 295),
        "Studies": (6, 355)
    }
    
    structure = {}
    chapter_locations = {}
    
    for chap, (num, page) in toc.items():
        if chap in chapters_of_interest:
            sanitized = sanitize_filename(chap)
            numbered_name = f"{num}_{sanitized}"
            structure[numbered_name] = []
            chapter_locations[numbered_name] = page - 1

    # Find all pages where a new study begins
    study_regex = re.compile(r"-\s*(\d+)\s*-")
    study_locations = []
    for i, page in enumerate(doc):
        # A study starts with a header like '- 1 -' typically at the top of a column.
        # We check the top half of the page to be more specific.
        page_top_half = page.get_text("text", clip=pymupdf.Rect(0, 0, page.rect.width, page.rect.height / 2))
        match = study_regex.search(page_top_half)
        if match:
            study_locations.append({'number': int(match.group(1)), 'start_page': i})

    # Create a sorted list of all break points (start of a new chapter or the end of the document)
    break_points = sorted(list(chapter_locations.values()) + [len(doc)])

    # Assign each study to its corresponding chapter
    sorted_chapters = sorted(chapter_locations.items(), key=lambda item: item[1])

    for study in study_locations:
        current_chapter = None
        for chap_name, chap_page_start in sorted_chapters:
            if study['start_page'] >= chap_page_start:
                current_chapter = chap_name
        
        if current_chapter:
            structure[current_chapter].append(study)

    # Determine the end page for each study
    all_study_starts = {s['start_page'] for s in study_locations}
    for i, bp in enumerate(break_points):
      for chapter in structure.values():
        for study in chapter:
          if study['start_page'] >= bp and (i + 1) < len(break_points) and study['start_page'] < break_points[i+1]:
            # The study ends right before the next study starts
            next_break = len(doc)
            for next_start in sorted(list(all_study_starts)):
                if next_start > study['start_page']:
                    next_break = next_start
                    break
            study['end_page'] = next_break - 1

    return doc, structure

def find_page_number_region(page, page_num):
    """
    Finds the region containing the page number at bottom of page.
    Returns a rectangle to exclude from extraction.
    
    Args:
        page: PyMuPDF page object
        page_num: The actual page number (0-based index)
        
    Returns:
        float: The y-coordinate above which content should be kept
    """
    height = page.rect.height
    width = page.rect.width
    
    # The actual page number printed on the page (1-based)
    printed_page_num = str(page_num + 1)
    
    # Search for the page number on the page
    page_num_instances = page.search_for(printed_page_num)
    
    if page_num_instances:
        # Find the lowest occurrence (closest to bottom)
        lowest_y = 0
        for rect in page_num_instances:
            if rect.y0 > lowest_y:
                lowest_y = rect.y0
        
        # Exclude everything from slightly above the page number
        if lowest_y > height - 100:  # Only if it's in the bottom portion
            return lowest_y - 5
    
    # Default: exclude bottom 40 points
    return height - 40

def extract_diagram(page, study_number):
    """
    Extracts the chess diagram from a page using OpenCV to detect the checkerboard pattern.
    
    Args:
        page: PyMuPDF page object
        study_number: The study number for debugging
        
    Returns:
        pymupdf.Rect or None: The rectangle containing the diagram
    """
    try:
        # Render the page to an image at high resolution
        mat = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # 2x resolution for better detection
        img_data = mat.tobytes("png")
        
        # Convert to OpenCV format
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Save the rendered image to a subfolder for debugging
        import os
        subfolder = "diagram_images"
        os.makedirs(subfolder, exist_ok=True)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # filename = os.path.join(subfolder, f"study_{study_number}_page_{page.number + 1}_gray.png")
        # cv2.imwrite(filename, gray)
        
        # Apply binary threshold to enhance checkerboard pattern
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for square-ish contours that could be the checkerboard
        candidates = []
        
        for i, contour in enumerate(contours):
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            # Draw rectangle on the grayscale image and save it for debugging
            debug_img = gray.copy()
            RED = (0, 0, 255)
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), RED, 3)
            debug_filename = os.path.join(subfolder, f"study_{study_number}_page_{page.number + 1}_{i}rect.png")
            cv2.imwrite(debug_filename, debug_img)

            area = w * h
            
            # Filter for reasonably sized, square-ish regions
            if area < 30000:  # Too small (scaled by 2x, so min ~15000 original)
                continue
            if area > 500000:  # Too large
                continue
                
            aspect_ratio = w / h if h > 0 else 0
            
            # Should be roughly square
            if 0.85 <= aspect_ratio <= 1.15:

                candidates.append({'rect': (x, y, w, h), 'area': area, 'aspect': aspect_ratio})
        
        # Sort by area (largest first) and pick the best candidate
        candidates.sort(key=lambda c: c['area'], reverse=True)
        
        if candidates:
            best = candidates[0]
            x, y, w, h = best['rect']
            
            # Convert back to PDF coordinates (accounting for 2x scale)
            scale = 2.0
            pdf_rect = pymupdf.Rect(
                x / scale,
                y / scale,
                (x + w) / scale,
                (y + h) / scale
            )
            
            print(f"  Study {study_number}: Found diagram via OpenCV at {pdf_rect})")
            return pdf_rect
            
    except Exception as e:
        print(f"  Study {study_number}: OpenCV detection failed: {e}")
    
    # Fallback: Try the GBR code method
    gbr_code_regex = re.compile(r"(\+|=)\s+(\d{4}\.\d{2}\s+\w{4})")
    page_text = page.get_text("text")
    gbr_match = gbr_code_regex.search(page_text)
    
    if gbr_match:
        gbr_text = gbr_match.group(0)
        text_instances = page.search_for(gbr_text)
        
        if text_instances:
            gbr_rect = text_instances[0]
            
            # Find the study header "- N -" to determine top of diagram
            study_header_regex = re.compile(r"-\s*" + str(study_number) + r"\s*-")
            header_instances = page.search_for(study_header_regex.pattern)
            
            if header_instances:
                header_rect = None
                for h_rect in header_instances:
                    if abs(h_rect.x0 - gbr_rect.x0) < 50:
                        header_rect = h_rect
                        break
                
                if header_rect:
                    x0 = gbr_rect.x0
                    y0 = header_rect.y1 + 8
                    y1 = gbr_rect.y0 - 8
                    x1 = x0 + (y1 - y0)
                    
                    diagram_rect = pymupdf.Rect(x0, y0, x1, y1)
                    print(f"  Study {study_number}: Found diagram via GBR fallback at {diagram_rect}")
                    return diagram_rect
    
    raise ValueError(f"  Study {study_number}: Could not locate diagram")

def extract_and_save_content(doc, structure, base_dir):
    """
    Iterates through the structured data, extracts diagrams and columns for each
    endgame study, and saves them to the appropriate folders.

    Args:
        doc (pymupdf.Document): The opened PDF document.
        structure (dict): The dictionary containing the book structure.
        base_dir (str): The root directory for the output.
    """
    for chapter_name, studies in structure.items():
        chapter_dir = Path(base_dir) / chapter_name
        chapter_dir.mkdir(parents=True, exist_ok=True)

        for study in studies:
            study_dir = chapter_dir / f"endgame{study['number']:03d}"
            study_dir.mkdir(exist_ok=True)
            
            start_page_num = study['start_page']
            end_page_num = study.get('end_page', start_page_num)

            print(f"\nProcessing study {study['number']} (pages {start_page_num}-{end_page_num})")


            # --- Column Extraction (temporary) ---
            temp_columns = []
            col_counter = 1
            
            for page_num in range(start_page_num, end_page_num + 1):
                page = doc.load_page(page_num)
                width = page.rect.width
                mid_point = width / 2
                    
                # Find where page number region starts
                content_height = find_page_number_region(page, page_num)

                # Define rectangles for left and right columns (excluding page numbers)
                col_rects = [
                    pymupdf.Rect(0, 0, mid_point, content_height),
                    pymupdf.Rect(mid_point, 0, width, content_height)
                ]

                for rect in col_rects:
                    new_doc = pymupdf.open()
                    new_page = new_doc.new_page(width=rect.width, height=rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num, clip=rect)

                    if col_counter == 1:
                        # --- Diagram Extraction ---
                        diagram_rect = extract_diagram(new_page, study['number'])
                        
                        if diagram_rect:
                            diagram_doc = pymupdf.open()
                            diagram_page = diagram_doc.new_page(width=diagram_rect.width, height=diagram_rect.height)
                            diagram_page.show_pdf_page(diagram_page.rect, doc, start_page_num, clip=diagram_rect)
                            
                            diagram_path = study_dir / f"endgame{study['number']:03d}_diagram.pdf"
                            diagram_doc.save(str(diagram_path))
                            diagram_doc.close()
                            print(f"  Saved diagram to {diagram_path.name}")

                    col_path = study_dir / f"temp_col{col_counter:02d}.pdf"
                    new_doc.save(str(col_path))
                    new_doc.close()
                    temp_columns.append(col_path)

                    col_counter += 1

            # --- Combine all columns into a single PDF ---
            if temp_columns:
                combined_doc = pymupdf.open()
                
                for col_path in temp_columns:
                    col_doc = pymupdf.open(col_path)
                    combined_doc.insert_pdf(col_doc)
                    col_doc.close()
                
                # Save combined PDF
                combined_path = study_dir / f"endgame{study['number']:03d}_text.pdf"
                combined_doc.save(str(combined_path))
                combined_doc.close()
                print(f"  Saved combined text to {combined_path.name}")
                
                # Delete temporary column PDFs
                for col_path in temp_columns:
                    col_path.unlink()

def main():
    """
    Main function to orchestrate the PDF processing.
    """
    pdf_path = "data/schaakstudiespinsels2.pdf"
    base_output_dir = "data/endgames"
    chapters_to_process = [
        "Manke Maljutka's",
        "Maljutka's",
        "Mini - Studies",
        "Miniaturen",
        "Bijna - Miniaturen",
        "Studies"
    ]

    if not Path(pdf_path).exists():
        print(f"Error: The file '{os.path.abspath(pdf_path)}' was not found.")
        return

    print("Parsing PDF and creating directory structure...")
    doc, structure = create_directory_structure(pdf_path, chapters_to_process)
    
    print("\nExtracting diagrams and columns for each study...")
    extract_and_save_content(doc, structure, base_output_dir)
    
    doc.close()
    print(f"\n{'='*60}")
    print(f"Processing complete! Files saved in '{base_output_dir}'")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()