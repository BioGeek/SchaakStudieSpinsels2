import pymupdf
import re
from pathlib import Path
import os
import cv2
import numpy as np
import cv2
import numpy as np
from operator import itemgetter

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
    seen = set()
    for i, page in enumerate(doc):
        # A study starts with a header like '- 1 -' typically at the top of a column.
        # We check the top half of the page to be more specific.
        page_top_half = page.get_text("text", clip=pymupdf.Rect(0, 0, page.rect.width, page.rect.height / 2))
        match = study_regex.search(page_top_half)
        if match:
            if int(match.group(1)) not in seen:
                study_locations.append({'number': int(match.group(1)), 'start_page': i})
                seen.add(int(match.group(1)))

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
        # Find instances that are likely page numbers (in bottom 20% of page)
        # and relatively isolated (not surrounded by much other text)
        bottom_threshold = height * 0.8
        
        for rect in page_num_instances:
            # Check if it's in the bottom portion
            if rect.y0 > bottom_threshold:
                # Check if this is an isolated number (page number)
                # by examining text around it
                search_area = pymupdf.Rect(
                    rect.x0 - 20, rect.y0 - 10,
                    rect.x1 + 20, rect.y1 + 10
                )
                nearby_text = page.get_text("text", clip=search_area).strip()
                
                # If the nearby text is just the number (or number with minimal whitespace),
                # it's likely a page number
                if nearby_text.replace('\n', '').replace(' ', '') == printed_page_num:
                    return rect.y0 - 5
    
    # Default: exclude bottom 40 points
    return height - 40

def extract_piece_templates(template_image_path, debug_dir=None):
    """
    Extracts individual chess piece templates from the template image.
    Saves debug images of contours and individual templates if debug_dir is provided.
    """
    templates = {}
    template_image = cv2.imread(template_image_path)
    if template_image is None:
        raise FileNotFoundError(f"Template image not found at {template_image_path}")

    gray_template = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_template, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    piece_names = ["K", "Q", "R", "B", "N", "P"]
    if len(contours) < len(piece_names):
        print("Warning: Fewer contours found than the expected number of piece types.")
        return {}

    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
    
    # --- Debug Logging ---
    if debug_dir:
        # Ensure debug directory exists
        os.makedirs(debug_dir, exist_ok=True)
        
        # Draw contours on the original template image for visualization
        debug_template_image = template_image.copy()
        cv2.drawContours(debug_template_image, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(debug_dir, "1_template_contours.png"), debug_template_image)
    # --- End Debug ---

    for i, contour in enumerate(contours):
        if i < len(piece_names):
            x, y, w, h = cv2.boundingRect(contour)
            piece_template = gray_template[y:y+h, x:x+w]
            templates[piece_names[i]] = piece_template

            # --- Debug Logging ---
            if debug_dir:
                # Ensure debug directory exists
                os.makedirs(debug_dir, exist_ok=True)
                
                # Save each extracted template image
                template_filename = os.path.join(debug_dir, f"2_template_{piece_names[i]}.png")
                cv2.imwrite(template_filename, piece_template)
            # --- End Debug ---
            
    return templates


def detect_chessboard_and_squares(image_path, debug_dir=None):
    """
    Detects the chessboard and extracts its 64 squares.
    Saves a debug image of the board with a grid if debug_dir is provided.
    """
    board_image = cv2.imread(image_path)
    if board_image is None:
        raise FileNotFoundError(f"Board image not found at {image_path}")

    gray_board = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)
    height, width = gray_board.shape
    square_size = width // 8
    
    squares = []
    for i in range(8):
        for j in range(8):
            square = gray_board[i*square_size:(i+1)*square_size, j*square_size:(j+1)*square_size]
            squares.append(((i, j), square))

    # --- Debug Logging ---
    if debug_dir:
        # Ensure debug directory exists
        os.makedirs(debug_dir, exist_ok=True)
        
        debug_board_image = board_image.copy()
        for i in range(1, 8):
            # Draw vertical lines
            cv2.line(debug_board_image, (i * square_size, 0), (i * square_size, height), (0, 255, 0), 2)
            # Draw horizontal lines
            cv2.line(debug_board_image, (0, i * square_size), (width, i * square_size), (0, 255, 0), 2)
        board_image_filename = os.path.basename(image_path)
        board_image_name, _ = os.path.splitext(board_image_filename)
        debug_filename = f"3_board_grid_{board_image_name}.png"
        abs_debug_path = os.path.abspath(os.path.join(debug_dir, debug_filename))
        cv2.imwrite(abs_debug_path, debug_board_image)
        print(f"Debug board grid image saved at {abs_debug_path}")
    # --- End Debug ---
            
    return board_image, squares


def identify_pieces(original_board_image, squares, templates, debug_dir=None):
    """
    Identifies pieces on the board by color and shape.
    Saves a detailed debug image annotating each square if debug_dir is provided.
    """
    board_representation = [['1' for _ in range(8)] for _ in range(8)]
    debug_annotated_board = original_board_image.copy() if debug_dir else None

    BLACK_PIECE_THRESHOLD = 100
    WHITE_PIECE_THRESHOLD = 180
    LIGHT_SQUARE_INTENSITY = 191
    DARK_SQUARE_INTENSITY = 168

    for (row, col), square in squares:
        avg_intensity = np.mean(square)
        piece_color = None

        if avg_intensity < BLACK_PIECE_THRESHOLD:
            piece_color = 'b'
        elif avg_intensity > WHITE_PIECE_THRESHOLD:
            piece_color = 'w'

        # Determine square color based on intensity
        square_color = "Light" if avg_intensity > (LIGHT_SQUARE_INTENSITY + DARK_SQUARE_INTENSITY) / 2 else "Dark"
        piece_info_for_debug = f"I:{int(avg_intensity)} {square_color}"
        
        if piece_color:
            best_match_shape = (None, -1)
            
            for name, template in templates.items():
                if template.shape[0] > square.shape[0] or template.shape[1] > square.shape[1]:
                    template = cv2.resize(template, (square.shape[1]-10, square.shape[0]-10))

                res = cv2.matchTemplate(square, template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)

                if max_val > best_match_shape[1]:
                    best_match_shape = (name, max_val)
            
            confidence_threshold = 0.7
            if best_match_shape[1] > confidence_threshold:
                piece_char = best_match_shape[0]
                board_representation[row][col] = piece_color + piece_char
                piece_info_for_debug += f" {piece_color}{piece_char}({best_match_shape[1]:.2f})"
            else:
                piece_info_for_debug += f" NoMatch({best_match_shape[1]:.2f})"

        # --- Debug Logging ---
        if debug_dir:
            square_size = square.shape[0]
            # Position text to avoid overlap - use smaller font and better positioning
            text_pos = (col * square_size + 2, row * square_size + 12)
            cv2.putText(debug_annotated_board, piece_info_for_debug, text_pos, 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        # --- End Debug ---

    # --- Debug Logging ---
    if debug_dir:
        # Ensure debug directory exists
        os.makedirs(debug_dir, exist_ok=True)
        
        cv2.imwrite(os.path.join(debug_dir, "4_final_detection_annotated.png"), debug_annotated_board)
    # --- End Debug ---
            
    return board_representation

def board_to_fen(board_representation):
    """
    Converts the internal 2D board representation to a FEN string.
    """
    fen = ""
    for row in board_representation:
        empty_squares = 0
        for square in row:
            if square == '1':
                empty_squares += 1
            else:
                if empty_squares > 0:
                    fen += str(empty_squares)
                    empty_squares = 0
                
                piece_color, piece_type = square[0], square[1]
                fen += piece_type.upper() if piece_color == 'w' else piece_type.lower()
        
        if empty_squares > 0:
            fen += str(empty_squares)
        
        fen += "/"
        
    return fen.rstrip('/') + " w KQkq - 0 1"

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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply binary threshold to enhance checkerboard pattern
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Look for square-ish contours that could be the checkerboard
        candidates = []
        
        for contour in contours:
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filter for reasonably sized, square-ish regions
            if area < 30000:  # Too small (scaled by 2x, so min ~15000 original)
                continue
            if area > 500000:  # Too large
                continue
                
            aspect_ratio = w / h if h > 0 else 0
            
            # Should be roughly square
            if 0.85 <= aspect_ratio <= 1.35:

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

def extract_and_save_content(doc, structure, base_dir, piece_templates):
    """
    Iterates through the structured data, extracts diagrams and columns for each
    endgame study, and saves them to the appropriate folders.

    Args:
        doc (pymupdf.Document): The opened PDF document.
        structure (dict): The dictionary containing the book structure.
        base_dir (str): The root directory for the output.
        piece_templates (dict): A dictionary of piece templates.
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

            # --- Diagram Extraction ---
            start_page = doc.load_page(start_page_num)
            diagram_rect = extract_diagram(start_page, study['number'])
            
            if diagram_rect:
                # Render the diagram region to a high-resolution image
                mat = start_page.get_pixmap(matrix=pymupdf.Matrix(3, 3), clip=diagram_rect)
                img_data = mat.tobytes("png")
                
                # Load into numpy array for processing
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Convert to grayscale for contour detection
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Threshold to find the checkerboard
                _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                
                # Find contours
                contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Find the largest contour (the checkerboard)
                    largest_contour = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    # Crop to the tight bounding box
                    cropped = img[y:y+h, x:x+w]
                    
                    # Save as PNG image
                    diagram_path = study_dir / f"endgame{study['number']:03d}_diagram.png"
                    cv2.imwrite(str(diagram_path), cropped)
                    print(f"  Saved diagram to {diagram_path.name}")

                    # Extract FEN from the diagram
                    board_image_gray, board_squares = detect_chessboard_and_squares(diagram_path, debug_dir='data/debug')

                    # Step 3: Identify pieces on the board
                    board_state = identify_pieces(board_image_gray, board_squares, piece_templates, debug_dir='data/debug')

                    # Step 4: Convert the board state to FEN
                    fen_notation = board_to_fen(board_state)

                    if fen_notation:
                        fen_path = study_dir / "fen.txt"
                        with open(fen_path, 'w') as f:
                            f.write(fen_notation)
                        print(f"  Saved FEN to fen.txt")


                else:
                    raise ValueError(f"  Study {study['number']}: Could not locate diagram")

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

                for col_idx, rect in enumerate(col_rects):
                    # Skip the left column if this is the start page and study begins in right column
                    # Detect this by checking if the study header appears in the right column
                    if page_num == start_page_num and col_idx == 0:
                        # Check if study header is in the right column
                        right_col_rect = pymupdf.Rect(mid_point, 0, width, content_height)
                        right_col_text = page.get_text("text", clip=right_col_rect)
                        study_header_pattern = f"- {study['number']} -"
                        
                        if study_header_pattern in right_col_text:
                            # Study starts in right column, skip left column
                            print(f"  Study {study['number']}: Starts in right column, skipping left column")
                            continue
                    
                    new_doc = pymupdf.open()
                    new_page = new_doc.new_page(width=rect.width, height=rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num, clip=rect)
                    
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

    piece_templates = extract_piece_templates("data/template.png")
    if not piece_templates:
        raise ValueError("Could not extract piece templates. Exiting.")
    
    print("\nExtracting diagrams and columns for each study...")
    extract_and_save_content(doc, structure, base_output_dir, piece_templates)
    
    doc.close()
    print(f"\n{'='*60}")
    print(f"Processing complete! Files saved in '{base_output_dir}'")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()