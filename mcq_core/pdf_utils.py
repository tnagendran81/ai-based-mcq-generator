from fpdf import FPDF
import os
import re
from PIL import Image


def clean_text_for_latin1(text):
    """Clean text to be Latin-1 compatible"""
    if not text:
        return ""

    text = str(text)
    replacements = {
        '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
        '\u2220': 'angle', '\u2264': '<=', '\u2265': '>=', '\u2260': '!=',
        '\u03c0': 'pi', '\u03b1': 'alpha', '\u03b2': 'beta', '\u03b8': 'theta',
        '\uf0d0': '', '\uf0b7': '•', '\uf020': ' ',
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return ''.join(c if ord(c) < 256 else '?' for c in text)


def add_image_with_proper_sizing(pdf, img_path, max_width=120, max_height=80):
    """Add image with proper sizing"""
    try:
        if not os.path.exists(img_path):
            return False

        with Image.open(img_path) as pil_img:
            img_width, img_height = pil_img.size

            # Calculate scaling
            width_scale = max_width / img_width
            height_scale = max_height / img_height
            scale = min(width_scale, height_scale, 1.0)

            final_width = int(img_width * scale)
            final_height = int(img_height * scale)

            # Center horizontally
            page_width = 210  # A4 width in mm
            x_position = (page_width - final_width) / 2

            pdf.image(img_path, x=x_position, y=None, w=final_width, h=final_height)
            return True

    except Exception as e:
        print(f"Error adding image {img_path}: {e}")
        return False


def generate_mcq_pdf(mcqs, path):
    """Generate complete MCQ PDF with all options"""
    if not mcqs:
        return False

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Generated MCQs", ln=True, align="C")
        pdf.ln(5)

        # Summary
        complexity_counts = {'easy': 0, 'medium': 0, 'hard': 0}
        total_images = 0

        for mcq in mcqs:
            complexity = mcq.get('complexity', 'medium')
            if complexity in complexity_counts:
                complexity_counts[complexity] += 1
            if mcq.get('images'):
                total_images += len(mcq['images'])

        pdf.set_font("Arial", "", 10)
        summary = f"Total: {len(mcqs)} questions (Easy: {complexity_counts['easy']}, Medium: {complexity_counts['medium']}, Hard: {complexity_counts['hard']})"
        if total_images > 0:
            summary += f" | Images: {total_images}"

        clean_summary = clean_text_for_latin1(summary)
        pdf.cell(0, 8, clean_summary, ln=True, align="C")
        pdf.ln(8)

        # Generate complete MCQs
        for idx, mcq in enumerate(mcqs, 1):
            # Check page break
            if pdf.get_y() > 250:
                pdf.add_page()

            # Question
            complexity = mcq.get('complexity', 'medium').upper()
            pdf.set_font("Arial", "B", 12)
            question_text = f"{idx}. [{complexity}] {mcq['question']}"
            clean_question = clean_text_for_latin1(question_text)
            pdf.multi_cell(0, 8, clean_question)
            pdf.ln(3)

            # Add images with correct source page references
            if mcq.get('images'):
                for img in mcq['images']:
                    if add_image_with_proper_sizing(pdf, img['path']):
                        pdf.ln(3)
                        pdf.set_font("Arial", "", 9)
                        true_source_page = img.get('source_page', img['page'])
                        img_caption = f"Figure {img['index']} from Page {true_source_page}"
                        clean_caption = clean_text_for_latin1(img_caption)
                        pdf.cell(0, 4, clean_caption, ln=True, align="C")
                        pdf.ln(3)

            # **CRITICAL: Multiple Choice Options**
            pdf.set_font("Arial", "", 11)
            option_letters = ['A', 'B', 'C', 'D']

            options = mcq.get('options', [])
            if not options:
                print(f"WARNING: Question {idx} has no options!")
                options = ['Option A', 'Option B', 'Option C', 'Option D']

            # Display all options
            for i, option in enumerate(options[:4]):
                if i < len(option_letters):
                    option_text = f"   {option_letters[i]}) {option}"
                    clean_option = clean_text_for_latin1(option_text)
                    pdf.multi_cell(0, 6, clean_option)
                    pdf.ln(2)

            pdf.ln(5)  # Space between questions

        pdf.output(path)
        print(f"✅ MCQ PDF generated: {path}")
        return True

    except Exception as e:
        print(f"❌ Error generating MCQ PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_answer_pdf(mcqs, path):
    """Generate answer key PDF"""
    if not mcqs:
        return False

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Answer Key & Explanations", ln=True, align="C")
        pdf.ln(10)

        for idx, mcq in enumerate(mcqs, 1):
            if pdf.get_y() > 260:
                pdf.add_page()

            complexity = mcq.get('complexity', 'medium').upper()
            pdf.set_font("Arial", "B", 12)

            correct_answer = mcq.get('answer', 'A')
            answer_text = f"{idx}. [{complexity}] Correct Answer: {correct_answer}"
            clean_answer = clean_text_for_latin1(answer_text)
            pdf.multi_cell(0, 8, clean_answer)
            pdf.ln(2)

            # Show question briefly
            pdf.set_font("Arial", "", 10)
            question_brief = f"   Question: {mcq['question'][:80]}..."
            clean_question = clean_text_for_latin1(question_brief)
            pdf.multi_cell(0, 6, clean_question)
            pdf.ln(2)

            # Show correct option
            options = mcq.get('options', [])
            if options and correct_answer in ['A', 'B', 'C', 'D']:
                option_index = ord(correct_answer) - ord('A')
                if 0 <= option_index < len(options):
                    correct_option_text = f"   {correct_answer}) {options[option_index]}"
                    clean_correct = clean_text_for_latin1(correct_option_text)
                    pdf.multi_cell(0, 6, clean_correct)
                    pdf.ln(2)

            # Explanation
            explanation = mcq.get('explanation', 'No explanation provided.')
            if explanation and explanation.strip():
                pdf.set_font("Arial", "", 10)
                explanation_text = f"   Explanation: {explanation}"
                clean_explanation = clean_text_for_latin1(explanation_text)
                pdf.multi_cell(0, 6, clean_explanation)

            pdf.ln(8)

        pdf.output(path)
        print(f"✅ Answer PDF generated: {path}")
        return True

    except Exception as e:
        print(f"❌ Error generating answer PDF: {e}")
        return False
