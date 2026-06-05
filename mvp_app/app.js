const apiBaseUrl =
  window.COMPANA_CONFIG?.API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000";

const runButton = document.getElementById("runButton");
const submitAssessmentButton = document.getElementById("submitAssessmentButton");
const assessmentForm = document.getElementById("assessmentForm");
const projectSubmissionForm = document.getElementById("projectSubmissionForm");
const submitProjectButton = document.getElementById("submitProjectButton");
const userInput = document.getElementById("userInput");
const taskSelect = document.getElementById("taskSelect");
const submissionText = document.getElementById("submissionText");
const submissionFiles = document.getElementById("submissionFiles");
const errorBox = document.getElementById("error");
const resultsSection = document.getElementById("results");
const pretextResult = document.getElementById("pretextResult");
const assessmentQuestions = document.getElementById("assessmentQuestions");
const scoredAnswers = document.getElementById("scoredAnswers");
const validatedContext = document.getElementById("validatedContext");
const skillGap = document.getElementById("skillGap");
const actionPlan = document.getElementById("actionPlan");
const projectEvaluation = document.getElementById("projectEvaluation");
const apiHelpText = document.getElementById("apiHelpText");

let currentPretext = null;
let currentQuestions = [];
let currentRecommendedTasks = [];

apiHelpText.innerHTML = `API aktif: <strong>${apiBaseUrl}</strong>`;

function toPrettyJson(data) {
  return JSON.stringify(data, null, 2);
}

function parseOptions(options) {
  if (Array.isArray(options)) return options;
  return String(options || "")
    .split("|")
    .map((item) => item.trim())
    .filter(Boolean);
}

async function postJson(path, payload) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API error ${response.status}: ${text}`);
  }

  return response.json();
}

function renderQuestions(questions) {
  if (!questions || questions.length === 0) {
    submitAssessmentButton.classList.add("hidden");
    return "<p>Tidak ada pertanyaan assessment.</p>";
  }

  submitAssessmentButton.classList.remove("hidden");
  return questions
    .map((question, index) => {
      const prompt = question.question || question.prompt || "Pertanyaan";
      const isSingleChoice =
        String(question.answer_type || "").toLowerCase() === "single_choice";
      const options = isSingleChoice ? parseOptions(question.options) : [];
      const fieldName = `answer_${question.question_id}`;
      const optionControls = options.length
        ? options
            .map(
              (option, optionIndex) => `
                <label class="option-row">
                  <input
                    type="radio"
                    name="${fieldName}"
                    value="${option}"
                    ${optionIndex === 0 ? "required" : ""}
                  />
                  <span>${option.replaceAll("_", " ")}</span>
                </label>
              `,
            )
            .join("")
        : `
          <textarea
            name="${fieldName}"
            class="answer-textarea"
            placeholder="Tulis jawaban Anda"
            required
          ></textarea>
        `;

      return `
        <fieldset class="question-card">
          <legend>${index + 1}. ${prompt}</legend>
          <div class="question-meta">
            ID: ${question.question_id || "-"} · Skill: ${question.skill_id || "-"} · Level: ${question.difficulty || "-"}
          </div>
          <div class="option-list">${optionControls}</div>
        </fieldset>
      `;
    })
    .join("");
}

function collectAnswers() {
  return currentQuestions.map((question) => {
    const fieldName = `answer_${question.question_id}`;
    const field = assessmentForm.elements[fieldName];
    let value = "";

    if (field instanceof RadioNodeList) {
      value = field.value;
    } else if (field) {
      value = field.value;
    }

    return {
      question_id: question.question_id,
      answer_value: value,
    };
  });
}

function clearDownstreamResults() {
  scoredAnswers.textContent = "";
  validatedContext.textContent = "";
  skillGap.textContent = "";
  actionPlan.textContent = "";
  projectEvaluation.textContent = "";
  taskSelect.innerHTML = "";
  taskSelect.disabled = true;
  submitProjectButton.disabled = true;
}

function renderTaskOptions(tasks) {
  currentRecommendedTasks = tasks || [];
  if (currentRecommendedTasks.length === 0) {
    taskSelect.innerHTML = '<option value="">Tidak ada task rekomendasi</option>';
    taskSelect.disabled = true;
    submitProjectButton.disabled = true;
    return;
  }

  taskSelect.innerHTML = currentRecommendedTasks
    .map(
      (task) => `
        <option value="${task.task_id}">
          ${task.task_id} · ${task.task_title || task.target_skill || "Recommended task"}
        </option>
      `,
    )
    .join("");
  taskSelect.disabled = false;
  submitProjectButton.disabled = false;
}

async function runAnalysis() {
  errorBox.textContent = "";
  resultsSection.classList.add("hidden");
  submitAssessmentButton.classList.add("hidden");
  clearDownstreamResults();

  const text = userInput.value.trim();
  if (!text) {
    errorBox.textContent = "Masukkan teks analisis sebelum menjalankan.";
    return;
  }

  runButton.disabled = true;
  runButton.textContent = "Memproses...";

  try {
    currentPretext = await postJson("/analyze-pretext", {
      user_input_text: text,
    });
    const questionResult = await postJson("/select-questions", {
      pretext_analysis: currentPretext,
      max_questions: 3,
    });

    currentQuestions = questionResult.questions || [];
    resultsSection.classList.remove("hidden");
    pretextResult.textContent = toPrettyJson(currentPretext);
    assessmentQuestions.innerHTML = renderQuestions(currentQuestions);
  } catch (err) {
    errorBox.textContent = err.message;
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Mulai Assessment";
  }
}

async function submitAssessment(event) {
  event.preventDefault();
  errorBox.textContent = "";

  if (!currentPretext || currentQuestions.length === 0) {
    errorBox.textContent = "Jalankan assessment dulu sebelum submit jawaban.";
    return;
  }

  submitAssessmentButton.disabled = true;
  submitAssessmentButton.textContent = "Mengirim...";

  try {
    const result = await postJson("/submit-assessment", {
      user_id: "U001",
      pretext_analysis: currentPretext,
      questions: currentQuestions,
      answers: collectAnswers(),
    });

    scoredAnswers.textContent = toPrettyJson(result.scored_answers || []);
    validatedContext.textContent = toPrettyJson(result.validated_context || {});
    skillGap.textContent = toPrettyJson(result.skill_gap || {});
    actionPlan.textContent = toPrettyJson(result.action_plan || {});
    renderTaskOptions(result.action_plan?.recommended_tasks || []);
  } catch (err) {
    errorBox.textContent = err.message;
  } finally {
    submitAssessmentButton.disabled = false;
    submitAssessmentButton.textContent = "Submit Jawaban";
  }
}

async function submitProject(event) {
  event.preventDefault();
  errorBox.textContent = "";

  const taskId = taskSelect.value;
  const text = submissionText.value.trim();
  const files = submissionFiles.value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);

  if (!taskId) {
    errorBox.textContent = "Pilih task rekomendasi sebelum submit project.";
    return;
  }

  if (!text && files.length === 0) {
    errorBox.textContent = "Isi submission atau lampirkan file/link pendukung.";
    return;
  }

  submitProjectButton.disabled = true;
  submitProjectButton.textContent = "Mengevaluasi...";

  try {
    const result = await postJson("/evaluate-task", {
      task_id: taskId,
      submission_text: text,
      submission_files: files,
    });
    projectEvaluation.textContent = toPrettyJson(result);
  } catch (err) {
    errorBox.textContent = err.message;
  } finally {
    submitProjectButton.disabled = false;
    submitProjectButton.textContent = "Submit Project";
  }
}

runButton.addEventListener("click", runAnalysis);
assessmentForm.addEventListener("submit", submitAssessment);
projectSubmissionForm.addEventListener("submit", submitProject);
