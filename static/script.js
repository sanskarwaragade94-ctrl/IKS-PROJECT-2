let quizQuestions = [];
let selectedQuizAnswers = [];
let shownQuizQuestionIds = [];

function getInputValue(id) {
  const input = document.getElementById(id);
  return input ? input.value.trim() : "";
}

function setToolInput(id, value) {
  const input = document.getElementById(id);
  if (input) {
    input.value = value;
    input.focus();
  }
}

async function postJson(url, payload = null, method = "POST") {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };

  if (payload !== null) {
    options.body = JSON.stringify(payload);
  }

  const response = await fetch(url, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }

  return data;
}

function setResult(message, type = "success") {
  const result = document.getElementById("result");
  if (!result) {
    return;
  }

  result.classList.remove("is-error", "is-success");
  result.classList.add(type === "error" ? "is-error" : "is-success");
  result.textContent = message;
}

function clearResult() {
  const result = document.getElementById("result");
  if (!result) {
    return;
  }

  result.classList.remove("is-error", "is-success");
  result.textContent = "Choose a module below to see the response from the backend.";
}

function scrollToQuiz() {
  const panel = document.getElementById("quiz-panel");
  if (panel) {
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function resetQuizResults() {
  const quizResults = document.getElementById("quizResults");
  if (!quizResults) {
    return;
  }

  quizResults.classList.remove("is-error", "is-success");
  quizResults.textContent = "Submit the Brainstorming Quiz to see your score and answer review here.";
}

function setSelectedQuizAnswer(questionIndex, answer) {
  selectedQuizAnswers[questionIndex] = answer;

  const optionButtons = document.querySelectorAll(`[data-question-index="${questionIndex}"]`);
  optionButtons.forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.answer === answer);
  });
}

function renderQuizQuestions(questions) {
  const quizBox = document.getElementById("quizQuestions");
  if (!quizBox) {
    return;
  }

  if (!questions.length) {
    quizBox.textContent = "No quiz questions are available right now.";
    return;
  }

  quizBox.innerHTML = questions
    .map((question, index) => {
      const options = question.options
        .map((option) => {
          const answer = option.charAt(0);
          return `
            <button
              class="quiz-option-button"
              type="button"
              data-question-index="${index}"
              data-answer="${answer}"
              onclick="setSelectedQuizAnswer(${index}, '${answer}')"
            >
              ${option}
            </button>
          `;
        })
        .join("");

      return `
        <div class="quiz-question-item">
          <p class="quiz-question-title">Q${index + 1}: ${question.q}</p>
          <div class="quiz-options-grid">${options}</div>
        </div>
      `;
    })
    .join("");
}

function renderQuizResults(data) {
  const quizResults = document.getElementById("quizResults");
  if (!quizResults) {
    return;
  }

  const findOptionText = (options, answer) => {
    const matchingOption = options.find((option) => option.startsWith(`${answer}.`));
    return matchingOption || answer || "No answer selected";
  };

  const details = data.results
    .map((item, index) => {
      const userAnswer = findOptionText(item.options, item.user_answer);
      const correctAnswer = findOptionText(item.options, item.correct_answer);
      const statusClass = item.is_correct ? "is-correct" : "is-wrong";
      const statusLabel = item.is_correct ? "Correct" : "Wrong";

      return `
        <div class="quiz-review-item ${statusClass}">
          <p class="quiz-review-title">Q${index + 1}: ${item.question}</p>
          <p>Your answer: <strong>${userAnswer}</strong></p>
          <p>Correct answer: <strong>${correctAnswer}</strong></p>
          <p>Status: <strong>${statusLabel}</strong></p>
        </div>
      `;
    })
    .join("");

  quizResults.classList.remove("is-error");
  quizResults.classList.add("is-success");
  quizResults.innerHTML = `
    <div class="quiz-score-summary">
      <strong>Score: ${data.score}/${data.total}</strong>
    </div>
    <div class="quiz-review-list">${details}</div>
  `;
}

async function runNasta() {
  const rawValue = getInputValue("nastaInput");

  if (!rawValue) {
    setResult("Please enter a number first.", "error");
    return;
  }

  const number = Number(rawValue);
  if (!Number.isInteger(number)) {
    setResult("Please enter a valid integer for Nasta conversion.", "error");
    return;
  }

  try {
    const data = await postJson("/to-binary", { number });
    setResult(`Binary Sequence: ${data.binary}`);
  } catch (error) {
    setResult(error.message, "error");
  }
}

async function runUddishta() {
  const binary = getInputValue("uddishtaInput");

  if (!binary) {
    setResult("Please enter a binary sequence first.", "error");
    return;
  }

  try {
    const data = await postJson("/to-number", { binary });
    setResult(`Row Number: ${data.row_number}`);
  } catch (error) {
    setResult(error.message, "error");
  }
}

async function checkPalindrome() {
  const value = getInputValue("palindromeInput");

  if (!value) {
    setResult("Please enter a word, number, or binary value first.", "error");
    return;
  }

  try {
    const data = await postJson("/api/palindrome", { value });
    setResult(data.is_palindrome ? "Palindrome detected." : "This value is not a palindrome.");
  } catch (error) {
    setResult(error.message, "error");
  }
}

async function wordCheck() {
  const word = getInputValue("wordInput");

  if (!word) {
    setResult("Please enter a word first.", "error");
    return;
  }

  try {
    const data = await postJson("/api/word-check", { word });
    setResult(
      `Binary: ${data.binary_sequence}\nBinary Palindrome: ${data.binary_palindrome ? "Yes" : "No"}\nWord Palindrome: ${data.word_palindrome ? "Yes" : "No"}`
    );
  } catch (error) {
    setResult(error.message, "error");
  }
}

async function loadQuiz() {
  try {
    const excludeParam = shownQuizQuestionIds.join(",");
    quizQuestions = await postJson(excludeParam ? `/api/quiz?exclude=${excludeParam}` : "/api/quiz", null, "GET");

    const currentQuestionIds = quizQuestions.map((question) => question.id);
    const isRepeatBatch = currentQuestionIds.every((id) => shownQuizQuestionIds.includes(id));

    if (isRepeatBatch) {
      shownQuizQuestionIds = [...currentQuestionIds];
    } else {
      shownQuizQuestionIds = [...shownQuizQuestionIds, ...currentQuestionIds];
    }

    selectedQuizAnswers = new Array(quizQuestions.length).fill("");
    renderQuizQuestions(quizQuestions);
    resetQuizResults();
    setResult(isRepeatBatch ? "A new quiz cycle has started with 5 questions. Choose one option for each and submit." : "Quiz loaded with 5 questions. Choose one option button for each question, then submit.");
  } catch (error) {
    setResult(error.message, "error");
  }
}

async function submitQuiz() {
  if (!quizQuestions.length) {
    setResult("Please load the quiz first.", "error");
    return;
  }

  if (selectedQuizAnswers.some((answer) => !answer)) {
    setResult("Please choose one answer for each quiz question before submitting.", "error");
    return;
  }

  try {
    const data = await postJson("/api/quiz", {
      question_ids: quizQuestions.map((question) => question.id),
      answers: selectedQuizAnswers,
    });
    renderQuizResults(data);
    setResult(`Score submitted. You got ${data.score} out of ${data.total}.`);
  } catch (error) {
    setResult(error.message, "error");
  }
}
