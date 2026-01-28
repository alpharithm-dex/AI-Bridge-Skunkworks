from flask import Flask, request, jsonify, make_response
import os
import sys
import json
import io

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rewriter import correct_bias

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Bias Correction API</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .section { background: #f9f9f9; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ddd; }
        h2 { margin-top: 0; color: #444; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #0056b3; }
        #result, #batch-result { margin-top: 15px; white-space: pre-wrap; background: #fff; padding: 15px; border: 1px solid #eee; border-radius: 4px; display: none; }
        .error { color: red; }
        select { padding: 8px; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>Bias Correction API</h1>
    
    <div class="section">
        <h2>Single Sentence Correction</h2>
        <p>Enter text to detect and correct bias.</p>
        <textarea id="inputText" placeholder="Enter text here... (e.g., 'Mosetsana o apea dijo')"></textarea>
        <br>
        <select id="language">
            <option value="">Auto-detect Language</option>
            <option value="tn">Setswana</option>
            <option value="zu">isiZulu</option>
        </select>
        <button onclick="correctSingle()">Correct Text</button>
        <div id="result"></div>
    </div>

    <div class="section">
        <h2>Batch Processing</h2>
        <p>Upload a JSON file containing a list of items to process.</p>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="file" accept=".json" required>
            <button type="button" onclick="uploadBatch()">Upload & Process</button>
        </form>
        <div id="batch-result"></div>
    </div>

    <script>
        async function correctSingle() {
            const text = document.getElementById('inputText').value;
            const lang = document.getElementById('language').value;
            const resultDiv = document.getElementById('result');
            
            if (!text) {
                alert('Please enter some text');
                return;
            }

            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Processing...';

            try {
                const response = await fetch('/correct', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text, language: lang || null })
                });
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                resultDiv.textContent = 'Error: ' + e.message;
                resultDiv.classList.add('error');
            }
        }

        async function uploadBatch() {
            const form = document.getElementById('uploadForm');
            const fileInput = form.querySelector('input[type="file"]');
            const resultDiv = document.getElementById('batch-result');

            if (!fileInput.files[0]) {
                alert('Please select a file');
                return;
            }

            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Uploading and processing...';

            const formData = new FormData(form);

            try {
                const response = await fetch('/batch-correct', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                resultDiv.textContent = 'Error: ' + e.message;
                resultDiv.classList.add('error');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "bias-correction-api"}), 200

@app.route('/', methods=['GET'])
def index():
    return make_response(HTML_TEMPLATE)

@app.route('/correct', methods=['POST'])
def correct():
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field in request body"}), 400
    
    text = data['text']
    language = data.get('language')  # Optional, defaults to auto-detect
    
    try:
        result = correct_bias(text, language)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/batch-correct', methods=['POST'])
def batch_correct():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        try:
            # Read file content
            content = file.read()
            items = json.loads(content)
            
            if not isinstance(items, list):
                return jsonify({"error": "JSON must be a list of items"}), 400
            
            results = []
            for item in items:
                # Support both 'text' and 'biased_text' keys for flexibility
                text = item.get('text') or item.get('biased_text')
                item_id = item.get('id', 'unknown')
                lang = item.get('lang') or item.get('language')
                
                if text:
                    try:
                        correction = correct_bias(text, language=lang)
                        results.append({
                            "id": item_id,
                            "original": text,
                            "correction": correction
                        })
                    except Exception as e:
                        results.append({
                            "id": item_id,
                            "error": str(e)
                        })
            
            return jsonify(results), 200
            
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON file"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible inside container
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
