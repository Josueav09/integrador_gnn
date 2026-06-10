import sys

pdf_path = r"c:\Users\JOSUE\Downloads\CICLO 9\Integrador_de_software\Entrenamiento_GNN\APF2_INDICACIONES Y RÚBRICA_S12F.pdf"

try:
    import pypdf
    print("Using pypdf...")
    reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    print("SUCCESS")
    with open("pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    sys.exit(0)
except ImportError:
    pass

try:
    import pdfplumber
    print("Using pdfplumber...")
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    print("SUCCESS")
    with open("pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    sys.exit(0)
except ImportError:
    pass

try:
    import fitz # PyMuPDF
    print("Using fitz...")
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    print("SUCCESS")
    with open("pdf_content.txt", "w", encoding="utf-8") as f:
        f.write(text)
    sys.exit(0)
except ImportError:
    pass

print("No PDF extraction libraries found.")
sys.exit(1)
