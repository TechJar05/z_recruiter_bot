import fitz  # PyMuPDF

def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc)




import fitz  # PyMuPDF
from PIL import Image
import io
import os
import base64
from uuid import uuid4


def extract_images_from_pdf(pdf_file):
    images = []
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page_index in range(len(doc)):
            for img_index, img in enumerate(doc.get_page_images(page_index)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                image = Image.open(io.BytesIO(image_bytes))
                filename = f"profile_image_{uuid4().hex}.{image_ext}"

                # Save or return base64 image
                buffered = io.BytesIO()
                image.save(buffered, format=image_ext.upper())
                encoded_img = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                images.append({
                    "filename": filename,
                    "image_base64": f"data:image/{image_ext};base64,{encoded_img}",
                    "width": image.width,
                    "height": image.height,
                    "page": page_index + 1
                })

                # 🚀 Usually profile photo is first image → break
                if page_index == 0:
                    return images[0]  # Only return first image (likely profile)

    return None
