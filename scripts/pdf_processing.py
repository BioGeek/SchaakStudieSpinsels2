import pymupdf
import re
from pathlib import Path
import os


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
    structure = {sanitize_filename(chap): [] for chap in chapters_of_interest}

    # Use the Table of Contents on page 453 to locate chapter start pages (1-based index).
    # Page numbers are converted to 0-based index for PyMuPDF.
    toc = {
        "Manke Maljutka’s": 35,
        "Maljutka’s": 67,
        "Mini - Studies": 121,
        "Miniaturen": 207,
        "Bijna - Miniaturen": 295,
        "Studies": 355
    }
    chapter_locations = {
        sanitize_filename(chap): page - 1
        for chap, page in toc.items() if chap in chapters_of_interest
    }

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

def extract_and_save_content(doc, structure, base_dir):
    """
    Iterates through the structured data, extracts diagrams and columns for each
    endgame study, and saves them to the appropriate folders.

    Args:
        doc (pymupdf.Document): The opened PDF document.
        structure (dict): The dictionary containing the book structure.
        base_dir (str): The root directory for the output.
    """
    gbr_code_regex = re.compile(r"(\+|=)\s+(\d{4}\.\d{2}\s+\w{4})")

    for chapter_name, studies in structure.items():
        chapter_dir = Path(base_dir) / chapter_name
        chapter_dir.mkdir(parents=True, exist_ok=True)

        for study in studies:
            study_dir = chapter_dir / f"endgame{study['number']:03d}"
            study_dir.mkdir(exist_ok=True)
            
            start_page_num = study['start_page']
            end_page_num = study.get('end_page', start_page_num)

            # --- Diagram Extraction ---
            start_page = doc.load_page(start_page_num)
            gbr_match = gbr_code_regex.search(start_page.get_text("text"))
            if gbr_match:
                gbr_text = gbr_match.group(0)
                text_instances = start_page.search_for(gbr_text)
                if text_instances:
                    gbr_rect = text_instances[0]
                    # Estimate diagram position: a square box above the GBR code.
                    diagram_size = 200  # A reasonable guess for the diagram size in points
                    x0 = gbr_rect.x0
                    y0 = gbr_rect.y0 - diagram_size - 10  # 10 points margin
                    x1 = x0 + diagram_size
                    y1 = gbr_rect.y0 - 10
                    diagram_rect = pymupdf.Rect(x0, y0, x1, y1)

                    new_doc = pymupdf.open()
                    new_page = new_doc.new_page(width=diagram_rect.width, height=diagram_rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, start_page_num, clip=diagram_rect)
                    
                    diagram_path = study_dir / f"endgame{study['number']:03d}_diagram.pdf"
                    new_doc.save(str(diagram_path))
                    new_doc.close()

            # --- Column Extraction ---
            col_counter = 1
            for page_num in range(start_page_num, end_page_num + 1):
                page = doc.load_page(page_num)
                width, height = page.rect.width, page.rect.height
                mid_point = width / 2

                # Define rectangles for left and right columns
                col_rects = [
                    pymupdf.Rect(0, 0, mid_point, height),
                    pymupdf.Rect(mid_point, 0, width, height)
                ]

                for rect in col_rects:
                    new_doc = pymupdf.open()
                    new_page = new_doc.new_page(width=rect.width, height=rect.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_num, clip=rect)
                    
                    col_path = study_dir / f"endgame{study['number']:03d}_col{col_counter:02d}.pdf"
                    new_doc.save(str(col_path))
                    new_doc.close()
                    col_counter += 1

def main():
    """
    Main function to orchestrate the PDF processing.
    """
    pdf_path = "data/schaakstudiespinsels2.pdf"
    base_output_dir = "data/endgames"
    chapters_to_process = [
        "Manke Maljutka’s",
        "Maljutka’s",
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
    
    print("Extracting diagrams and columns for each study...")
    extract_and_save_content(doc, structure, base_output_dir)
    
    doc.close()
    print(f"\nProcessing complete. Files have been saved in the '{base_output_dir}' directory.")

if __name__ == "__main__":
    main()