import os
from pathlib import Path
from typing import List

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 is required. Install with: pip install PyPDF2")
    raise SystemExit(1)


def get_pdf_files(directory: str) -> List[Path]:
    path = Path(directory)
    return sorted([f for f in path.iterdir() if f.suffix.lower() == ".pdf"])


def merge_pdfs(input_files: List[Path], output_file: str):
    writer = PdfWriter()
    total_pages = 0
    for pdf_path in input_files:
        try:
            reader = PdfReader(str(pdf_path))
            page_count = len(reader.pages)
            for page_num in range(page_count):
                writer.add_page(reader.pages[page_num])
            print(f"Added: {pdf_path.name} ({page_count} pages)")
            total_pages += page_count
        except Exception as e:
            print(f"Skipping {pdf_path.name}: {e}")
    with open(output_file, "wb") as f:
        writer.write(f)
    print(f"\nSuccess! Merged {len(input_files)} PDFs into: {output_file}")
    print(f"Total pages: {total_pages}")


def merge_all_in_directory(directory: str, output_name: str = "merged_output.pdf"):
    pdf_files = get_pdf_files(directory)
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        print("Add PDF files to the current directory and try again.")
        return
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    confirm = input(f"\nMerge into '{output_name}'? (Y/n): ").strip().lower()
    if confirm == "n":
        print("Cancelled.")
        return
    merge_pdfs(pdf_files, output_name)


def main():
    print("=" * 50)
    print("  PDF MERGER")
    print("=" * 50)
    target = input("Directory with PDF files (default: current): ").strip()
    if not target:
        target = "."
    output = input("Output filename (default: merged_output.pdf): ").strip()
    if not output:
        output = "merged_output.pdf"
    if not output.endswith(".pdf"):
        output += ".pdf"
    merge_all_in_directory(target, output)


if __name__ == "__main__":
    main()
