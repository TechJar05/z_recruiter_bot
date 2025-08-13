import fitz  # PyMuPDF

def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)
   






import fitz  # PyMuPDF
import io
import base64
from PIL import Image
from uuid import uuid4

def extract_images_from_pdf(pdf_file):
    images = []

    pdf_file.seek(0)  # Reset file pointer
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            img_list = page.get_images(full=True)

            # ✅ Try extracting directly embedded images
            for img_index, img in enumerate(img_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image = Image.open(io.BytesIO(image_bytes))

                # ✅ Filter non-profile images
                width, height = image.size
                aspect_ratio = width / height

                # Example filters: dimensions and aspect ratio
                if width < 100 or height < 100:
                    continue  # Too small to be a profile photo
                if aspect_ratio < 0.5 or aspect_ratio > 1.5:
                    continue  # Too wide/tall — likely not a profile photo

                # ✅ Passed filters, return this image
                filename = f"profile_image_{uuid4().hex}.{image_ext}"
                buffered = io.BytesIO()
                image.save(buffered, format=image_ext.upper())
                encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")

                return {
                    "filename": filename,
                    "image_base64": f"data:image/{image_ext};base64,{encoded_img}",
                    "width": width,
                    "height": height,
                    "page": page_index + 1
                }

           

    return None  # No suitable profile image found
