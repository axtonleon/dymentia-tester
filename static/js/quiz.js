// --- DOM ELEMENT REFERENCES ---
const startScreen = document.getElementById('start-screen');
const quizScreen = document.getElementById('quiz-screen');
const reportScreen = document.getElementById('report-screen');
const startQuizBtn = document.getElementById('start-quiz-btn');
const controlBtn = document.getElementById('control-btn');
const statusText = document.getElementById('status-text');
const reportSummary = document.getElementById('report-summary');
const reportDetails = document.getElementById('report-details');

// --- STATE MANAGEMENT ---
const patientId = JSON.parse(document.getElementById('patient-id-data').textContent);
let allQuestions = [];
let sessionResults = [];
let currentQuestionIndex = 0;

let mediaRecorder;
let audioChunks = [];
let startTime;
let currentState = 'idle';

// --- CORE LOGIC ---

async function startQuiz() {
    startScreen.classList.add('hidden');
    quizScreen.classList.remove('hidden');
    updateUI('loading-session', 'Initializing assessment...');
    
    try {
        const response = await fetch(`/api/quiz-questions/${patientId}`);
        if (!response.ok) throw new Error('Could not load quiz session.');
        allQuestions = await response.json();

        if (allQuestions.length === 0) {
            updateUI('error', 'No quiz data available for this patient.');
            return;
        }
        
        sessionResults = [];
        currentQuestionIndex = 0;
        askNextQuestion();
    } catch (error) {
        console.error("Error starting quiz:", error);
        updateUI('error', error.message);
    }
}

async function askNextQuestion() {
    if (currentQuestionIndex >= allQuestions.length) {
        finishQuiz();
        return;
    }

    const question = allQuestions[currentQuestionIndex];
    const progress = `Question ${currentQuestionIndex + 1} of ${allQuestions.length}`;
    updateUI('getting-question', progress);

    try {
        const response = await fetch('/api/text-to-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: question.question_text })
        });

        if (!response.ok) throw new Error('Could not generate question audio.');
        
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        playQuestionAudio(audioUrl);
    } catch (error) {
         console.error("Error getting question audio:", error);
         updateUI('error', 'Could not get question audio.');
    }
}

function playQuestionAudio(audioUrl) {
    updateUI('playing-question', 'Listen carefully...');
    const audio = new Audio(audioUrl);
    audio.play();
    audio.onended = () => {
        updateUI('ready-to-record', 'Press the button to start recording');
    };
}

async function startRecording() {
    updateUI('recording', 'Recording... Press to stop');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
        mediaRecorder.onstop = uploadAudio; 
        mediaRecorder.start();
        startTime = Date.now();
    } catch (error) {
        console.error("Error accessing microphone:", error);
        updateUI('error', 'Microphone access denied.');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
}

async function uploadAudio() {
    updateUI('evaluating', 'Evaluating your answer...');
    const responseTime = (Date.now() - startTime) / 1000;
    const currentQuestion = allQuestions[currentQuestionIndex];

    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'response.webm');
    formData.append('response_time', responseTime);
    formData.append('reference_answer_b64', btoa(currentQuestion.reference_answer));

    try {
        const response = await fetch('/api/submit-answer', { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Could not evaluate answer.');
        
        const result = await response.json();
        
        sessionResults.push({
            question_text: currentQuestion.question_text,
            transcribed_text: result.transcribed_text,
            score: result.score,
            feedback: result.feedback
        });

        currentQuestionIndex++;
        askNextQuestion();

    } catch (error) {
        console.error("Error submitting answer:", error);
        updateUI('error', 'Could not evaluate your answer.');
    }
}

async function finishQuiz() {
    updateUI('summarizing', 'Generating final report...');
    
    try {
        const response = await fetch('/api/summarize-quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient_id: patientId, results: sessionResults })
        });
        if (!response.ok) throw new Error('Could not generate summary.');

        const finalReport = await response.json();
        displayFinalReport(finalReport);
    } catch (error) {
        console.error("Error finishing quiz:", error);
        updateUI('error', 'Could not create report.');
    }
}

function displayFinalReport(report) {
    quizScreen.classList.add('hidden');
    reportScreen.classList.remove('hidden');

    reportSummary.textContent = report.summary;
    reportDetails.innerHTML = '';

    report.results.forEach(item => {
        const scoreColor = item.score >= 70 ? 'text-green-400' : item.score >= 40 ? 'text-yellow-400' : 'text-red-400';
        const li = document.createElement('li');
        li.className = 'bg-slate-800/50 p-4 rounded-lg';
        li.innerHTML = `
            <p class="font-semibold text-slate-300">Q: ${item.question_text}</p>
            <p class="italic text-slate-400 my-1">A: "${item.transcribed_text}"</p>
            <div class="flex justify-between items-center mt-2">
                <p class="text-sm">${item.feedback}</p>
                <p class="text-lg font-mono ${scoreColor}">${item.score}/100</p>
            </div>
        `;
        reportDetails.appendChild(li);
    });
}

function updateUI(state, message = '') {
    currentState = state;
    const controlBtnIcon = controlBtn.querySelector('i');
    controlBtn.disabled = true;
    controlBtn.className = "w-24 h-24 text-white rounded-full flex items-center justify-center text-4xl transition-all shadow-lg";

    statusText.textContent = message;

    switch (state) {
        case 'idle':
            break;
        case 'loading-session':
        case 'getting-question':
        case 'summarizing':
            controlBtn.classList.add('bg-slate-500');
            controlBtnIcon.className = 'fas fa-spinner fa-spin';
            break;
        case 'playing-question':
            controlBtn.classList.add('bg-slate-500');
            controlBtnIcon.className = 'fa-solid fa-volume-high';
            break;
        case 'ready-to-record':
            controlBtn.disabled = false;
            controlBtn.classList.add('bg-green-500', 'hover:bg-green-400');
            controlBtnIcon.className = 'fa-solid fa-microphone';
            break;
        case 'recording':
            controlBtn.disabled = false;
            controlBtn.classList.add('bg-red-500', 'hover:bg-red-400', 'animate-pulse');
            controlBtnIcon.className = 'fa-solid fa-stop';
            break;
        case 'evaluating':
            controlBtn.classList.add('bg-purple-500');
            controlBtnIcon.className = 'fas fa-spinner fa-spin';
            break;
        case 'error':
            controlBtn.disabled = false;
            controlBtn.classList.add('bg-yellow-500');
            controlBtnIcon.className = 'fa-solid fa-exclamation-triangle';
            break;
    }
}

function handleControlButtonClick() {
    switch (currentState) {
        case 'ready-to-record': startRecording(); break;
        case 'recording': stopRecording(); break;
        case 'error': startQuiz(); break;
    }
}

startQuizBtn.addEventListener('click', startQuiz);
controlBtn.addEventListener('click', handleControlButtonClick);
