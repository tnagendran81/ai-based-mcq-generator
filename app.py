import os
import uuid
import shutil
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from dotenv import load_dotenv
import fitz  # PyMuPDF

from mcq_core.generator import generate_mcqs
from mcq_core.extractor import extract_text_and_images_from_pdf, extract_text_from_pdf
from mcq_core.pdf_utils import generate_mcq_pdf, generate_answer_pdf

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
TEMP_IMAGES_FOLDER = "temp_images"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_IMAGES_FOLDER, exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # File validation
        if "pdf" not in request.files:
            flash("No file part in request.", "error")
            return redirect(request.url)

        pdf_file = request.files["pdf"]
        if not pdf_file or pdf_file.filename == "":
            flash("No file selected.", "error")
            return redirect(request.url)

        if not pdf_file.filename.lower().endswith(".pdf"):
            flash("Please upload a valid PDF file.", "error")
            return redirect(request.url)

        try:
            # Get and validate parameters
            pages_requested = max(1, min(int(request.form.get("pages", 2)), 50))
            questions_requested = max(5, min(int(request.form.get("questions", 10)), 50))

            # Get complexity distribution from sliders
            low_percent = max(0, min(100, int(request.form.get("low_complexity", 40))))
            medium_percent = max(0, min(100, int(request.form.get("medium_complexity", 40))))
            hard_percent = max(0, min(100, int(request.form.get("hard_complexity", 20))))

            # Normalize percentages
            total_percent = low_percent + medium_percent + hard_percent
            if total_percent == 0:
                low_percent = medium_percent = hard_percent = 33
                total_percent = 99

            low_percent = int(low_percent * 100 / total_percent)
            medium_percent = int(medium_percent * 100 / total_percent)
            hard_percent = 100 - low_percent - medium_percent

            complexity_distribution = {
                'low': low_percent,
                'medium': medium_percent,
                'hard': hard_percent
            }

        except Exception as e:
            flash(f"Invalid input values: {e}", "error")
            return redirect(request.url)

        # Save uploaded file
        filename = f"{uuid.uuid4()}.pdf"
        temp_file_path = os.path.join(UPLOAD_FOLDER, filename)
        session_id = uuid.uuid4().hex[:8]
        session_image_folder = os.path.join(TEMP_IMAGES_FOLDER, session_id)

        try:
            pdf_file.save(temp_file_path)

            # Extract text and images
            extraction_result = extract_text_and_images_from_pdf(
                temp_file_path,
                max_pages=pages_requested,
                output_folder=session_image_folder
            )

            if not extraction_result["text"].strip():
                flash("No extractable text found in the PDF.", "error")
                cleanup_temp_files(temp_file_path, session_image_folder)
                return redirect(request.url)

            print(f"Extracted text from {pages_requested} pages")
            print(f"Found {len(extraction_result['images'])} images")

            # Generate MCQs with complexity support
            import inspect
            sig = inspect.signature(generate_mcqs)

            if 'complexity_distribution' in sig.parameters:
                mcqs = generate_mcqs(extraction_result["text"], questions_requested, complexity_distribution)
            else:
                mcqs = generate_mcqs(extraction_result["text"], questions_requested)

            # Add image references to MCQs
            if extraction_result["images"]:
                mcqs = add_image_references_to_mcqs(mcqs, extraction_result["images"])

            if not mcqs:
                flash("MCQ generation failed.", "error")
                cleanup_temp_files(temp_file_path, session_image_folder)
                return redirect(request.url)

            # Generate PDFs
            mcq_filename = f"mcqs_{session_id}.pdf"
            ans_filename = f"answers_{session_id}.pdf"

            mcq_path = os.path.join(OUTPUT_FOLDER, mcq_filename)
            ans_path = os.path.join(OUTPUT_FOLDER, ans_filename)

            if not generate_mcq_pdf(mcqs, mcq_path):
                flash("Failed to create MCQ PDF.", "error")
                cleanup_temp_files(temp_file_path, session_image_folder)
                return redirect(request.url)

            if not generate_answer_pdf(mcqs, ans_path):
                flash("Failed to create answer key PDF.", "error")
                cleanup_temp_files(temp_file_path, session_image_folder)
                return redirect(request.url)

            # Count results
            complexity_counts = {'easy': 0, 'medium': 0, 'hard': 0}
            total_images = 0

            for mcq in mcqs:
                complexity = mcq.get('complexity', 'medium')
                if complexity in complexity_counts:
                    complexity_counts[complexity] += 1
                if mcq.get('images'):
                    total_images += len(mcq['images'])

            success_message = f'Generated {len(mcqs)} MCQs with {total_images} images! '
            success_message += f'(Easy: {complexity_counts["easy"]}, Medium: {complexity_counts["medium"]}, Hard: {complexity_counts["hard"]})'
            flash(success_message, "success")

            # Clean up temp files
            cleanup_temp_files(temp_file_path, session_image_folder)

            return render_template(
                "index.html",
                mcq_path=mcq_filename,
                ans_path=ans_filename,
                success=True,
                question_count=len(mcqs),
                page_count=pages_requested,
                image_count=total_images,
                complexity_counts=complexity_counts
            )

        except Exception as e:
            flash(f"Error processing PDF: {e}", "error")
            cleanup_temp_files(temp_file_path, session_image_folder)
            return redirect(request.url)

    return render_template("index.html", success=False)


def add_image_references_to_mcqs(mcqs, images):
    """Smart assignment of images only to questions that need them"""
    if not images:
        print("DEBUG: No images available")
        return mcqs

    print(f"DEBUG: Have {len(images)} images for {len(mcqs)} questions")

    # Keywords indicating visual content
    visual_keywords = [
        'figure', 'diagram', 'graph', 'chart', 'table', 'image', 'picture',
        'illustration', 'example', 'shown', 'following', 'given',
        'tower', 'building', 'angle', 'triangle', 'circle', 'line'
    ]

    # Only assign images to questions with visual references
    image_index = 0
    assigned_count = 0

    for mcq in mcqs:
        question_lower = mcq['question'].lower()

        # Check if question mentions visual elements
        has_visual_ref = any(keyword in question_lower for keyword in visual_keywords)

        if has_visual_ref and image_index < len(images):
            mcq['images'] = [images[image_index]]
            print(f"DEBUG: Assigned {images[image_index]['filename']} to: {mcq['question'][:50]}...")
            image_index += 1
            assigned_count += 1
        else:
            mcq['images'] = []  # No image for non-visual questions

    print(f"DEBUG: {assigned_count} questions got images, {len(mcqs) - assigned_count} without images")
    return mcqs


def cleanup_temp_files(temp_file_path, session_image_folder):
    """Clean up temporary files and folders"""
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if os.path.exists(session_image_folder):
            shutil.rmtree(session_image_folder)
    except Exception as e:
        print(f"Error cleaning up: {e}")


@app.route("/download/<filename>")
def download_file(filename):
    """Secure file download handler"""
    try:
        # Security: prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            flash("Invalid filename.", "error")
            return redirect(url_for("index"))

        file_path = os.path.join(OUTPUT_FOLDER, filename)

        if not os.path.isfile(file_path):
            flash("File not found.", "error")
            return redirect(url_for("index"))

        # Additional security check
        if not os.path.abspath(file_path).startswith(os.path.abspath(OUTPUT_FOLDER)):
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        flash(f"Error downloading file: {e}", "error")
        return redirect(url_for("index"))


@app.errorhandler(413)
def too_large(e):
    flash("File too large. Please upload a smaller PDF.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
    app.run(debug=True, host="0.0.0.0", port=5000)
