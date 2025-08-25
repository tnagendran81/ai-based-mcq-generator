import openai
import os
import re
import math

openai.api_key = os.getenv("OPENAI_API_KEY")


def split_text_into_chunks(text, max_words=600):
    """Split text into manageable chunks for processing"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


def generate_mcqs(text, total_questions=25, complexity_distribution=None):
    """Generate MCQs with accurate count and complexity distribution"""
    if not text.strip():
        return []

    # Default complexity distribution
    if complexity_distribution is None:
        complexity_distribution = {"low": 40, "medium": 40, "hard": 20}

    # Calculate exact question counts
    easy_count = int(total_questions * complexity_distribution.get("low", 40) / 100)
    medium_count = int(total_questions * complexity_distribution.get("medium", 40) / 100)
    hard_count = total_questions - easy_count - medium_count

    # Ensure hard_count is not negative
    if hard_count < 0:
        hard_count = 0
        medium_count = total_questions - easy_count

    print(f"Generating: Easy={easy_count}, Medium={medium_count}, Hard={hard_count}")

    chunks = split_text_into_chunks(text)
    all_mcqs = []

    # Generate by complexity level
    complexity_levels = [
        ("easy", easy_count),
        ("medium", medium_count),
        ("hard", hard_count)
    ]

    for complexity, count in complexity_levels:
        if count <= 0:
            continue
        questions = generate_questions_by_complexity(chunks, count, complexity)
        all_mcqs.extend(questions)

    return all_mcqs[:total_questions]


def generate_questions_by_complexity(chunks, question_count, complexity):
    """Generate questions for specific complexity level"""
    questions = []
    questions_per_chunk = max(1, question_count // len(chunks))
    remaining_questions = question_count

    complexity_instructions = {
        "easy": "Create simple questions focusing on basic facts, definitions, and direct recall from the text.",
        "medium": "Create questions requiring understanding of relationships, basic analysis, and application of concepts.",
        "hard": "Create challenging questions requiring deep analysis, evaluation, synthesis, and critical thinking."
    }

    for i, chunk in enumerate(chunks):
        if remaining_questions <= 0:
            break

        # Calculate questions for this chunk
        remaining_chunks = len(chunks) - i
        if remaining_chunks > 1:
            current_questions = min(questions_per_chunk, remaining_questions)
        else:
            current_questions = remaining_questions

        if current_questions <= 0:
            continue

        prompt = f"""Create {current_questions} {complexity} difficulty multiple choice questions from this text.

{complexity_instructions[complexity]}

Text: {chunk}

Format each question exactly as:
Question 1: [Your question here]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Answer: [A/B/C/D]
Explanation: [Brief explanation why this answer is correct]

Requirements:
- Generate exactly {current_questions} questions
- Each question must have 4 options (A, B, C, D)
- Do NOT include markers like **CORRECT** or **WRONG** in options
- Provide clear explanations for each answer
- Base questions strictly on the provided text"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2500
            )

            content = response['choices'][0]['message']['content']
            chunk_questions = parse_ai_response(content, complexity)

            chunk_questions = chunk_questions[:current_questions]
            questions.extend(chunk_questions)
            remaining_questions -= len(chunk_questions)

        except Exception as e:
            print(f"Error generating {complexity} questions: {e}")
            continue

    return questions


def parse_ai_response(content, complexity):
    """Parse AI response with marker removal and robust extraction"""
    mcqs = []

    # Remove unwanted markers
    content = re.sub(r'\*\*(CORRECT|WRONG|RIGHT)\*\*', '', content, flags=re.IGNORECASE)

    # Split by questions
    question_blocks = re.split(r'Question\s+\d+\s*:', content, flags=re.IGNORECASE)

    for block in question_blocks[1:]:  # Skip first empty element
        lines = [line.strip() for line in block.split('\n') if line.strip()]

        if len(lines) < 6:  # Need question + 4 options + answer + explanation
            continue

        # Extract question
        question_text = lines[0]

        # Extract options
        options = []
        answer = ""
        explanation = ""

        for line in lines[1:]:
            if re.match(r'^[A-D]\)', line, re.IGNORECASE):
                option_text = re.sub(r'^[A-D]\)\s*', '', line, flags=re.IGNORECASE)
                options.append(option_text.strip())
            elif line.lower().startswith('answer:'):
                answer_match = re.search(r'answer:\s*([A-D])', line, re.IGNORECASE)
                if answer_match:
                    answer = answer_match.group(1).upper()
            elif line.lower().startswith('explanation:'):
                explanation = line.split(':', 1)[1].strip()

        # Only add complete questions
        if len(options) == 4 and question_text and answer and explanation:
            mcqs.append({
                "question": question_text,
                "options": options,
                "answer": answer,
                "explanation": explanation,
                "complexity": complexity
            })

    return mcqs
