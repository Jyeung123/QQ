from flask import Flask, request, send_file, jsonify
import os
import io
import re
from html import escape
from bs4 import BeautifulSoup
from pathlib import Path

app = Flask(__name__)
print(f"Current working directory: {os.getcwd()}")

# --- Get user's Downloads path (Assumption!) ---
# This assumes a standard Windows Downloads folder location.
DOWNLOADS_PATH = Path.home() / "Downloads"
print(f"Assuming Downloads path: {DOWNLOADS_PATH}")

# HTML template as a string variable
CREATOR_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML Question Template Creator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #3498db;
            --primary-hover: #2980b9;
            --secondary-color: #6c757d;
            --success-color: #2ecc71;
            --danger-color: #e74c3c;
            --border-color: #dee2e6;
            --light-bg: #f8f9fa;
            --dark-bg: #212529;
            --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            --hover-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }

        body {
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            background-color: #f9fbfd;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
        }

        .section {
            margin-bottom: 24px;
            padding: 24px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background-color: #ffffff;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
        }

        .section:hover {
            box-shadow: var(--hover-shadow);
        }

        h2 {
            margin-bottom: 30px;
            color: var(--dark-bg);
            font-weight: 700;
            text-align: center;
            position: relative;
            padding-bottom: 12px;
        }

        h2:after {
            content: '';
            position: absolute;
            width: 60px;
            height: 3px;
            background-color: var(--primary-color);
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
        }

        h4 {
            color: var(--primary-color);
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }

        .question-config {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            position: relative;
            background-color: var(--light-bg);
            transition: all 0.2s ease-in-out;
        }

        .question-config:hover {
            box-shadow: var(--card-shadow);
        }

        .sample-config {
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background-color: white;
            position: relative;
            box-shadow: var(--card-shadow);
            transition: all 0.3s ease;
        }

        .sample-config:hover {
            box-shadow: var(--hover-shadow);
            transform: translateY(-2px);
        }

        .btn-remove-sample {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 18px;
            color: var(--danger-color);
            background: none;
            border: none;
            cursor: pointer;
            z-index: 10;
            transition: transform 0.2s, color 0.2s;
            opacity: 0.7;
        }

        .btn-remove-sample:hover {
            transform: scale(1.2);
            opacity: 1;
        }

        .sample-move-buttons {
            display: inline-flex;
            gap: 2px;
            margin-left: 8px; /* Space between title and buttons */
            vertical-align: middle;
        }

        .btn-move-sample {
            font-size: 1.1rem;
            line-height: 1;
            color: var(--secondary-color);
            opacity: 0.7;
            transition: opacity 0.2s, color 0.2s;
        }

        .btn-move-sample:hover {
            color: var(--primary-color);
            opacity: 1;
        }

        .btn-move-sample:disabled {
            opacity: 0.2;
            cursor: not-allowed;
            color: var(--secondary-color);
        }

        .sample-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-right: 30px;
        }

        .btn-add-sample {
            margin-top: 10px;
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            font-size: 0.9rem;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .btn-add-sample:hover {
            background-color: var(--primary-hover);
            border-color: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .action-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 30px;
        }

        .action-buttons button {
            padding: 12px 30px;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s;
        }

        .action-buttons button:hover {
            transform: translateY(-3px);
            box-shadow: var(--hover-shadow);
        }

        .eval-input {
            width: 80px;
            display: inline-block;
            margin-left: 8px;
            margin-right: 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            padding: 6px 12px;
        }

        .type-eval-container {
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .type-container, .eval-container {
            display: flex;
            align-items: center;
        }

        .type-select {
            width: 150px;
            margin-left: 8px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            background-color: white;
        }

        .form-control, .form-select {
            border-radius: 8px;
            border: 1px solid var(--border-color);
            padding: 10px 14px;
            transition: all 0.2s ease-in-out;
            box-shadow: none;
        }

        .form-control:focus, .form-select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 0.25rem rgba(52, 152, 219, 0.25);
        }

        textarea.form-control {
            min-height: 120px;
            line-height: 1.6;
            font-size: 0.95rem;
            /* No resize - we'll handle it with custom controls */
            resize: none;
        }

        .textarea-container {
            position: relative;
            margin-bottom: 15px;
        }

        .resize-handle {
            display: block;
            height: 10px;
            background-color: #f0f0f0;
            border-radius: 0 0 4px 4px;
            cursor: ns-resize;
            position: relative;
            border: 1px solid #dee2e6;
            border-top: none;
            user-select: none;
        }

        .resize-handle:hover, .resize-handle.active {
            background-color: #d0d0d0;
        }

        .resize-handle::after {
            content: '';
            display: block;
            width: 20px;
            height: 3px;
            position: absolute;
            top: 3px;
            left: 50%;
            transform: translateX(-50%);
            background-image: linear-gradient(to right, #aaa 1px, transparent 1px);
            background-size: 4px 100%;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .import-container {
            display: flex;
            align-items: center;
        }

        #importFile {
            display: none;
        }

        .import-label {
            margin-bottom: 0;
            cursor: pointer;
            color: var(--primary-color);
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            border: 1px solid var(--primary-color);
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .import-label:hover {
            background-color: rgba(52, 152, 219, 0.1);
        }

        .import-status {
            margin-left: 12px;
            font-size: 0.9rem;
            font-weight: 500;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .import-status.success {
            color: var(--success-color);
        }

        .import-status.error {
            color: var(--danger-color);
        }

        .import-status.visible {
            opacity: 1;
        }

        .ocr-name-fields {
            display: flex;
            gap: 15px;
        }

        .ocr-name-fields .form-control {
            flex: 1;
        }

        .form-label {
            font-weight: 500;
            color: #555;
            margin-bottom: 8px;
        }

        h5 {
            color: #444;
            font-weight: 600;
            margin-bottom: 0;
        }

        .btn-outline-primary {
            border-color: var(--primary-color);
            color: var(--primary-color);
        }

        .btn-outline-primary:hover {
            background-color: var(--primary-color);
            color: white;
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .btn-primary:hover {
            background-color: var(--primary-hover);
            border-color: var(--primary-hover);
        }

        .btn-secondary {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }

        @media (max-width: 768px) {
            .type-eval-container {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }

            .action-buttons {
                flex-direction: column;
                gap: 15px;
            }

            .action-buttons button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Sample Answer HTML</h2>

        <form id="templateForm" action="/" method="post">
            <div class="section">
                <div class="section-header">
                    <h4>Basic Configuration</h4>
                    <div class="import-container">
                        <span id="importStatus" class="import-status"></span>
                        <label for="importFile" class="import-label">
                            <i class="bi bi-file-earmark-arrow-up"></i> Import HTML
                        </label>
                        <input class="form-control" type="file" id="importFile" accept=".html">
                    </div>
                </div>

                <div class="mb-3">
                    <label for="filename" class="form-label">HTML File Name</label>
                    <input type="text" class="form-control" id="filename" name="filename" required>
                </div>

                <div class="mb-3">
                    <label for="question_type" class="form-label">Default Question Type</label>
                    <select class="form-select" id="question_type" name="question_type" required onchange="updateQuestionType()">
                        <option value="short">Short Answer</option>
                        <option value="long">Long Answer</option>
                        <option value="math pure">Math (Pure)</option>
                        <option value="math mixed">Math (Mixed)</option>
                        <option value="custom">Custom (Mixed Types)</option>
                    </select>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="num_questions" class="form-label">Number of Questions</label>
                        <input type="number" class="form-control" id="num_questions" name="num_questions" min="1" value="1" required onchange="updateQuestions()">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="samples_per_question" class="form-label">Initial Samples per Question</label>
                        <div class="input-group">
                            <input type="number" class="form-control" id="samples_per_question" name="samples_per_question" min="1" value="1" required onchange="updateQuestions()">
                            <button class="btn btn-outline-secondary" type="button" id="samplesLockBtn" title="When locked, changes only affect new questions. When unlocked, changes affect all current questions.">
                                <i class="bi bi-lock-fill" id="samplesLockIcon"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <div class="mb-3">
                    <label for="num_ocr_samples" class="form-label">Number of OCR Sample Images</label>
                    <input type="number" class="form-control" id="num_ocr_samples" name="num_ocr_samples" min="0" value="0" required onchange="updateOCRSamples()">
                </div>
                <div id="ocr_samples_container">
                    <!-- Generated image name inputs here -->
                </div>
            </div>

            <div class="section">
                <h4>Sample Answers</h4>
                <div id="answers_container">
                    <!-- Dynamically generated based on question type, number of questions, and samples -->
                </div>
            </div>

            <div class="text-center mt-4 action-buttons">
                <button type="button" id="previewButton" class="btn btn-secondary btn-lg">Preview</button>
                <button type="submit" class="btn btn-primary btn-lg">Generate HTML</button>
            </div>
        </form>
    </div>

    <script>
        // Global variables to track dynamic elements
        let questionSampleCounts = {};
        let previewWindow = null;
        let sampleValues = {}; // To store all sample values when updating
        let samplesLocked = false; // Default to unlocked state
        let ocrValues = {}; // To store OCR sample values when updating

        // Import functionality - Auto import when file is selected
        document.getElementById('importFile').addEventListener('change', function() {
            if (this.files.length === 0) {
                return;
            }

            const file = this.files[0];
            const formData = new FormData();
            formData.append('html_file', file);

            // Show status as pending
            const statusElement = document.getElementById('importStatus');
            statusElement.className = 'import-status visible';
            statusElement.style.color = '#6c757d'; // Gray color for pending

            fetch('/import_html', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reset the form
                    sampleValues = {};
                    questionSampleCounts = {};
                    ocrValues = {}; // Clear OCR values for imported data

                    // Populate the form with the imported data
                    populateFormWithImportedData(data.data);

                    // Show success message
                    statusElement.className = 'import-status success visible';
                } else {
                    // Show error message
                    statusElement.textContent = data.error;
                    statusElement.className = 'import-status error visible';
                }

                // Hide the status message after 3 seconds
                setTimeout(() => {
                    statusElement.className = 'import-status';
                }, 3000);
            })
            .catch(error => {
                console.error('Error:', error);

                // Show error message
                statusElement.textContent = 'Import failed';
                statusElement.className = 'import-status error visible';

                // Hide the status message after 3 seconds
                setTimeout(() => {
                    statusElement.className = 'import-status';
                }, 3000);
            });
        });

        function populateFormWithImportedData(data) {
            // Set basic configuration
            document.getElementById('filename').value = data.filename;
            document.getElementById('question_type').value = data.question_type;
            document.getElementById('num_questions').value = data.num_questions;

            // Set OCR samples
            const ocrFiles = data.ocr_files || [];
            const ocrDisplays = data.ocr_displays || [];
            document.getElementById('num_ocr_samples').value = ocrFiles.length;
            updateOCRSamples();

            // Fill OCR image names
            for (let i = 0; i < ocrFiles.length; i++) {
                const fileField = document.getElementById(`ocr_file_${i+1}`);
                const displayField = document.getElementById(`ocr_display_${i+1}`);

                if (fileField) {
                    fileField.value = ocrFiles[i];
                    ocrValues[`ocr_file_${i+1}`] = ocrFiles[i];
                }

                if (displayField) {
                    displayField.value = ocrDisplays[i] || ocrFiles[i];
                    ocrValues[`ocr_display_${i+1}`] = ocrDisplays[i] || ocrFiles[i];
                }
            }

            // Determine maximum samples per question for initial setup
            let maxSamplesPerQuestion = 0;
            data.samples.forEach(questionSamples => {
                maxSamplesPerQuestion = Math.max(maxSamplesPerQuestion, questionSamples.length);
            });

            document.getElementById('samples_per_question').value = maxSamplesPerQuestion;

            // Update questions container with initial setup
            updateQuestions(true);

            // Now populate all the samples with the imported data
            data.samples.forEach((questionSamples, qIndex) => {
                const questionNum = qIndex + 1;

                // Store sample counts
                questionSampleCounts[questionNum] = questionSamples.length;

                // Clear existing samples for this question and add the correct number
                const samplesContainer = document.getElementById(`q${questionNum}_samples_container`);
                if (samplesContainer) {
                    samplesContainer.innerHTML = '';

                    questionSamples.forEach((sample, sIndex) => {
                        const sampleNum = sIndex + 1;
                        const sampleId = `q${questionNum}_s${sampleNum}`;

                        // Store sample values - ensure we have a valid type
                        // For individual samples, we never use 'custom' - use their actual type
                        const sampleType = sample.type || (data.question_type === 'custom' ? 'short' : data.question_type);
                        
                        sampleValues[`${sampleId}_answer`] = sample.answer;
                        sampleValues[`${sampleId}_eval`] = sample.evaluation;
                        sampleValues[`${sampleId}_type`] = sampleType;
                        if (sample.preview) {
                            sampleValues[`${sampleId}_preview`] = sample.preview;
                        }

                        // Create the sample div with the appropriate type
                        const sampleDiv = createSampleConfig(questionNum, sampleNum, sampleType);
                        samplesContainer.appendChild(sampleDiv);

                        // Update the newly created fields with the stored values
                        const typeSelect = document.getElementById(`${sampleId}_type`);
                        if (typeSelect) {
                            typeSelect.value = sampleType;
                        }
                        
                        document.getElementById(`${sampleId}_eval`).value = sample.evaluation;
                        document.getElementById(`${sampleId}_answer`).value = sample.answer;

                        // For types with preview fields, set the preview values
                        if ((sampleType === 'long' || sampleType === 'math mixed') && 
                            document.getElementById(`${sampleId}_preview`)) {
                            document.getElementById(`${sampleId}_preview`).value = sample.preview || '';
                        }

                        // Make sure the correct fields are shown based on the sample type
                        updateSampleFields(questionNum, sampleNum);
                    });
                    
                    // Update button states after adding samples for this question
                    updateMoveButtonStates(questionNum);
                }
            });

            // After successfully importing data, set the lock to locked
            samplesLocked = true;
            updateLockIcon();

            // Wrap textareas after population
            setTimeout(wrapTextareas, 0);
        }

        function updateOCRSamples() {
            const numSamplesInput = document.getElementById('num_ocr_samples');
            // Handle empty input - default to 0
            if (numSamplesInput.value === '') {
                numSamplesInput.value = '0';
            }

            // Store existing OCR sample values before updating
            storeOCRValues();

            const numSamples = parseInt(numSamplesInput.value) || 0;
            const container = document.getElementById('ocr_samples_container');
            container.innerHTML = '';
            for (let i = 1; i <= numSamples; i++) {
                const div = document.createElement('div');
                div.className = 'mb-2';
                div.innerHTML = `
                    <label for="ocr_display_${i}" class="form-label">Image ${i}</label>
                    <div class="ocr-name-fields">
                        <input type="text" class="form-control" id="ocr_display_${i}" name="ocr_display_${i}" 
                               placeholder="Display name" required>
                        <input type="text" class="form-control" id="ocr_file_${i}" name="ocr_file_${i}" 
                               placeholder="File name (without extension)" required>
                    </div>
                `;
                container.appendChild(div);
            }

            // Restore OCR sample values after updating
            restoreOCRValues();
        }

        // Store OCR sample values
        function storeOCRValues() {
            const numSamples = parseInt(document.getElementById('num_ocr_samples').value) || 0;
            for (let i = 1; i <= numSamples; i++) {
                const fileField = document.getElementById(`ocr_file_${i}`);
                const displayField = document.getElementById(`ocr_display_${i}`);
                
                if (fileField) {
                    ocrValues[`ocr_file_${i}`] = fileField.value;
                }
                
                if (displayField) {
                    ocrValues[`ocr_display_${i}`] = displayField.value;
                }
            }
        }

        // Restore OCR sample values
        function restoreOCRValues() {
            const numSamples = parseInt(document.getElementById('num_ocr_samples').value) || 0;
            for (let i = 1; i <= numSamples; i++) {
                const fileField = document.getElementById(`ocr_file_${i}`);
                const displayField = document.getElementById(`ocr_display_${i}`);
                
                if (fileField && ocrValues[`ocr_file_${i}`]) {
                    fileField.value = ocrValues[`ocr_file_${i}`];
                }
                
                if (displayField && ocrValues[`ocr_display_${i}`]) {
                    displayField.value = ocrValues[`ocr_display_${i}`];
                }
            }
        }

        // Format evaluation score to always have decimal point
        function formatEvalScore(value) {
            if (value === '') return '';

            // Parse as float and format with 1 decimal place if needed
            const num = parseFloat(value);
            if (isNaN(num)) return '';

            // Check if the number already has a decimal part
            if (Math.floor(num) === num) {
                return num.toFixed(1); // Add .0 to whole numbers
            }
            return num.toString(); // Keep as is if already has decimals
        }

        function createSampleConfig(questionNum, sampleNum, questionType) {
            // Generate unique ID for this sample
            const sampleId = `q${questionNum}_s${sampleNum}`;

            const sampleDiv = document.createElement('div');
            sampleDiv.className = 'sample-config';
            sampleDiv.id = `${sampleId}_container`;

            // Get stored values if they exist
            const storedAnswer = sampleValues[`${sampleId}_answer`] || '';
            const storedEval = sampleValues[`${sampleId}_eval`] || '';
            const storedPreview = sampleValues[`${sampleId}_preview`] || '';
            const storedType = sampleValues[`${sampleId}_type`] || questionType;

            let sampleContent = `
                <button type="button" class="btn-remove-sample" onclick="removeSample(${questionNum}, ${sampleNum})">
                    <i class="bi bi-x-circle-fill"></i>
                </button>
                <div class="sample-header">
                    <div class="d-flex align-items-center">
                        <h5>Sample ${sampleNum}</h5>
                        <div class="sample-move-buttons">
                             <button type="button" class="btn btn-sm btn-outline-secondary p-0 border-0 btn-move-sample" 
                                     id="${sampleId}_move_up" onclick="moveSampleUp(${questionNum}, ${sampleNum})" title="Move Up">
                                 <i class="bi bi-arrow-up-circle"></i>
                             </button>
                             <button type="button" class="btn btn-sm btn-outline-secondary p-0 border-0 btn-move-sample" 
                                     id="${sampleId}_move_down" onclick="moveSampleDown(${questionNum}, ${sampleNum})" title="Move Down">
                                 <i class="bi bi-arrow-down-circle"></i>
                             </button>
                        </div>
                    </div>
                    <div class="type-eval-container">
                        <div class="type-container">
                            <label for="${sampleId}_type" class="form-label small mb-0">Question Type:</label>
                            <select class="form-select form-select-sm type-select" 
                                    id="${sampleId}_type" 
                                    name="${sampleId}_type" 
                                    onchange="updateSampleFields(${questionNum}, ${sampleNum})">
                                <option value="short" ${storedType === 'short' ? 'selected' : ''}>Short Answer</option>
                                <option value="long" ${storedType === 'long' ? 'selected' : ''}>Long Answer</option>
                                <option value="math pure" ${storedType === 'math pure' ? 'selected' : ''}>Math (Pure)</option>
                                <option value="math mixed" ${storedType === 'math mixed' ? 'selected' : ''}>Math (Mixed)</option>
                            </select>
                        </div>
                        <div class="eval-container">
                            <label for="${sampleId}_eval" class="form-label small mb-0">Score:</label>
                            <input type="text" class="form-control form-control-sm eval-input" 
                                   id="${sampleId}_eval" 
                                   name="${sampleId}_eval" 
                                   value="${storedEval}"
                                   onblur="formatEvalField(this)"
                                   required>
                        </div>
                    </div>
                </div>
                <div id="${sampleId}_fields">
            `;

            // Add appropriate fields based on the question type
            if (storedType === 'long') {
                sampleContent += `
                    <div class="mb-3">
                        <label for="${sampleId}_preview" class="form-label">Preview Answer</label>
                        <textarea class="form-control" id="${sampleId}_preview" 
                                name="${sampleId}_preview" rows="2" required>${storedPreview}</textarea>
                    </div>
                `;
            }

            sampleContent += `
                    <div class="mb-3">
                        <label for="${sampleId}_answer" class="form-label">Sample Answer</label>
                        <textarea class="form-control" id="${sampleId}_answer" 
                                name="${sampleId}_answer" rows="4" required>${storedAnswer}</textarea>
                    </div>
                </div>
            `;

            sampleDiv.innerHTML = sampleContent;
            
            // Wait a tick for the DOM to update, then wrap textareas
            setTimeout(wrapTextareas, 0);
            
            return sampleDiv;
        }

        function updateSampleFields(questionNum, sampleNum) {
            const sampleId = `q${questionNum}_s${sampleNum}`;
            const sampleType = document.getElementById(`${sampleId}_type`).value;
            const fieldsContainer = document.getElementById(`${sampleId}_fields`);

            // Store current answer value before updating fields
            const answerField = document.getElementById(`${sampleId}_answer`);
            if (answerField) {
                sampleValues[`${sampleId}_answer`] = answerField.value;
            }

            // Store evaluation score
            const evalField = document.getElementById(`${sampleId}_eval`);
            if (evalField) {
                sampleValues[`${sampleId}_eval`] = evalField.value;
            }

            // Store preview if it exists (for long answers or math mixed)
            const previewField = document.getElementById(`${sampleId}_preview`);
            if (previewField) {
                sampleValues[`${sampleId}_preview`] = previewField.value;
            }

            // Store selected type
            sampleValues[`${sampleId}_type`] = sampleType;

            let fieldsHtml = '';

            // Add preview field for long answer and math mixed types
            if (sampleType === 'long' || sampleType === 'math mixed') {
                const previewValue = sampleValues[`${sampleId}_preview`] || '';
                fieldsHtml += `
                    <div class="mb-3">
                        <label for="${sampleId}_preview" class="form-label">Preview Answer</label>
                        <textarea class="form-control" id="${sampleId}_preview" 
                                name="${sampleId}_preview" rows="2" required>${previewValue}</textarea>
                    </div>
                `;
            }

            // Add answer field for all types
            const answerValue = sampleValues[`${sampleId}_answer`] || '';
            
            // For math types, add a different label to clarify the format
            let answerLabel = 'Sample Answer';
            let helperText = '';
            
            if (sampleType === 'math pure') {
                answerLabel = 'Sample Answer';
                helperText = '<small class="form-text text-muted">Enter LaTeX formulas without dollar signs. For example: "x^2 + y^2 = r^2" or "\\frac{a}{b} + c"</small>';
            } else if (sampleType === 'math mixed') {
                answerLabel = 'Sample Answer';
                helperText = '<small class="form-text text-muted">Use $...$ for inline math and $$...$$ for display math. Example: "The area of a circle is $A = \\pi r^2$."</small>';
            }
            
            fieldsHtml += `
                <div class="mb-3">
                    <label for="${sampleId}_answer" class="form-label">${answerLabel}</label>
                    <textarea class="form-control" id="${sampleId}_answer" 
                            name="${sampleId}_answer" rows="4" required>${answerValue}</textarea>
                </div>
            `;

            fieldsContainer.innerHTML = fieldsHtml;
            
            // Wrap new textareas
            setTimeout(wrapTextareas, 0);
        }

        function addSample(questionNum) {
            const samplesContainer = document.getElementById(`q${questionNum}_samples_container`);
            const questionType = document.getElementById('question_type').value;

            // Increment the sample count for this question
            if (!questionSampleCounts[questionNum]) {
                questionSampleCounts[questionNum] = 0;
            }

            // Get current visual samples to determine the next sample number
            const sampleContainers = samplesContainer.querySelectorAll('.sample-config');
            const nextSampleNum = sampleContainers.length + 1;

            questionSampleCounts[questionNum] = nextSampleNum;

            const sampleDiv = createSampleConfig(questionNum, nextSampleNum, questionType);
            samplesContainer.appendChild(sampleDiv);
            
            // Update button states for this question
            updateMoveButtonStates(questionNum);
        }

        function removeSample(questionNum, sampleNum) {
            const sampleDiv = document.getElementById(`q${questionNum}_s${sampleNum}_container`);
            if (sampleDiv) {
                // Check if this is the last sample
                const samplesContainer = document.getElementById(`q${questionNum}_samples_container`);
                if (samplesContainer.children.length <= 1) {
                    alert("Cannot remove the last sample. Each question must have at least one sample.");
                    return;
                }

                // Store sample values before removal
                const sampleId = `q${questionNum}_s${sampleNum}`;
                const answerField = document.getElementById(`${sampleId}_answer`);
                if (answerField) {
                    sampleValues[`${sampleId}_answer`] = answerField.value;
                }

                const evalField = document.getElementById(`${sampleId}_eval`);
                if (evalField) {
                    sampleValues[`${sampleId}_eval`] = evalField.value;
                }

                const previewField = document.getElementById(`${sampleId}_preview`);
                if (previewField) {
                    sampleValues[`${sampleId}_preview`] = previewField.value;
                }

                const typeField = document.getElementById(`${sampleId}_type`);
                if (typeField) {
                    sampleValues[`${sampleId}_type`] = typeField.value;
                }

                sampleDiv.remove();

                // Renumber the samples after removal
                reorderSamples(questionNum);
            }
        }

        // Function to reorder sample numbers after deletion
        function reorderSamples(questionNum) {
            const samplesContainer = document.getElementById(`q${questionNum}_samples_container`);
            const sampleDivs = samplesContainer.querySelectorAll('.sample-config');

            sampleDivs.forEach((div, index) => {
                const newSampleNum = index + 1;
                const oldId = div.id;
                const oldSampleNum = parseInt(oldId.split('_s')[1].split('_')[0]);

                if (oldSampleNum !== newSampleNum) {
                    // Update the sample header number
                    const headerElement = div.querySelector('h5');
                    if (headerElement) {
                        headerElement.textContent = `Sample ${newSampleNum}`;
                    }

                    // Create new IDs for form elements
                    const oldSampleId = `q${questionNum}_s${oldSampleNum}`;
                    const newSampleId = `q${questionNum}_s${newSampleNum}`;

                    // Update DIV ID
                    div.id = `${newSampleId}_container`;

                    // Update field IDs and names
                    const formElements = div.querySelectorAll('[id^="' + oldSampleId + '"]');
                    formElements.forEach(element => {
                        const oldElementId = element.id;
                        const suffix = oldElementId.substring(oldSampleId.length);
                        const newElementId = newSampleId + suffix;

                        // Update element ID
                        element.id = newElementId;

                        // Update element name if it's a form input
                        if (element.name) {
                            element.name = newElementId;
                        }

                        // Update any labels targeting this element
                        const labels = div.querySelectorAll(`label[for="${oldElementId}"]`);
                        labels.forEach(label => {
                            label.setAttribute('for', newElementId);
                        });
                    });

                    // Update onclick attributes for buttons
                    const removeButton = div.querySelector('.btn-remove-sample');
                    if (removeButton) {
                        removeButton.setAttribute('onclick', `removeSample(${questionNum}, ${newSampleNum})`);
                    }
                    
                    // Update onclick for move buttons
                    const moveUpButton = div.querySelector('.btn-move-sample[id$="_move_up"]');
                    if (moveUpButton) {
                        moveUpButton.id = `${newSampleId}_move_up`; // Update ID too
                        moveUpButton.setAttribute('onclick', `moveSampleUp(${questionNum}, ${newSampleNum})`);
                    }
                    const moveDownButton = div.querySelector('.btn-move-sample[id$="_move_down"]');
                    if (moveDownButton) {
                        moveDownButton.id = `${newSampleId}_move_down`; // Update ID too
                        moveDownButton.setAttribute('onclick', `moveSampleDown(${questionNum}, ${newSampleNum})`);
                    }

                    // Move stored values to new keys
                    if (sampleValues[`${oldSampleId}_answer`] !== undefined) {
                        sampleValues[`${newSampleId}_answer`] = sampleValues[`${oldSampleId}_answer`];
                    }
                    if (sampleValues[`${oldSampleId}_eval`] !== undefined) {
                        sampleValues[`${newSampleId}_eval`] = sampleValues[`${oldSampleId}_eval`];
                    }
                    if (sampleValues[`${oldSampleId}_preview`] !== undefined) {
                        sampleValues[`${newSampleId}_preview`] = sampleValues[`${oldSampleId}_preview`];
                    }
                    if (sampleValues[`${oldSampleId}_type`] !== undefined) {
                        sampleValues[`${newSampleId}_type`] = sampleValues[`${oldSampleId}_type`];
                    }
                }
            });

            // Update the question's sample count
            questionSampleCounts[questionNum] = sampleDivs.length;
            
            // Update button states after reordering
            updateMoveButtonStates(questionNum);
        }

        // --- Add functions for moving samples ---
        function moveSampleUp(questionNum, sampleNum) {
            const sampleDiv = document.getElementById(`q${questionNum}_s${sampleNum}_container`);
            const previousSampleDiv = sampleDiv.previousElementSibling;

            if (previousSampleDiv) {
                // Store values before moving
                storeAllSampleValues();
                
                // Move the element
                sampleDiv.parentNode.insertBefore(sampleDiv, previousSampleDiv);
                
                // Reorder and update button states
                reorderSamples(questionNum);
            }
        }

        function moveSampleDown(questionNum, sampleNum) {
            const sampleDiv = document.getElementById(`q${questionNum}_s${sampleNum}_container`);
            const nextSampleDiv = sampleDiv.nextElementSibling;

            if (nextSampleDiv) {
                // Store values before moving
                storeAllSampleValues();
                
                // Move the element
                sampleDiv.parentNode.insertBefore(nextSampleDiv, sampleDiv);
                
                // Reorder and update button states
                reorderSamples(questionNum);
            }
        }

        // --- Function to update Move Up/Down button states ---
        function updateMoveButtonStates(questionNum) {
            const samplesContainer = document.getElementById(`q${questionNum}_samples_container`);
            if (!samplesContainer) return;
            
            const sampleDivs = samplesContainer.querySelectorAll('.sample-config');
            const totalSamples = sampleDivs.length;

            sampleDivs.forEach((div, index) => {
                const sampleNum = index + 1; // Current visual index
                const sampleId = `q${questionNum}_s${sampleNum}`;
                
                const upButton = document.getElementById(`${sampleId}_move_up`);
                const downButton = document.getElementById(`${sampleId}_move_down`);

                if (upButton) {
                    upButton.disabled = (sampleNum === 1);
                }
                if (downButton) {
                    downButton.disabled = (sampleNum === totalSamples);
                }
            });
        }
        // --- End of new functions ---

        function updateQuestionType() {
            // Store all current values
            storeAllSampleValues();

            // Get the new question type
            const newQuestionType = document.getElementById('question_type').value;
            
            // If custom type is selected, don't change individual sample types
            if (newQuestionType === 'custom') {
                return;
            }

            // Update all sample type selects to match the new default type
            const typeSelects = document.querySelectorAll('select[id$="_type"]');
            typeSelects.forEach(select => {
                // Update the select value
                select.value = newQuestionType;

                // Also update the stored value in sampleValues
                if (select.id) {
                    sampleValues[select.id] = newQuestionType;

                    // Get the question and sample numbers from the ID
                    const idParts = select.id.match(/q(\d+)_s(\d+)_type/);
                    if (idParts && idParts.length === 3) {
                        const qNum = parseInt(idParts[1]);
                        const sNum = parseInt(idParts[2]);

                        // Update the sample fields to match the new type
                        updateSampleFields(qNum, sNum);
                    }
                }
            });
        }

        function storeAllSampleValues() {
            // Get all questions
            const numQuestions = parseInt(document.getElementById('num_questions').value) || 0;
            
            for (let q = 1; q <= numQuestions; q++) {
                // Get all sample containers for this question
                const samplesContainer = document.getElementById(`q${q}_samples_container`);
                if (!samplesContainer) continue;
                
                const sampleContainers = samplesContainer.querySelectorAll('.sample-config');
                
                // Store the current count of samples for this question
                questionSampleCounts[q] = sampleContainers.length;
                
                // Store values for each sample
                sampleContainers.forEach((container, index) => {
                    const sampleNum = index + 1;
                    const sampleId = `q${q}_s${sampleNum}`;
                    
                    // Store answer value
                    const answerField = document.getElementById(`${sampleId}_answer`);
                    if (answerField) {
                        sampleValues[`${sampleId}_answer`] = answerField.value;
                    }
                    
                    // Store evaluation score
                    const evalField = document.getElementById(`${sampleId}_eval`);
                    if (evalField) {
                        sampleValues[`${sampleId}_eval`] = evalField.value;
                    }
                    
                    // Store preview if it exists (for long answers)
                    const previewField = document.getElementById(`${sampleId}_preview`);
                    if (previewField) {
                        sampleValues[`${sampleId}_preview`] = previewField.value;
                    }
                    
                    // Store question type
                    const typeField = document.getElementById(`${sampleId}_type`);
                    if (typeField) {
                        sampleValues[`${sampleId}_type`] = typeField.value;
                    }
                });
            }
        }

        function updateQuestions(resetSamples = false) {
            if (!resetSamples) {
                // Store all current values before updating
                storeAllSampleValues();
            } else {
                // Clear all stored values if resetting
                sampleValues = {};
            }

            const questionType = document.getElementById('question_type').value;
            const numQuestions = parseInt(document.getElementById('num_questions').value) || 0;
            const samplesPerQuestion = parseInt(document.getElementById('samples_per_question').value) || 0;
            const container = document.getElementById('answers_container');
            container.innerHTML = '';

            // Reset sample counts if needed
            if (resetSamples) {
                questionSampleCounts = {};
            }

            for (let q = 1; q <= numQuestions; q++) {
                // Create question container
                const questionDiv = document.createElement('div');
                questionDiv.className = 'question-config mb-3';
                questionDiv.id = `question_${q}_config`;

                // Add question header and samples container
                questionDiv.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5>Question ${q}</h5>
                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="addSample(${q})">
                            <i class="bi bi-plus-circle"></i> Add Sample
                        </button>
                    </div>
                    <div id="q${q}_samples_container"></div>
                `;

                container.appendChild(questionDiv);

                // Add samples
                const samplesContainer = document.getElementById(`q${q}_samples_container`);
                
                // Determine how many samples to add
                if (!resetSamples) {
                    // If not resetting, use existing count or apply new count based on lock state
                    if (!questionSampleCounts[q]) {
                        // New question - always use samplesPerQuestion
                        questionSampleCounts[q] = samplesPerQuestion;
                    } else if (!samplesLocked) {
                        // Unlocked - update all questions to new count
                        questionSampleCounts[q] = samplesPerQuestion;
                    }
                    // If locked and count exists, keep the existing count
                } else {
                    // For initial setup, use the specified number
                    questionSampleCounts[q] = samplesPerQuestion;
                }

                for (let s = 1; s <= questionSampleCounts[q]; s++) {
                    const sampleDiv = createSampleConfig(q, s, questionType);
                    samplesContainer.appendChild(sampleDiv);
                }
                
                // Update button states for the newly added question
                updateMoveButtonStates(q);
            }
            
            // Ensure textareas are wrapped after the update
            setTimeout(wrapTextareas, 0);
        }

        function formatEvalField(field) {
            field.value = formatEvalScore(field.value);
            // Store the formatted value
            sampleValues[field.id] = field.value;
        }

        // Preview functionality
        document.getElementById('previewButton').addEventListener('click', function() {
            // Store current values
            storeAllSampleValues();

            // Collect form data
            const formData = new FormData(document.getElementById('templateForm'));
            const jsonData = {
                filename: formData.get('filename') || 'questions',
                question_type: formData.get('question_type'),
                num_questions: parseInt(formData.get('num_questions')) || 1,
                samples_per_question: parseInt(formData.get('samples_per_question')) || 1,
                num_ocr_samples: parseInt(formData.get('num_ocr_samples') || '0'),
                ocr_files: [],
                ocr_displays: [],
                samples: []
            };

            // Format all evaluation scores
            const evalInputs = document.querySelectorAll('input[id$="_eval"]');
            evalInputs.forEach(input => {
                input.value = formatEvalScore(input.value);
            });

            // Collect OCR image names
            if (jsonData.num_ocr_samples > 0) {
                for (let i = 1; i <= jsonData.num_ocr_samples; i++) {
                    const fileName = formData.get(`ocr_file_${i}`);
                    const displayName = formData.get(`ocr_display_${i}`);
                    if (fileName) {
                        jsonData.ocr_files.push(fileName);
                        jsonData.ocr_displays.push(displayName || fileName);
                    }
                }
            }

            // Collect samples data
            for (let q = 1; q <= jsonData.num_questions; q++) {
                const questionSamples = [];

                // Find all samples for this question by looking for sample answer fields
                const sampleInputs = document.querySelectorAll(`[id^="q${q}_s"][id$="_answer"]`);
                for (const input of sampleInputs) {
                    const id = input.id;
                    const parts = id.split('_');
                    const sampleNum = parseInt(parts[1].substring(1));
                    const sampleId = `q${q}_s${sampleNum}`;

                    const typeSelect = document.getElementById(`${sampleId}_type`);
                    const sampleType = typeSelect ? typeSelect.value : jsonData.question_type;

                    const evalInput = document.getElementById(`${sampleId}_eval`);
                    // Format evaluation score
                    if (evalInput) {
                        evalInput.value = formatEvalScore(evalInput.value);
                    }

                    const sample = {
                        answer: input.value,
                        evaluation: evalInput ? evalInput.value : '0.0',
                        type: sampleType
                    };

                    // Add preview for types that need it
                    if (sampleType === 'long' || sampleType === 'math mixed') {
                        const previewElement = document.getElementById(`${sampleId}_preview`);
                        sample.preview = previewElement ? previewElement.value : '';
                    }

                    questionSamples.push(sample);
                }

                jsonData.samples.push(questionSamples);
            }

            // Send data to server for preview
            fetch('/preview', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jsonData)
            })
            .then(response => response.json())
            .then(data => {
                // Close previous preview window if it exists and is not closed
                if (previewWindow && !previewWindow.closed) {
                    previewWindow.close();
                }

                // Open new window
                previewWindow = window.open('', 'PreviewWindow', 'width=800,height=600');

                // Write preview content to the new window
                previewWindow.document.open();
                previewWindow.document.write(data.html);
                previewWindow.document.close();

                // Focus on the new window
                previewWindow.focus();
            })
            .catch(error => {
                console.error('Error generating preview:', error);
                alert('Error generating preview: ' + error);
            });
        });

        // Initialize the lock functionality when the document is loaded
        document.addEventListener('DOMContentLoaded', function() {
            updateQuestions(true); // Initialize with default (unlocked)
            
            // Add click event for the lock button
            document.getElementById('samplesLockBtn').addEventListener('click', function() {
                samplesLocked = !samplesLocked;
                updateLockIcon();
            });
            
            // Initialize the lock icon based on the default state (unlocked)
            updateLockIcon();
            
            // Clear OCR values and sample values on page load
            ocrValues = {};
            sampleValues = {};
        });
        
        // Function to update the lock icon based on the lock state
        function updateLockIcon() {
            const lockIcon = document.getElementById('samplesLockIcon');
            if (samplesLocked) {
                lockIcon.className = 'bi bi-lock-fill';
                document.getElementById('samplesLockBtn').title = "Locked: Changes only affect new questions";
                document.getElementById('samplesLockBtn').classList.remove('btn-outline-danger');
                document.getElementById('samplesLockBtn').classList.add('btn-outline-secondary');
            } else {
                lockIcon.className = 'bi bi-unlock-fill';
                document.getElementById('samplesLockBtn').title = "Unlocked: Changes affect all current questions";
                document.getElementById('samplesLockBtn').classList.remove('btn-outline-secondary');
                document.getElementById('samplesLockBtn').classList.add('btn-outline-danger');
                
                // Immediately apply the current samples_per_question to all questions when unlocked
                const samplesPerQuestion = parseInt(document.getElementById('samples_per_question').value) || 1;
                
                // Store all current values before updating
                storeAllSampleValues();
                
                // Update all questions to the new sample count
                const numQuestions = parseInt(document.getElementById('num_questions').value) || 0;
                for (let q = 1; q <= numQuestions; q++) {
                    questionSampleCounts[q] = samplesPerQuestion;
                }
                
                // Refresh the UI
                updateQuestions(false);
            }
        }

        // Add this function to createSampleConfig function, after setting sampleDiv.innerHTML = sampleContent;
        function wrapTextareas() {
            // Find all textareas in the document
            const textareas = document.querySelectorAll('textarea.form-control');
            
            textareas.forEach(textarea => {
                // Skip if already wrapped
                if (textarea.parentNode.classList.contains('textarea-container')) {
                    return;
                }
                
                // Create container
                const container = document.createElement('div');
                container.className = 'textarea-container';
                
                // Create resize handle
                const resizer = document.createElement('div');
                resizer.className = 'resize-handle';
                
                // Insert wrapper before textarea
                textarea.parentNode.insertBefore(container, textarea);
                
                // Move textarea into container
                container.appendChild(textarea);
                
                // Add resize handle after textarea
                container.appendChild(resizer);
                
                // Add resize handling
                let startY, startHeight;
                
                function initResize(e) {
                    e.preventDefault();
                    startY = e.clientY || e.touches?.[0]?.clientY;
                    startHeight = parseInt(window.getComputedStyle(textarea).height);
                    resizer.classList.add('active');
                    
                    // Add mousemove and mouseup event listeners
                    document.addEventListener('mousemove', resize);
                    document.addEventListener('touchmove', resize);
                    document.addEventListener('mouseup', stopResize);
                    document.addEventListener('touchend', stopResize);
                }
                
                function resize(e) {
                    if (!startY) return;
                    const y = e.clientY || e.touches?.[0]?.clientY;
                    const newHeight = Math.max(60, startHeight + (y - startY));
                    
                    // Use requestAnimationFrame for smooth resizing
                    requestAnimationFrame(() => {
                        textarea.style.height = newHeight + 'px';
                    });
                }
                
                function stopResize() {
                    resizer.classList.remove('active');
                    document.removeEventListener('mousemove', resize);
                    document.removeEventListener('touchmove', resize);
                    document.removeEventListener('mouseup', stopResize);
                    document.removeEventListener('touchend', stopResize);
                    startY = null;
                }
                
                // Function to resize textarea to fit all content on double-click
                function resizeToFitContent() {
                    // Save scroll position
                    const scrollPos = textarea.scrollTop;
                    
                    // Temporarily modify the textarea to measure content
                    const originalHeight = textarea.style.height;
                    textarea.style.height = 'auto';
                    
                    // Create a hidden div to measure content precisely
                    const hiddenDiv = document.createElement('div');
                    
                    // Copy textarea styles that affect content measurement
                    const styles = window.getComputedStyle(textarea);
                    const relevantStyles = [
                        'font-family', 'font-size', 'font-weight', 'line-height',
                        'letter-spacing', 'text-transform', 'word-spacing', 'padding-top',
                        'padding-right', 'padding-bottom', 'padding-left', 'border-width',
                        'box-sizing', 'width'
                    ];
                    
                    relevantStyles.forEach(style => {
                        hiddenDiv.style[style] = styles.getPropertyValue(style);
                    });
                    
                    // Force specific styles needed for accurate measurement
                    hiddenDiv.style.visibility = 'hidden';
                    hiddenDiv.style.position = 'absolute';
                    hiddenDiv.style.height = 'auto';
                    hiddenDiv.style.whiteSpace = 'pre-wrap';
                    hiddenDiv.style.overflow = 'auto';
                    
                    // Set text content and add to DOM
                    hiddenDiv.textContent = textarea.value;
                    document.body.appendChild(hiddenDiv);
                    
                    // Get the height (add a small buffer for accuracy)
                    const contentHeight = hiddenDiv.scrollHeight + 5;
                    
                    // Remove the hidden div
                    document.body.removeChild(hiddenDiv);
                    
                    // Set the new height with a nice animation
                    textarea.style.transition = 'height 0.2s ease';
                    textarea.style.height = Math.max(120, contentHeight) + 'px';
                    
                    // Reset scroll position
                    textarea.scrollTop = scrollPos;
                    
                    // Remove transition after animation completes
                    setTimeout(() => {
                        textarea.style.transition = '';
                    }, 200);
                }
                
                // Add event listeners
                resizer.addEventListener('mousedown', initResize);
                resizer.addEventListener('touchstart', initResize, { passive: false });
                
                // Add double-click to resize to content
                resizer.addEventListener('dblclick', resizeToFitContent);
                
                // Add a tooltip to indicate the double-click functionality
                resizer.title = "Drag to resize or double-click to fit content";
            });
        }
    </script>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        filename = request.form.get('filename', 'questions')
        question_type = request.form.get('question_type')
        num_questions = int(request.form.get('num_questions', 1))
        samples_per_question = int(request.form.get('samples_per_question', 1))
        num_ocr_samples = int(request.form.get('num_ocr_samples', 0))
        ocr_image_names = []
        ocr_display_names = []

        if num_ocr_samples > 0:
            for i in range(1, num_ocr_samples + 1):
                file_name = request.form.get(f'ocr_file_{i}')
                display_name = request.form.get(f'ocr_display_{i}')
                if file_name:
                    ocr_image_names.append(file_name)
                    ocr_display_names.append(display_name or file_name)

        # Collect sample answers and evaluations
        samples = []
        for q in range(1, num_questions + 1):
            question_samples = []
            sample_index = 1
            while True:
                answer_key = f'q{q}_s{sample_index}_answer'
                if answer_key not in request.form:
                    break

                eval_key = f'q{q}_s{sample_index}_eval'
                preview_key = f'q{q}_s{sample_index}_preview'
                sample_type_key = f'q{q}_s{sample_index}_type'

                answer = request.form.get(answer_key, '')
                evaluation = request.form.get(eval_key, '0.0')
                sample_type = request.form.get(sample_type_key, question_type)
                
                # Get preview for long type and math mixed - both need preview fields
                preview = None
                if sample_type in ('long', 'math mixed'):
                    preview = request.form.get(preview_key, '')

                question_samples.append({
                    'answer': answer,
                    'evaluation': evaluation,
                    'preview': preview,
                    'type': sample_type
                })
                sample_index += 1

            samples.append(question_samples)

        # --- Modification Start: Attempt to rename file in local Downloads folder ---
        original_filename = f"{filename}.html"
        backup_filename = f"{filename}_backup.html"
        
        # ASSUMPTION: Construct the full path in the user's Downloads folder
        assumed_original_path = DOWNLOADS_PATH / original_filename
        assumed_backup_path = DOWNLOADS_PATH / backup_filename

        print(f"--- Attempting Local Rename --- ")
        print(f"Assuming Original Path: {assumed_original_path}")
        print(f"Assuming Backup Path: {assumed_backup_path}")

        # Try to rename the file in the Downloads folder
        if assumed_original_path.exists():
            print(f"Original file found at assumed path. Attempting rename...")
            try:
                # Remove old backup if it exists
                if assumed_backup_path.exists():
                    print(f"Removing existing backup: {assumed_backup_path}")
                    assumed_backup_path.unlink()
                
                # Rename original to backup
                assumed_original_path.rename(assumed_backup_path)
                print(f"Successfully renamed {assumed_original_path} to {assumed_backup_path}")
            except Exception as e:
                print(f"Error renaming file in Downloads folder: {e}")
                print("This might be due to permissions or the file being in use.")
        else:
            print(f"Original file not found at assumed path: {assumed_original_path}")
        # --- Modification End ---

        # Generate HTML content based on question type
        html_content = generate_html(filename, question_type, num_questions,
                                     samples_per_question, num_ocr_samples > 0,
                                     ocr_image_names, ocr_display_names, samples)

        # --- Modification: Send content directly for download ---
        # Send the generated content directly, letting the browser save it
        return send_file(
            io.BytesIO(html_content.encode('utf-8')),
            as_attachment=True,
            download_name=original_filename, # Suggest the original name
            mimetype='text/html'
        )
        # --- Modification End ---

    # Return the HTML template directly
    return CREATOR_HTML


@app.route('/preview', methods=['POST'])
def preview():
    # Get form data from AJAX request
    data = request.json
    filename = data.get('filename', 'questions')
    question_type = data.get('question_type')
    num_questions = int(data.get('num_questions', 1))
    samples_per_question = int(data.get('samples_per_question', 1))
    num_ocr_samples = int(data.get('num_ocr_samples', 0))
    require_ocr = num_ocr_samples > 0
    ocr_image_names = data.get('ocr_files', [])
    ocr_display_names = data.get('ocr_displays', [])
    samples = data.get('samples', [])

    # Process the samples to ensure consistency with the generate_html function
    # For math mixed, we need both preview (for display) and answer (for copying)
    for q_idx, question_samples in enumerate(samples):
        for s_idx, sample in enumerate(question_samples):
            # Fix debug: Print values before/after processing
            print(f"Preview: Q{q_idx+1}S{s_idx+1} Type: {sample.get('type')}, Preview: {sample.get('preview')}")
            
            # Ensure both answer and preview fields are present as needed
            if sample.get('type') == 'math mixed':
                # For math mixed, ensure we have both preview and answer
                sample['answer'] = sample.get('answer', '')
                # If preview is empty or None but answer exists, use the answer as preview
                if not sample.get('preview') and sample.get('answer'):
                    sample['preview'] = sample.get('answer')
                else:
                    sample['preview'] = sample.get('preview', '')
                    
            elif sample.get('type') == 'long':
                # For long, we need both answer and preview
                sample['answer'] = sample.get('answer', '')
                sample['preview'] = sample.get('preview', '')
            else:
                # For other types, just ensure answer is present
                sample['answer'] = sample.get('answer', '')
                
            # Debug: Print after processing
            print(f"After: Q{q_idx+1}S{s_idx+1} Type: {sample.get('type')}, Preview: {sample.get('preview')}")

    # Check if any sample has a different type than the default question type
    has_custom_types = any(
        sample.get('type') != question_type
        for question_samples in samples
        for sample in question_samples
    )
    
    # If custom types are used, add this info to data for potential UI feedback
    data['has_custom_types'] = has_custom_types

    # Generate HTML content using the same function as the main route
    html_content = generate_html(filename, question_type, num_questions,
                                 samples_per_question, require_ocr,
                                 ocr_image_names, ocr_display_names, samples)

    return jsonify({'html': html_content, 'has_custom_types': has_custom_types})


@app.route('/import_html', methods=['POST'])
def import_html():
    try:
        # Get the uploaded HTML file content
        if 'html_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})

        file = request.files['html_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})

        # Get the actual filename without extension
        actual_filename = os.path.splitext(file.filename)[0]

        html_content = file.read().decode('utf-8')

        # Parse the HTML to extract data
        data = parse_html_for_import(html_content)

        if data:
            # Set the actual filename
            data['filename'] = actual_filename
            return jsonify({'success': True, 'data': data})
        else:
            return jsonify({'success': False, 'error': 'Could not parse the HTML file correctly'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def parse_html_for_import(html_content):
    """Parse the HTML file and extract the data needed to populate the form."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract filename from title as fallback
        title_tag = soup.title
        filename_from_title = title_tag.string if title_tag else "questions"
        filename = filename_from_title

        # Check for OCR images
        ocr_files = []
        ocr_displays = []
        ocr_section = soup.find('h4', string=lambda text: text and 'Download handwritten sample' in text)
        if ocr_section:
            image_links = ocr_section.find_next('div', class_='download-buttons').find_all('a')
            for link in image_links:
                img_url = link.get('href', '')
                img_file = img_url.split('/')[-1].replace('.png', '')
                img_display = link.text.strip()
                ocr_files.append(img_file)
                ocr_displays.append(img_display)

        # Extract samples
        samples = []
        rows = soup.find_all('tr')
        current_question = 0
        question_samples = []
        sample_types = set()
        max_samples = 0
        
        # Default question type
        question_type = 'short'

        for row in rows[1:]:  # Skip header row
            # Parse question number and sample number
            question_cell = row.find('td')
            if not question_cell:
                continue

            question_text = question_cell.text.strip()
            match = re.match(r'Q(\d+).*?Sample (\d+)', question_text)
            if not match:
                continue

            q_num = int(match.group(1))
            s_num = int(match.group(2))
            max_samples = max(max_samples, s_num)

            # If we're starting a new question, add the previous question's samples to the list
            if q_num != current_question:
                if question_samples:
                    samples.append(question_samples)
                    question_samples = []
                current_question = q_num

            # Get sample cells
            cells = row.find_all('td')
            if len(cells) < 4:
                continue

            # Extract data
            answer_cell = cells[2]
            eval_cell = cells[3]

            # Determine sample type and extract content
            sample_type = 'short'  # default
            answer = ''
            preview = None

            # Check if it's a math mixed cell
            if answer_cell.get('class') and 'mixed-math-content' in answer_cell.get('class'):
                sample_type = 'math mixed'
                # Get the full answer from data-full-text attribute
                answer = answer_cell.get('data-full-text', '')
                
                # For preview, get the actual rendered content from math-line divs
                preview_lines = []
                math_lines = answer_cell.find_all('div', class_='math-line')
                if math_lines:
                    for line in math_lines:
                        # Get the actual rendered content, not the data attribute
                        line_text = line.get_text().strip()
                        if line_text:
                            preview_lines.append(line_text)
                    preview = '\n'.join(preview_lines)
                else:
                    # If no math-line divs found, use the text content as preview
                    preview = answer_cell.get_text().strip()
                
                # If preview is empty but we have an answer, use the answer
                if not preview and answer:
                    preview = answer
                
            # Check if it's a math pure cell
            elif answer_cell.find('div', class_='math-formula'):
                sample_type = 'math pure'
                math_formulas = answer_cell.find_all('div', class_='math-formula')
                math_parts = []
                for formula in math_formulas:
                    formula_text = formula.get_text().strip()
                    if formula_text.startswith('$$') and formula_text.endswith('$$'):
                        formula_text = formula_text[2:-2]  # Remove $$ from start and end
                    math_parts.append(formula_text)
                answer = '\n'.join(math_parts)
                preview = None  # Math pure doesn't need preview
                
            # Check if it's a long answer
            elif answer_cell.has_attr('data-full-text'):
                sample_type = 'long'
                answer = answer_cell.get('data-full-text', '')
                preview_text = answer_cell.get_text().strip()
                if '......' in preview_text:
                    preview = preview_text.split('......')[0].strip()
                else:
                    preview = preview_text
            # Otherwise it's a short answer
            else:
                answer = answer_cell.get_text().strip()

            # Extract evaluation score
            evaluation = eval_cell.get_text().strip()

            # Create the sample data
            sample_data = {
                'answer': answer,
                'evaluation': evaluation,
                'type': sample_type
            }
            if preview is not None:
                sample_data['preview'] = preview

            question_samples.append(sample_data)
            sample_types.add(sample_type)

        # Add the last group of samples
        if question_samples:
            samples.append(question_samples)

        # Determine question type based on sample types
        if len(sample_types) == 1:
            question_type = next(iter(sample_types))
        elif len(sample_types) > 1:
            # Use "custom" for mixed types
            question_type = 'custom'

        return {
            'filename': filename,
            'question_type': question_type,
            'num_questions': len(samples),
            'samples_per_question': max_samples,
            'ocr_files': ocr_files,
            'ocr_displays': ocr_displays,
            'samples': samples
        }
    except Exception as e:
        print(f"Error parsing HTML: {str(e)}")
        return None


def generate_html(filename, question_type, num_questions, samples_per_question,
                  require_ocr, ocr_image_names, ocr_display_names, samples):
    # Start with basic HTML structure following the exact layout provided
    html = '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
    html += '  <meta charset="utf-8">\n'
    html += '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
    html += '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet"\n'
    html += '    integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">\n'
    html += '  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"\n'
    html += '    integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"\n'
    html += '    crossorigin="anonymous"></script>\n'
    html += '  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">\n'
    
    # Check if any sample uses math type
    has_math_samples = question_type in ('math pure', 'math mixed') or any(
        sample.get('type') in ('math pure', 'math mixed')
        for question_samples in samples
        for sample in question_samples
    )
    
    # Add MathJax for math questions or if any sample uses math type
    if has_math_samples:
        html += '  <script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=es6"></script>\n'
        html += '  <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n'
        # Add MathJax configuration to ensure it processes all math content
        html += '  <script type="text/javascript">\n'
        html += '    window.MathJax = {\n'
        html += '      tex: {\n'
        html += '        inlineMath: [["$", "$"]],\n'
        html += '        displayMath: [["$$", "$$"]],\n'
        html += '        processEscapes: true,\n'
        html += '        processEnvironments: true\n'
        html += '      },\n'
        html += '      startup: {\n'
        html += '        ready: function () {\n'
        html += '          MathJax.startup.defaultReady();\n'
        html += '        }\n'
        html += '      },\n'
        html += '      options: {\n'
        html += '        enableMenu: false, /* Disable the right-click menu */\n'
        html += '        renderActions: {\n'
        html += '          addMenu: [0, "", ""] /* Remove menu items */\n'
        html += '        }\n'
        html += '      }\n'
        html += '    };\n'
        html += '  </script>\n'

    html += f'  <title>{escape(filename)}</title>\n'
    html += '  <style>\n'
    html += '    body {\n'
    html += '      margin: 0;\n'
    html += '      padding: 0;\n'
    html += '      overflow-x: hidden;\n'
    html += '      width: 100%;\n'
    html += '    }\n'
    html += '    .container-fluid {\n'
    html += '      padding-left: 0;\n'
    html += '      padding-right: 0;\n'
    html += '      width: calc(100% - 5px);\n'
    html += '      margin-right: 5px;\n'
    html += '      overflow-x: hidden;\n'
    html += '    }\n'
    html += '    h4 {\n'
    html += '      padding-left: 5px !important;\n'
    html += '    }\n'
    html += '    .full-width-table {\n'
    html += '      width: 100%;\n'
    html += '      margin: 0;\n'
    html += '      table-layout: fixed;\n'
    html += '      overflow: hidden;\n'
    html += '    }\n'
    html += '    .sample-answer-cell {\n'
    html += '      font-size: 0.95em;\n'
    html += '      padding: 4px;\n'
    html += '    }\n'
    html += '    .question-col, td.question-col, th.question-col {\n'
    html += '      width: 90px !important;\n'
    html += '      min-width: 90px !important;\n'
    html += '      max-width: 90px !important;\n'
    html += '      font-size: 1.1em !important;\n'
    html += '      white-space: normal;\n'
    html += '      overflow: hidden;\n'
    html += '      padding-top: 4px !important;\n'
    html += '      line-height: 1.3;\n'
    html += '      font-weight: 500;\n'
    html += '    }\n'
    html += '    .eval-col, td.eval-col, th.eval-col {\n'
    html += '      width: 85px !important;\n'
    html += '      min-width: 85px !important;\n'
    html += '      max-width: 85px !important;\n'
    html += '      font-size: 1.1em !important;\n'
    html += '      white-space: nowrap;\n'
    html += '      overflow: visible;\n'
    html += '      text-align: left;\n'
    html += '      padding-top: 4px !important;\n'
    html += '      padding-left: 8px !important;\n'
    html += '    }\n'
    html += '    .full-width-table th {\n'
    html += '      font-size: 0.85em !important;\n'
    html += '      white-space: nowrap;\n'
    html += '      overflow: hidden;\n'
    html += '      padding: 8px 4px;\n'
    html += '      font-weight: bold;\n'
    html += '    }\n'
    html += '    .sample-answer-header {\n'
    html += '      font-size: 0.85em !important;\n'
    html += '      text-align: left;\n'
    html += '      white-space: nowrap;\n'
    html += '      overflow: hidden;\n'
    html += '      font-weight: bold;\n'
    html += '      padding-left: 8px !important;\n'
    html += '    }\n'
    html += '    .math-formula {\n'
    html += '      display: block;\n'
    html += '      margin: 0;\n'
    html += '      padding: 0;\n'
    html += '      max-width: 100%;\n'
    html += '      font-size: 1em;\n'
    html += '      transform-origin: left;\n'
    html += '      transform: scale(1);\n'
    html += '      overflow: hidden;\n'
    html += '      line-height: 0.9;\n'
    html += '      min-height: 0;\n'
    html += '    }\n'
    html += '    .math-line {\n'
    html += '      margin: 0;\n'
    html += '      padding: 2px 0;\n'
    html += '      display: block;\n'
    html += '      font-size: 1em;\n'
    html += '      max-width: 100%;\n'
    html += '      overflow: hidden;\n'
    html += '      overflow-wrap: break-word;\n'
    html += '      word-wrap: break-word;\n'
    html += '      -ms-word-break: break-all;\n'
    html += '      word-break: break-word;\n'
    html += '      line-height: 1.4;\n'
    html += '      min-height: 1.4em;\n'
    html += '    }\n'
    html += '    .math-line:has(.MathJax) {\n'
    html += '      line-height: 0.2;\n'
    html += '      min-height: 0;\n'
    html += '      padding: 0;\n'
    html += '    }\n'
    html += '    .mixed-math-content {\n'
    html += '      white-space: pre-wrap;\n'
    html += '      font-family: inherit;\n'
    html += '      line-height: 1.4;\n'
    html += '      font-size: 1em;\n'
    html += '      padding: 0;\n'
    html += '      margin: 0;\n'
    html += '      width: 100%;\n'
    html += '      box-sizing: border-box;\n'
    html += '      overflow: hidden;\n'
    html += '      min-height: 0;\n'
    html += '    }\n'
    html += '    .preserve-whitespace {\n'
    html += '      white-space: pre-wrap;\n'
    html += '    }\n'
    html += '    textarea.form-control {\n'
    html += '      min-height: 120px;\n'
    html += '      line-height: 1.6;\n'
    html += '      font-size: 0.95rem;\n'
    html += '      /* No resize - we\'ll handle it with custom controls */\n'
    html += '      resize: none;\n'
    html += '    }\n'
    html += '    .textarea-container {\n'
    html += '      position: relative;\n'
    html += '      margin-bottom: 15px;\n'
    html += '    }\n'
    html += '    .resize-handle {\n'
    html += '      display: block;\n'
    html += '      height: 10px;\n'
    html += '      background-color: #f0f0f0;\n'
    html += '      border-radius: 0 0 4px 4px;\n'
    html += '      cursor: ns-resize;\n'
    html += '      position: relative;\n'
    html += '      border: 1px solid #dee2e6;\n'
    html += '      border-top: none;\n'
    html += '      user-select: none;\n'
    html += '    }\n'
    html += '    .resize-handle:hover, .resize-handle.active {\n'
    html += '      background-color: #d0d0d0;\n'
    html += '    }\n'
    html += '    .resize-handle::after {\n'
    html += '      content: \'\';\n'
    html += '      display: block;\n'
    html += '      width: 20px;\n'
    html += '      height: 3px;\n'
    html += '      position: absolute;\n'
    html += '      top: 3px;\n'
    html += '      left: 50%;\n'
    html += '      transform: translateX(-50%);\n'
    html += '      background-image: linear-gradient(to right, #aaa 1px, transparent 1px);\n'
    html += '      background-size: 4px 100%;\n'
    html += '    }\n'
    html += '    .table-layout-fixed {\n'
    html += '      table-layout: fixed;\n'
    html += '      width: 100%;\n'
    html += '    }\n'
    html += '    .copy-col {\n'
    html += '      width: 60px !important;\n'
    html += '      max-width: 60px !important;\n'
    html += '      min-width: 60px !important;\n'
    html += '      padding: 4px !important;\n'
    html += '    }\n'
    html += '    .copy-button {\n'
    html += '      width: 100% !important;\n'
    html += '      height: 30px;\n'
    html += '      padding: 4px 0;\n'
    html += '      font-size: 14px;\n'
    html += '      white-space: nowrap;\n'
    html += '      display: block;\n'
    html += '      margin: 0;\n'
    html += '    }\n'
    html += '    .eval-math-content {\n'
    html += '      font-size: 0.9em; /* Base size slightly smaller for evaluation math */\n'
    html += '      overflow-x: auto; /* Allow horizontal scrolling if needed */\n'
    html += '    }\n'
    html += '    @media screen and (max-width: 768px) {\n'
    html += '      .sample-answer-cell {\n'
    html += '        font-size: 0.85em;\n'
    html += '        padding: 4px 2px;\n'
    html += '      }\n'
    html += '    }\n'
    html += '    @media screen and (max-width: 576px) {\n'
    html += '      .sample-answer-cell {\n'
    html += '        font-size: 0.8em;\n'
    html += '        padding: 4px 2px;\n'
    html += '      }\n'
    html += '    }\n'
    html += '    .math-line .MathJax {\n'
    html += '      max-width: 100%;\n'
    html += '      overflow: hidden;\n'
    html += '      font-size: 100% !important;\n'
    html += '      margin: 0 !important;\n'
    html += '      padding: 0 !important;\n'
    html += '      line-height: 0 !important;\n'
    html += '      min-height: 0 !important;\n'
    html += '      display: block !important;\n'
    html += '    }\n'
    html += '    .MathJax_Display {\n'
    html += '      margin: 0 !important;\n'
    html += '      padding: 0 !important;\n'
    html += '      line-height: 0 !important;\n'
    html += '      min-height: 0 !important;\n'
    html += '    }\n'
    html += '    .MathJax_SVG_Display {\n'
    html += '      margin: 0 !important;\n'
    html += '      padding: 0 !important;\n'
    html += '      line-height: 0 !important;\n'
    html += '      min-height: 0 !important;\n'
    html += '    }\n'
    html += '    .download-buttons {\n'
    html += '      display: flex;\n'
    html += '      flex-wrap: wrap;\n'
    html += '      gap: 2px;\n'
    html += '      padding: 2px;\n'
    html += '    }\n'
    html += '    .download-buttons .btn {\n'
    html += '      font-size: 0.9em;\n'
    html += '      padding: 6px 12px;\n'
    html += '      margin: 0;\n'
    html += '      line-height: 1.5;\n'
    html += '      height: auto;\n'
    html += '      transform: scale(0.9);\n'
    html += '    }\n'
    html += '  </style>\n'
    html += '</head>\n<body>\n'
    html += '  <div class="container-fluid">\n'
    html += '    <div class="row">\n'
    html += '      <div class="col">\n'

    # OCR section if required
    if require_ocr and ocr_image_names:
        html += '        <h4 style="padding-left: 10px; padding-top: 5px;">Download handwritten sample images</h4>\n'
        html += '        <table class="table table-bordered table-no-space">\n'
        html += '          <thead>\n'
        html += '          </thead>\n'
        html += '          <tbody>\n'
        html += '            <tr>\n'
        html += '              <td style="padding: 2px;">\n'
        html += '                <div class="download-buttons">\n'

        # Add buttons for each image with display name
        for idx, img_name in enumerate(ocr_image_names):
            display_name = ocr_display_names[idx] if idx < len(ocr_display_names) else img_name
            html += f'                  <a type="button" class="btn btn-primary" href="https://www.una.study/gpt/hw/{escape(img_name)}.png">{display_name}</a>\n'

        html += '                </div>\n'
        html += '              </td>\n'
        html += '            </tr>\n'
        html += '          </tbody>\n'
        html += '        </table>\n'

    # Sample answers section
    html += '        <h4 style="padding-left: 10px; padding-top: 5px;">Copy plain text sample answers</h4>\n'
    html += '        <table class="table table-striped table-bordered table-hover full-width-table">\n'
    html += '          <thead>\n'
    html += '            <tr>\n'
    html += '              <th scope="col" class="question-col">Question</th>\n'
    html += '              <th scope="col" class="copy-col"></th>\n'
    html += '              <th scope="col" class="sample-answer-header" style="width: auto;">Sample Answer</th>\n'
    html += '              <th scope="col" class="eval-col">Evaluation</th>\n'
    html += '            </tr>\n'
    html += '          </thead>\n'
    html += '          <tbody>\n'

    # Create rows for each question and sample
    for q in range(len(samples)):
        question_samples = samples[q]
        for s in range(len(question_samples)):
            sample_data = question_samples[s]
            sample_type = sample_data.get('type', question_type)

            html += '            <tr>\n'
            html += f'              <td scope="row">Q{q + 1}<br>Sample {s + 1}</td>\n'
            html += '              <td class="copy-col">\n'
            html += '                <button type="button" class="btn btn-primary copy-button" onclick="copyToClipboard(this)">\n'
            html += '                  Copy\n'
            html += '                </button>\n'
            html += '              </td>\n'

            # Content display based on sample type
            if sample_type == 'short':
                html += f'              <td class="preserve-whitespace sample-answer-cell">{escape(sample_data["answer"])}</td>\n'
            elif sample_type == 'long':
                html += f'              <td class="preserve-whitespace sample-answer-cell" data-full-text="{escape(sample_data["answer"])}">{escape(sample_data["preview"])}\n'
                html += '<strong>......</strong>\n'
                html += '              </td>\n'
            elif sample_type == 'math mixed':
                html += f'              <td class="mixed-math-content mathjax sample-answer-cell" data-full-text="{escape(sample_data["answer"])}">'
                
                # Get the PREVIEW content for math mixed type - this should have LaTeX formatting
                preview_content = sample_data.get("preview", "")
                
                # If preview is empty, fall back to the answer content
                if not preview_content.strip() and sample_data.get("answer"):
                    preview_content = sample_data.get("answer", "")
                
                # For math mixed type, we need to ensure MathJax processes the content
                # We'll create divs for each line to ensure proper math rendering
                lines = preview_content.split('\n')
                for line in lines:
                    if line.strip():
                        # Replace % with \% to prevent LaTeX comment behavior
                        processed_line = line.replace('%', '\\%')
                        
                        # For math mixed content, insert directly without HTML escaping
                        # to allow MathJax to process the math delimiters
                        html += f'<div class="math-line">{processed_line}</div>\n'
                
                html += '              </td>\n'
            elif sample_type == 'math pure':
                # Store the original LaTeX formula (without dollar signs) for copying
                html += f'              <td class="mixed-math-content mathjax sample-answer-cell" data-full-text="{escape(sample_data["answer"])}">'
                
                # Math pure uses the answer content directly
                # Split math content by lines and render each line separately
                math_lines = sample_data["answer"].split('\n')
                for line in math_lines:
                    if line.strip():  # Only process non-empty lines
                        # Replace % with \% to prevent LaTeX comment behavior
                        processed_line = line.strip().replace('%', '\\%')
                        
                        # For math pure, automatically wrap with $$ delimiters
                        html += f'<div class="math-line">$${processed_line}$$</div>\n'
                
                html += '              </td>\n'

            html += f'              <td class="eval-col">{escape(sample_data["evaluation"])}</td>\n'
            html += '            </tr>\n'

    html += '          </tbody>\n'
    html += '        </table>\n'
    html += '      </div>\n'
    html += '    </div>\n'
    html += '  </div>\n'

    # JavaScript for copy functionality
    html += '  <script>\n'
    html += 'function copyToClipboard(button) {\n'
    html += '  const tr = button.closest(\'tr\');\n'
    html += '  let textToCopy;\n'
    html += '  const dataFullText = tr.querySelector(\'td[data-full-text]\');\n'
    html += '  if (dataFullText) {\n'
    html += '    textToCopy = dataFullText.getAttribute(\'data-full-text\');\n'
    html += '  } else {\n'
    html += '    const tds = tr.querySelectorAll(\'td\');\n'
    html += '    textToCopy = tds[2].innerText;\n'
    html += '  }\n'
    html += '  navigator.clipboard.writeText(textToCopy);\n'
    html += '\n'
    html += '  const buttons = document.querySelectorAll(\'button\');\n'
    html += '  for (const btn of buttons) {\n'
    html += '    btn.classList.remove(\'btn-success\');\n'
    html += '    btn.classList.add(\'btn-primary\');\n'
    html += '  }\n'
    html += '\n'
    html += '  button.classList.remove(\'btn-primary\');\n'
    html += '  button.classList.add(\'btn-success\');\n'
    html += '}\n'
    html += '\n'
    html += 'document.addEventListener("DOMContentLoaded", function() {\n'
    html += '  // Force MathJax to reprocess the page after it\'s loaded\n'
    html += '  if (typeof MathJax !== "undefined") {\n'
    html += '    setTimeout(function() {\n'
    html += '      MathJax.typeset();\n'
    html += '    }, 100);\n'
    html += '  }\n'
    html += '});\n'
    html += '  </script>\n'
    html += '  <style>\n'
    html += '    button {\n'
    html += '      padding: 4px 8px;\n'
    html += '      font-size: 12px;\n'
    html += '    }\n'
    html += '  </style>\n'
    html += '<script defer src="https://static.cloudflareinsights.com/beacon.min.js/vcd15cbe7772f49c399c6a5babf22c1241717689176015" integrity="sha512-ZpsOmlRQV6y907TI0dKBHq9Md29nnaEIPlkf84rnaERnq6zvWvPUqr2ft8M1aS28oN72PdrCzSjY4U6VaAw1EQ==" data-cf-beacon=\'{"rayId":"92df0cc99c3fe88a","version":"2025.3.0","r":1,"token":"a8d6ea2b591b4a668957e39125a30b03","serverTiming":{"name":{"cfExtPri":true,"cfL4":true,"cfSpeedBrain":true,"cfCacheStatus":true}}}\' crossorigin="anonymous"></script>\n'
    html += '</body>\n</html>'

    return html


if __name__ == '__main__':
    app.run(debug=True) 