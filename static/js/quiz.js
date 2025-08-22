document.addEventListener('DOMContentLoaded', () => {
    const startQuizBtn = document.getElementById('start-quiz-btn');
    const quizContainer = document.getElementById('quiz-container');
    const quizSetup = document.getElementById('quiz-setup');
    const questionCountInput = document.getElementById('question-count-input');
    const questionDisplay = document.getElementById('question-display');
    const questionImage = document.getElementById('question-image');
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const resultDiv = document.getElementById('result');
    const transcribedTextElem = document.getElementById('transcribed-text');
    const scoreElem = document.getElementById('score');
    const feedbackElem = document.getElementById('feedback');
    const nextQuestionBtn = document.getElementById('next-question-btn');
    const progressBar = document.getElementById('progress-bar');
    const summaryDiv = document.getElementById('summary');
    const readAloudBtn = document.getElementById('read-aloud-btn');
    const startNewQuizBtn = document.getElementById('start-new-quiz-btn');
    const newQuizSection = document.getElementById('new-quiz-section');
    const timerDisplay = document.getElementById('timer-display');

    let quizState = {};
    let mediaRecorder;
    let audioChunks = [];
    let questionStartTime;
    let isRecording = false;

    const readAloud = (text) => {
        if (text) {
            const utterance = new SpeechSynthesisUtterance(text);
            speechSynthesis.speak(utterance);
        }
    };

    const fetchQuestions = async (questionCount) => {
        try {
            const response = await fetch(`/api/quiz-questions?count=${questionCount}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to fetch questions');
            }
            const questions = await response.json();
            quizState = {
                questions: questions,
                currentQuestionIndex: 0,
                results: []
            };
            sessionStorage.setItem('quizState', JSON.stringify(quizState));
            displayQuestion();
        } catch (error) {
            console.error('Error fetching questions:', error);
            questionDisplay.textContent = `Could not load questions: ${error.message}. Please try again later.`;
        }
    };

    const displayQuestion = () => {
        const question = quizState.questions[quizState.currentQuestionIndex];

        // Start with image viewing phase
        startImageViewingPhase(question);
    };

    const startImageViewingPhase = (question) => {
        // Show image and hide question initially
        questionDisplay.textContent = '';
        questionImage.src = `/image/${question.id}`;
        questionImage.classList.remove('fade-out');
        questionImage.classList.add('image-viewing-phase');
        resultDiv.style.display = 'none';

        // Hide recording controls during image viewing
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'none';

        if (nextQuestionBtn) {
            nextQuestionBtn.style.display = 'none';
        }

        // Show image viewing instructions
        const instructionText = "Take a good look at this image. You have 20 seconds to study it carefully.";
        questionDisplay.innerHTML = `<div class="text-lg sm:text-xl font-semibold text-blue-600 dark:text-blue-400 mb-4 animate-pulse">${instructionText}</div>`;

        // Read the instruction aloud
        readAloud(instructionText);

        // Show countdown timer
        showCountdownTimer(20);

        // After 18 seconds, start fade out animation
        setTimeout(() => {
            questionImage.classList.add('fade-out');
        }, 18000);

        // After 20 seconds, move to question phase
        setTimeout(() => {
            startQuestionPhase(question);
        }, 20000);

        updateProgressBar();
    };

    const showCountdownTimer = (seconds) => {
        let remainingTime = seconds;
        const countdownElement = document.createElement('div');
        countdownElement.id = 'countdown-timer';
        countdownElement.className = 'text-center mt-4 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700';
        countdownElement.innerHTML = `
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-2">${remainingTime}</div>
            <div class="text-sm text-blue-500 dark:text-blue-300">seconds remaining to study the image</div>
        `;

        // Insert countdown after question display
        questionDisplay.parentNode.insertBefore(countdownElement, questionDisplay.nextSibling);

        const countdownInterval = setInterval(() => {
            remainingTime--;
            if (remainingTime > 0) {
                countdownElement.innerHTML = `
                    <div class="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-2">${remainingTime}</div>
                    <div class="text-sm text-blue-500 dark:text-blue-300">seconds remaining to study the image</div>
                `;
            } else {
                clearInterval(countdownInterval);
                countdownElement.remove();
            }
        }, 1000);
    };

    const startQuestionPhase = (question) => {
        // Hide the image completely
        questionImage.style.display = 'none';
        questionImage.classList.remove('image-viewing-phase', 'fade-out');

        // Show the question with styling
        questionDisplay.innerHTML = `<div class="question-phase"><div class="text-lg sm:text-xl font-semibold text-gray-700 dark:text-gray-200 mb-4">Now answer this question:</div><div class="text-xl sm:text-2xl font-bold text-gray-800 dark:text-gray-100">${question.question}</div></div>`;

        // Show recording controls
        recordBtn.disabled = false;
        recordBtn.innerHTML = '<span class="flex items-center justify-center"><svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="3"></circle></svg>Start Recording</span>';
        recordBtn.className = 'w-full sm:w-auto px-6 py-3 font-bold text-white bg-green-500 dark:bg-green-600 hover:bg-green-600 dark:hover:bg-green-700 rounded-lg shadow-md dark:shadow-lg transition duration-300';
        recordBtn.style.display = 'block';

        // Reset stop button to initial state
        stopBtn.disabled = true;
        stopBtn.innerHTML = '<span class="flex items-center justify-center"><svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><rect x="6" y="6" width="8" height="8"></rect></svg>Stop Recording</span>';
        stopBtn.className = 'w-full sm:w-auto px-6 py-3 font-bold text-white bg-red-500 dark:bg-red-600 hover:bg-red-600 dark:hover:bg-red-700 rounded-lg shadow-md dark:shadow-lg transition duration-300';
        stopBtn.style.display = 'none';

        // Read the question aloud after a brief pause
        setTimeout(() => {
            readAloud(`Now answer this question: ${question.question}`);
        }, 500);

        // Start timing when question phase begins (not when image is shown)
        questionStartTime = Date.now();
        console.log('Question phase started at:', questionStartTime, 'for question:', question.question);

        // Show timer indicator
        if (timerDisplay) {
            timerDisplay.textContent = "⏱️ Response timer started - Ready to record your answer";
            timerDisplay.style.display = 'block';
        }
    };

    const updateProgressBar = () => {
        const progress = ((quizState.currentQuestionIndex + 1) / quizState.questions.length) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `Question ${quizState.currentQuestionIndex + 1} of ${quizState.questions.length}`;
    };

    startQuizBtn.addEventListener('click', () => {
        // Reset UI
        summaryDiv.style.display = 'none';
        quizContainer.style.display = 'block';
        quizSetup.style.display = 'none';
        if (newQuizSection) {
            newQuizSection.style.display = 'none';
        }

        // Clear old state from session storage and reset quiz state
        sessionStorage.removeItem('quizState');
        quizState = {
            questions: [],
            currentQuestionIndex: 0,
            results: []
        };

        const questionCount = questionCountInput.value;
        fetchQuestions(questionCount);
    });

    if (readAloudBtn) {
        readAloudBtn.addEventListener('click', () => {
            const questionText = questionDisplay.textContent;
            readAloud(questionText);
        });
    }

    if (startNewQuizBtn) {
        startNewQuizBtn.addEventListener('click', () => {
            // Hide summary and quiz container
            summaryDiv.style.display = 'none';
            quizContainer.style.display = 'none';
            if (newQuizSection) {
                newQuizSection.style.display = 'none';
            }

            // Show quiz setup
            quizSetup.style.display = 'block';

            // Clear quiz state from session storage
            sessionStorage.removeItem('quizState');

            // Reset progress bar
            progressBar.style.width = '0%';
            progressBar.textContent = 'Question 0 of 0';

            // Reset question count input to default
            questionCountInput.value = 10;

            // Clear displayed question and image
            questionDisplay.textContent = '';
            questionImage.src = '';

            // Hide result div
            resultDiv.style.display = 'none';
        });
    }

    recordBtn.addEventListener('click', async () => {
        try {
            console.log('Starting recording...');
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            audioChunks = [];
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener('stop', () => {
                const endTime = Date.now();

                // Handle case where questionStartTime might not be set
                if (!questionStartTime) {
                    console.warn('questionStartTime not set, using default response time');
                    questionStartTime = endTime - 3000; // Default to 3 seconds ago
                }

                let responseTime = (endTime - questionStartTime) / 1000;

                // Ensure minimum response time of 0.1 seconds for realistic timing
                responseTime = Math.max(responseTime, 0.1);

                // Debug logging for response time calculation
                console.log('Question start time:', questionStartTime);
                console.log('Recording end time:', endTime);
                console.log('Final response time:', responseTime);

                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                // Hide timer indicator
                if (timerDisplay) {
                    timerDisplay.style.display = 'none';
                }

                // Show processing state
                recordBtn.innerHTML = '<span class="flex items-center justify-center"><div class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div>Processing...</span>';
                recordBtn.className = 'w-full sm:w-auto px-6 py-3 font-bold text-white bg-blue-500 dark:bg-blue-600 rounded-lg shadow-md dark:shadow-lg transition duration-300 cursor-not-allowed';
                recordBtn.disabled = true;
                recordBtn.style.display = 'block';
                stopBtn.style.display = 'none';

                submitAnswer(audioBlob, responseTime);
            });

            mediaRecorder.start();

            // Update UI to show recording state
            recordBtn.innerHTML = '<span class="flex items-center justify-center"><div class="animate-pulse w-3 h-3 bg-red-500 rounded-full mr-2"></div>Recording...</span>';
            recordBtn.className = 'w-full sm:w-auto px-6 py-3 font-bold text-white bg-red-500 dark:bg-red-600 rounded-lg shadow-md dark:shadow-lg transition duration-300 cursor-not-allowed';
            recordBtn.disabled = true;
            recordBtn.style.display = 'block';

            // Show stop button
            stopBtn.innerHTML = '<span class="flex items-center justify-center"><svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><rect x="6" y="6" width="8" height="8"></rect></svg>Stop Recording</span>';
            stopBtn.className = 'w-full sm:w-auto px-6 py-3 font-bold text-white bg-red-600 dark:bg-red-700 hover:bg-red-700 dark:hover:bg-red-800 rounded-lg shadow-md dark:shadow-lg transition duration-300 animate-pulse';
            stopBtn.disabled = false;
            stopBtn.style.display = 'block';

            console.log('Stop button should now be visible:', stopBtn.style.display);
            console.log('Stop button element:', stopBtn);

        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check your permissions.');
        }
    });

    stopBtn.addEventListener('click', () => {
        console.log('Stop button clicked');
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
    });

    const submitAnswer = async (audioBlob, responseTime) => {
        const question = quizState.questions[quizState.currentQuestionIndex];
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');
        formData.append('reference_answer_b64', btoa(question.answer));
        formData.append('response_time', responseTime);

        try {
            const response = await fetch('/api/submit-answer', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.statusText}`);
            }

            const result = await response.json();

            // Debug logging to verify response time is being captured
            console.log('Response received:', result);
            console.log('Response time captured:', result.response_time);

            quizState.results.push({
                question_text: question.question,
                transcribed_text: result.transcribed_text,
                score: result.score,
                response_time: result.response_time,
                reference_answer: result.reference_answer
            });
            sessionStorage.setItem('quizState', JSON.stringify(quizState));
            displayResult(result);

        } catch (error) {
            console.error('Error submitting answer:', error);
            resultDiv.textContent = 'Failed to evaluate your answer. Please try again.';
            resultDiv.style.display = 'block';
        }
    };

    const displayResult = (result) => {
        transcribedTextElem.textContent = `You said: ${result.transcribed_text}`;
        scoreElem.textContent = `Score: ${result.score}/100`;
        feedbackElem.textContent = `Feedback: ${result.feedback}`;

        // Add response time display
        const responseTimeElem = document.getElementById('response-time');
        if (responseTimeElem) {
            responseTimeElem.textContent = `Response Time: ${(result.response_time || 0).toFixed(1)}s`;
            responseTimeElem.style.display = 'block';
        }

        resultDiv.style.display = 'block';

        setTimeout(() => {
            loadNextQuestion();
        }, 3000); // 3 second delay before loading next question
    };

    const loadNextQuestion = () => {
        // Reset image display for next question
        questionImage.style.display = 'block';

        // Remove any existing countdown timer
        const existingCountdown = document.getElementById('countdown-timer');
        if (existingCountdown) {
            existingCountdown.remove();
        }

        quizState.currentQuestionIndex++;
        if (quizState.currentQuestionIndex < quizState.questions.length) {
            displayQuestion();
        } else {
            summarizeQuiz();
        }
    };

    if (nextQuestionBtn) {
        nextQuestionBtn.addEventListener('click', loadNextQuestion);
    }

    const summarizeQuiz = async () => {
        try {
            // Ensure all results have response_time field for backward compatibility
            const resultsWithResponseTime = quizState.results.map(result => ({
                question_text: result.question_text,
                transcribed_text: result.transcribed_text,
                score: result.score,
                response_time: result.response_time || 0, // Default to 0 if missing
                reference_answer: result.reference_answer
            }));

            // Debug logging to verify response times are included
            console.log('Quiz results being sent to summary:', resultsWithResponseTime);
            console.log('Response times:', resultsWithResponseTime.map(r => r.response_time));

            const response = await fetch('/api/summarize-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ results: resultsWithResponseTime })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Summary API error:', errorData);
                throw new Error(`Server error: ${response.statusText}`);
            }

            const summary = await response.json();

            // Debug logging to verify summary data
            console.log('Summary received from API:', summary);
            console.log('Summary results with response times:', summary.results);

            displaySummary(summary);

        } catch (error) {
            console.error('Error summarizing quiz:', error);
            summaryDiv.innerHTML = `
                <div class="text-center p-6">
                    <h2 class="text-xl sm:text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">Quiz Complete!</h2>
                    <p class="text-red-600 dark:text-red-400 mb-4">Failed to generate detailed summary, but here are your results:</p>
                    <div class="space-y-4">
                        ${quizState.results.map((result, index) => `
                            <div class="p-4 sm:p-5 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm">
                                <div class="flex justify-between items-center mb-3">
                                    <h4 class="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-100">Question ${index + 1}</h4>
                                    <div class="flex items-center space-x-4">
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${result.score >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : result.score >= 60 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}">
                                            ${result.score}/100
                                        </span>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                            ⏱️ ${(result.response_time || 0).toFixed(1)}s
                                        </span>
                                    </div>
                                </div>
                                <div class="space-y-2">
                                    <div class="text-sm sm:text-base">
                                        <strong class="text-gray-800 dark:text-gray-100">Question:</strong>
                                        <span class="text-gray-700 dark:text-gray-300 break-words">${result.question_text}</span>
                                    </div>
                                    <div class="text-sm sm:text-base">
                                        <strong class="text-gray-800 dark:text-gray-100">Your Answer:</strong>
                                        <span class="text-gray-700 dark:text-gray-300 break-words italic">"${result.transcribed_text}"</span>
                                    </div>
                                    <div class="text-sm sm:text-base">
                                        <strong class="text-gray-800 dark:text-gray-100">Correct Answer:</strong>
                                        <span class="text-gray-700 dark:text-gray-300 break-words">${result.reference_answer}</span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            summaryDiv.style.display = 'block';
            if (newQuizSection) {
                newQuizSection.style.display = 'block';
            }
        }
    };

    const displaySummary = (summary) => {
        quizContainer.style.display = 'none';
        summaryDiv.innerHTML = `
            <h2 class="text-xl sm:text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">Quiz Complete!</h2>
            <h3 class="text-xl sm:text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Summary</h3>
            <p class="mb-4 text-sm sm:text-base text-gray-700 dark:text-gray-300">${summary.summary}</p>
            <h3 class="text-xl sm:text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Your Results</h3>
            <div class="space-y-4">
                ${summary.results.map((result, index) => `
                    <div class="p-4 sm:p-5 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 shadow-sm">
                        <div class="flex justify-between items-center mb-3">
                            <h4 class="text-base sm:text-lg font-semibold text-gray-800 dark:text-gray-100">Question ${index + 1}</h4>
                            <div class="flex items-center space-x-4">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${result.score >= 80 ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : result.score >= 60 ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}">
                                    ${result.score}/100
                                </span>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                                    ⏱️ ${(result.response_time || 0).toFixed(1)}s
                                </span>
                            </div>
                        </div>
                        <div class="space-y-2">
                            <div class="text-sm sm:text-base">
                                <strong class="text-gray-800 dark:text-gray-100">Question:</strong>
                                <span class="text-gray-700 dark:text-gray-300 break-words">${result.question_text}</span>
                            </div>
                            <div class="text-sm sm:text-base">
                                <strong class="text-gray-800 dark:text-gray-100">Your Answer:</strong>
                                <span class="text-gray-700 dark:text-gray-300 break-words italic">"${result.transcribed_text}"</span>
                            </div>
                            <div class="text-sm sm:text-base">
                                <strong class="text-gray-800 dark:text-gray-100">Correct Answer:</strong>
                                <span class="text-gray-700 dark:text-gray-300 break-words">${result.reference_answer}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
                <h4 class="text-xl sm:text-2xl font-semibold text-blue-800 dark:text-blue-100 text-center mb-2">Quiz Statistics</h4>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm sm:text-base">
                    <div class="text-center text-lg">
                        <span class="font-medium text-blue-700 dark:text-blue-200">Average Score:</span>
                        <span class="text-blue-800 dark:text-blue-100 font-bold">${summary.average_score.toFixed(2)}/100</span>
                    </div>
                    <div class="text-center text-lg">
                        <span class="font-medium text-blue-700 dark:text-blue-200">Average Response Time:</span>
                        <span class="text-blue-800 dark:text-blue-100 font-bold">${(summary.average_response_time || 0).toFixed(2)}s</span>
                    </div>
                    <div class="text-center text-lg">
                        <span class="font-medium text-blue-700 dark:text-blue-200">Total Time:</span>
                        <span class="text-blue-800 dark:text-blue-100 font-bold">${(summary.results.reduce((acc, r) => acc + (r.response_time || 0), 0)).toFixed(2)}s</span>
                    </div>
                </div>
            </div>
        `;
        summaryDiv.style.display = 'block';
        if (newQuizSection) {
            newQuizSection.style.display = 'block';
        }

        // Scroll to summary on mobile
        if (window.innerWidth <= 640) {
            summaryDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    // Check for existing quiz state in sessionStorage
    const savedState = sessionStorage.getItem('quizState');
    if (savedState) {
        try {
            quizState = JSON.parse(savedState);

            // Ensure backward compatibility - add response_time to existing results if missing
            if (quizState.results) {
                quizState.results = quizState.results.map(result => ({
                    ...result,
                    response_time: result.response_time || 0
                }));
            }

            if (quizState.currentQuestionIndex < quizState.questions.length) {
                quizSetup.style.display = 'none';
                quizContainer.style.display = 'block';
                displayQuestion();
            } else {
                summarizeQuiz();
            }
        } catch (error) {
            console.error('Error parsing saved quiz state:', error);
            // Clear corrupted state and start fresh
            sessionStorage.removeItem('quizState');
            quizSetup.style.display = 'block';
            quizContainer.style.display = 'none';
            summaryDiv.style.display = 'none';
            if (newQuizSection) {
                newQuizSection.style.display = 'none';
            }
        }
    } else { // If no saved state, ensure quiz setup is visible
        quizSetup.style.display = 'block';
        quizContainer.style.display = 'none';
        summaryDiv.style.display = 'none';
        if (newQuizSection) {
            newQuizSection.style.display = 'none';
        }
    }
});