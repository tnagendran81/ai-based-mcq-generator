import fitz  # PyMuPDF
import os
from PIL import Image
import shutil


def extract_text_and_images_from_pdf(file_path, max_pages=2, output_folder="temp_images"):
    """Enhanced extractor with proper image-to-page mapping and transparency handling"""

    print(f"🔍 Extracting from: {file_path}")
    print(f"📁 Output folder: {output_folder}")

    if not os.path.exists(file_path):
        return {"text": "", "images": [], "image_folder": ""}

    # Clean up existing folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    text = ""
    images = []
    page_image_map = {}  # Track true source pages for images

    try:
        with fitz.open(file_path) as doc:
            # Pass 1: Map ALL images to their true source pages
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                for img in image_list:
                    xref = img[0]
                    if xref not in page_image_map:
                        page_image_map[xref] = {
                            'source_page': page_num + 1,
                            'source_page_index': page_num
                        }

            # Pass 2: Extract text and images from specified pages
            pages_to_extract = min(max_pages, len(doc))

            for page_num in range(pages_to_extract):
                print(f"\n--- Processing Page {page_num + 1} ---")
                page = doc[page_num]

                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    print(f"✅ Extracted {len(page_text)} characters of text")

                # Extract images with proper handling
                image_list = page.get_images(full=True)
                print(f"🖼️  Found {len(image_list)} images")

                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        smask = img[1] if len(img) > 1 else 0

                        # Get true source page
                        true_source_page = page_image_map.get(xref, {}).get('source_page', page_num + 1)

                        print(f"  Processing image {img_index + 1}: xref={xref}, source=page_{true_source_page}")

                        # Enhanced image extraction
                        base_pix = fitz.Pixmap(doc, xref)

                        # Handle transparency masks
                        if smask > 0:
                            try:
                                mask_pix = fitz.Pixmap(doc, smask)
                                if base_pix.alpha == 0:
                                    final_pix = fitz.Pixmap(base_pix, mask_pix)
                                else:
                                    final_pix = base_pix
                                mask_pix = None
                                print(f"    🎭 Applied transparency mask")
                            except Exception:
                                final_pix = base_pix
                        else:
                            final_pix = base_pix

                        # Convert CMYK to RGB
                        if final_pix.n - final_pix.alpha == 4:
                            rgb_pix = fitz.Pixmap(fitz.csRGB, final_pix)
                            final_pix = None
                            final_pix = rgb_pix
                            print(f"    🎨 Converted CMYK to RGB")

                        width, height = final_pix.width, final_pix.height
                        print(f"    📐 Dimensions: {width}x{height}")

                        # Quality filtering
                        if width < 100 or height < 100:
                            print(f"    ❌ Skipped: too small")
                            final_pix = None
                            continue

                        if width > 2000 and height > 2000:
                            print(f"    ❌ Skipped: likely background")
                            final_pix = None
                            continue

                        # Save with source page info
                        filename = f"source_page_{true_source_page}_img_{img_index + 1}.png"
                        filepath = os.path.join(output_folder, filename)

                        final_pix.save(filepath)
                        final_pix = None

                        # Verify image quality
                        try:
                            with Image.open(filepath) as pil_img:
                                if pil_img.mode == 'RGB':
                                    pixels = list(pil_img.getdata())
                                    sample = pixels[::max(1, len(pixels) // 20)][:20]
                                    avg_brightness = sum(sum(p) / 3 for p in sample) / len(sample)

                                    if avg_brightness < 5:
                                        print(f"    ❌ Skipped: too dark")
                                        os.remove(filepath)
                                        continue

                                images.append({
                                    "page": page_num + 1,
                                    "source_page": true_source_page,
                                    "index": img_index + 1,
                                    "filename": filename,
                                    "path": filepath,
                                    "width": width,
                                    "height": height,
                                    "xref": xref
                                })
                                print(f"    ✅ Added: {filename}")

                        except Exception:
                            if os.path.exists(filepath):
                                os.remove(filepath)

                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                        continue

        print(f"\n🎯 Final Results:")
        print(f"   📝 Text: {len(text)} characters")
        print(f"   🖼️  Images: {len(images)}")

        return {
            "text": text.strip(),
            "images": images,
            "image_folder": output_folder
        }

    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        return {"text": "", "images": [], "image_folder": ""}


def extract_text_from_pdf(file_path, max_pages=2):
    """Backward compatibility function"""
    result = extract_text_and_images_from_pdf(file_path, max_pages)
    return result["text"]
