import os
import fitz
from PIL import Image
from io import BytesIO
import hashlib

BOOKS_FOLDER = "books"
IMAGES_FOLDER = "images"
EXTRACTED_FOLDER = "images/extracted"


def extract_images_from_pdf(pdf_path, min_size=100):
    images = []
    try:
        pdf = fitz.open(pdf_path)
        pdf_name = os.path.basename(pdf_path).replace(".pdf", "")
        pdf_folder = os.path.join(EXTRACTED_FOLDER, pdf_name)
        os.makedirs(pdf_folder, exist_ok=True)
        
        for page_num, page in enumerate(pdf, start=1):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    pil_img = Image.open(BytesIO(image_bytes))
                    
                    if pil_img.size[0] < min_size or pil_img.size[1] < min_size:
                        continue
                    
                    if pil_img.mode in ("RGBA", "P", "LA", "CMYK"):
                        pil_img = pil_img.convert("RGB")
                    
                    img_hash = hashlib.md5(image_bytes).hexdigest()[:8]
                    filename = f"page{page_num}_img{img_index}_{img_hash}.jpg"
                    save_path = os.path.join(pdf_folder, filename)
                    
                    if not os.path.exists(save_path):
                        pil_img.save(save_path, "JPEG", quality=90)
                    
                    images.append({
                        "path": save_path,
                        "page": page_num,
                        "size": pil_img.size,
                        "pdf": pdf_name,
                        "filename": filename
                    })
                except:
                    continue
        pdf.close()
        return images
    except Exception as e:
        print(f"[!] PDF extraction error: {e}")
        return []


def extract_all_books(progress_callback=None):
    os.makedirs(EXTRACTED_FOLDER, exist_ok=True)
    all_images = {}
    if not os.path.exists(BOOKS_FOLDER):
        return all_images
    pdfs = [f for f in os.listdir(BOOKS_FOLDER) if f.endswith(".pdf")]
    for i, pdf_file in enumerate(pdfs):
        pdf_path = os.path.join(BOOKS_FOLDER, pdf_file)
        pdf_name = pdf_file.replace(".pdf", "")
        if progress_callback:
            progress_callback(i + 1, len(pdfs), pdf_name)
        images = extract_images_from_pdf(pdf_path)
        if images:
            all_images[pdf_name] = images
    return all_images


def get_extracted_books():
    if not os.path.exists(EXTRACTED_FOLDER):
        return []
    return sorted([d for d in os.listdir(EXTRACTED_FOLDER)
                  if os.path.isdir(os.path.join(EXTRACTED_FOLDER, d))])


def get_book_images(book_name):
    book_folder = os.path.join(EXTRACTED_FOLDER, book_name)
    if not os.path.exists(book_folder):
        return []
    images = []
    for f in sorted(os.listdir(book_folder)):
        if f.endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(book_folder, f)
            page = 0
            if "page" in f:
                try:
                    page = int(f.split("page")[1].split("_")[0])
                except:
                    pass
            images.append({"path": path, "filename": f, "page": page, "book": book_name})
    images.sort(key=lambda x: x["page"])
    return images


def get_all_extracted_count():
    if not os.path.exists(EXTRACTED_FOLDER):
        return 0, 0
    total_books = 0
    total_images = 0
    for book_folder in os.listdir(EXTRACTED_FOLDER):
        book_path = os.path.join(EXTRACTED_FOLDER, book_folder)
        if os.path.isdir(book_path):
            total_books += 1
            total_images += len([f for f in os.listdir(book_path) if f.endswith((".jpg", ".png"))])
    return total_books, total_images


def copy_image_to_output(source_path, new_filename):
    import shutil
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    dest_path = os.path.join(IMAGES_FOLDER, new_filename)
    try:
        shutil.copy2(source_path, dest_path)
        return dest_path
    except:
        return None


def save_uploaded_pdf(uploaded_file, category="other"):
    """Save uploaded PDF to books folder with smart naming"""
    os.makedirs(BOOKS_FOLDER, exist_ok=True)
    
    filename = uploaded_file.name
    if not filename.startswith(f"ncert_{category}"):
        base_name = filename.replace(".pdf", "").lower().replace(" ", "_")
        filename = f"ncert_{category}_{base_name}.pdf"
    
    save_path = os.path.join(BOOKS_FOLDER, filename)
    
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return save_path


def delete_pdf(filename):
    """Delete a PDF from books folder"""
    path = os.path.join(BOOKS_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
