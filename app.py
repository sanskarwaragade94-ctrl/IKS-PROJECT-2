import os

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


def nasta_binary(num, binary_list):
    if num >= 2:
        if num % 2 == 0:
            num = num // 2
            binary_list.append(1)
            return nasta_binary(num, binary_list)
        num = (num + 1) // 2
        binary_list.append(0)
        return nasta_binary(num, binary_list)
    return binary_list


def uddishta_row(binary_seq):
    reversed_seq = binary_seq[::-1]
    decimal_value = 0

    for i in range(len(reversed_seq)):
        if reversed_seq[i] == "1":
            decimal_value += 2 ** (len(reversed_seq) - 1 - i)

    return decimal_value + 1


def sanitize_letters(value):
    return "".join(char.lower() for char in value if char.isalpha())


def word_to_pingala_binary(word):
    vowels = {"a", "e", "i", "o", "u"}
    letters = [char.lower() for char in word if char.isalpha()]
    return "".join("0" if char in vowels else "1" for char in letters)


QUIZ_QUESTIONS = [
    {
        "id": 1,
        "q": "Acharya Pingala is best known for which foundational text that bridges the gap between Sanskrit prosody (meters) and mathematics?",
        "options": ["A. Aryabhatiya", "B. Chhandasutra", "C. Lilavati", "D. Baudhayana Shulba Sutra"],
        "answer": "B",
    },
    {
        "id": 2,
        "q": "In Pingala's binary system, what do the terms 'Laghu' and 'Guru' represent?",
        "options": ["A. Prime and Composite numbers", "B. Positive and Negative integers", "C. Short and Long syllables", "D. Even and Odd numbers"],
        "answer": "C",
    },
    {
        "id": 3,
        "q": "Which mathematical structure described by Pingala is considered the Indian precursor to Pascal's Triangle?",
        "options": ["A. Meru Prastara", "B. Shri Yantra", "C. Nasta Algorithm", "D. Varna Samkhya"],
        "answer": "A",
    },
    {
        "id": 4,
        "q": "If a meter has 'n' syllables, Pingala's algorithm determines that the total number of possible combinations is given by which formula?",
        "options": ["A. n^2", "B. 2^n", "C. n!", "D. 2n"],
        "answer": "B",
    },
    {
        "id": 5,
        "q": "Which of Pingala's algorithms is used to find the specific metrical pattern when its rank or index number is known?",
        "options": ["A. Uddista", "B. Nasta", "C. Prastara", "D. Samkhya"],
        "answer": "B",
    },
    {
        "id": 6,
        "q": "Pingala's work is considered an early example of 'algorithmic thinking' because his rules are often:",
        "options": ["A. Randomized", "B. Recursive", "C. Purely descriptive", "D. Based on trial and error"],
        "answer": "B",
    },
    {
        "id": 7,
        "q": "In the context of 'Meru Prastara', what does each row represent in modern mathematical terms?",
        "options": ["A. The digits of Pi", "B. Binomial coefficients", "C. Prime factors", "D. Logarithmic scales"],
        "answer": "B",
    },
    {
        "id": 8,
        "q": "Pingala's method for calculating powers of 2 (like 2^8) used a shortcut that modern computer scientists would recognize as:",
        "options": ["A. Linear Search", "B. Binary Exponentiation", "C. Bubble Sort", "D. Floating point arithmetic"],
        "answer": "B",
    },
    {
        "id": 9,
        "q": "Which later Indian mathematician famously expanded on Pingala's work to describe what is now known as the Fibonacci sequence?",
        "options": ["A. Varahamihira", "B. Hemachandra", "C. Brahmagupta", "D. Madhava"],
        "answer": "B",
    },
    {
        "id": 10,
        "q": "Why is Pingala often referred to as the 'Father of the Binary System'?",
        "options": ["A. He invented the first mechanical computer", "B. He used two symbols to represent all possible metrical variations", "C. He was the first to use the symbol '0' in calculations", "D. He translated modern computer manuals into Sanskrit"],
        "answer": "B",
    },
]


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/home")
@app.route("/calculator")
def home():
    return render_template("home.html")


@app.route("/to-binary", methods=["POST"])
@app.route("/api/nasta", methods=["POST"])
def to_binary():
    data = request.get_json(silent=True) or {}
    number = data.get("number")

    if not isinstance(number, int):
        return jsonify({"error": "Invalid input. Please enter an integer."}), 400
    if number < 0:
        return jsonify({"error": "Please enter a non-negative integer."}), 400
    if number == 0:
        return jsonify({"binary": "0"})

    result = "".join(str(bit) for bit in nasta_binary(number, []))
    return jsonify({"binary": result})


@app.route("/to-number", methods=["POST"])
@app.route("/api/uddishta", methods=["POST"])
def to_number():
    data = request.get_json(silent=True) or {}
    binary_seq = data.get("binary")

    if not isinstance(binary_seq, str):
        return jsonify({"error": "Invalid input. Please enter a binary string."}), 400

    binary_seq = binary_seq.strip()
    if not binary_seq or any(char not in {"0", "1"} for char in binary_seq):
        return jsonify({"error": "Binary input must contain only 0 and 1."}), 400

    return jsonify({"row_number": uddishta_row(binary_seq)})


@app.route("/api/palindrome", methods=["POST"])
def palindrome():
    data = request.get_json(silent=True) or {}
    value = str(data.get("value", "")).strip()

    if not value:
        return jsonify({"error": "Please enter a value to check."}), 400

    normalized = "".join(char.lower() for char in value if char.isalnum())
    if not normalized:
        return jsonify({"error": "Please enter letters or numbers only."}), 400

    return jsonify({"is_palindrome": normalized == normalized[::-1]})


@app.route("/api/word-check", methods=["POST"])
def word_check():
    data = request.get_json(silent=True) or {}
    word = str(data.get("word", "")).strip()
    cleaned = sanitize_letters(word)

    if not cleaned:
        return jsonify({"error": "Please enter a word using alphabet letters."}), 400

    binary_sequence = word_to_pingala_binary(cleaned)
    return jsonify(
        {
            "binary_sequence": binary_sequence,
            "binary_palindrome": binary_sequence == binary_sequence[::-1],
            "word_palindrome": cleaned == cleaned[::-1],
        }
    )


@app.route("/api/quiz", methods=["GET", "POST"])
def quiz():
    if request.method == "GET":
        raw_exclude = request.args.get("exclude", "")
        excluded_ids = {
            int(item)
            for item in raw_exclude.split(",")
            if item.strip().isdigit()
        }
        available_questions = [item for item in QUIZ_QUESTIONS if item["id"] not in excluded_ids]
        if not available_questions:
            available_questions = QUIZ_QUESTIONS[:]

        public_questions = [
            {"id": item["id"], "q": item["q"], "options": item["options"]}
            for item in available_questions[:5]
        ]
        return jsonify(public_questions)

    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    question_ids = data.get("question_ids", [])

    if not isinstance(answers, list):
        return jsonify({"error": "Answers must be sent as a list."}), 400
    if not isinstance(question_ids, list):
        return jsonify({"error": "Question ids must be sent as a list."}), 400
    if len(answers) != len(question_ids):
        return jsonify({"error": "Answers and question ids must have the same length."}), 400

    normalized_answers = [str(answer).strip().upper() for answer in answers]
    normalized_ids = []
    for question_id in question_ids:
        try:
            normalized_ids.append(int(question_id))
        except (TypeError, ValueError):
            return jsonify({"error": "Each question id must be a valid integer."}), 400

    question_map = {item["id"]: item for item in QUIZ_QUESTIONS}
    results = []
    score = 0

    for question_id, user_answer in zip(normalized_ids, normalized_answers):
        question = question_map.get(question_id)
        if not question:
            return jsonify({"error": "One or more quiz questions could not be found."}), 400

        is_correct = user_answer == question["answer"]

        if is_correct:
            score += 1

        results.append(
            {
                "id": question["id"],
                "question": question["q"],
                "options": question["options"],
                "correct_answer": question["answer"],
                "user_answer": user_answer,
                "is_correct": is_correct,
            }
        )

    return jsonify({"score": score, "total": len(results), "results": results})


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host="0.0.0.0", port=port, debug=debug)
