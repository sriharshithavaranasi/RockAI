import os
from flask import Flask, request, send_from_directory, jsonify
import requests

app = Flask(__name__)

# Folder where the uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Your API Access Key
ACCESS_KEY = "cm6wfjbgp0001ky0c0ievtcxz"

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MP3 Uploader and AI Music Generator</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f8f9fa;
                color: #333;
                margin: 0;
                padding: 0;
                text-align: center;
            }

            h1 {
                color: #4CAF50;
                margin-top: 20px;
            }

            .container {
                width: 80%;
                margin: 20px auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                text-align: center;
            }

            .form-container {
                margin-top: 20px;
                background-color: #e9f5e9;
                padding: 20px;
                border-radius: 10px;
            }

            input[type="file"],
            input[type="text"] {
                padding: 10px;
                width: 80%;
                margin: 10px 0;
                border-radius: 5px;
                border: 1px solid #ccc;
            }

            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s;
            }

            button:hover {
                background-color: #45a049;
            }

            a {
                color: #4CAF50;
                text-decoration: none;
            }

            a:hover {
                text-decoration: underline;
            }

            #musicDownloadLink, #downloadLink {
                margin-top: 20px;
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
            }

            .card {
                background-color: #ffffff;
                margin: 10px;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                display: inline-block;
                width: 30%;
                margin-bottom: 20px;
                text-align: center;
            }

            .card h3 {
                color: #333;
                font-size: 24px;
                margin-bottom: 15px;
            }

            .card p {
                color: #555;
                font-size: 18px;
                margin-bottom: 15px;
            }

            .card button {
                background-color: #008CBA;
            }

            .card button:hover {
                background-color: #007B9F;
            }

            .voice-list {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 15px;
            }

            .voice-card {
                padding: 15px;
                background-color: #f1f1f1;
                border-radius: 8px;
                width: 250px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                text-align: center;
            }

        </style>
    </head>
    <body>
        <h1>MP3 Uploader and AI Music Generator</h1>
        <div class="container">
            <div class="form-container">
                <h3>Upload an MP3 File</h3>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file" accept=".mp3" required>
                    <button type="submit">Upload</button>
                </form>
                <div id="downloadLink"></div>
            </div>

            <div class="form-container">
                <h3>Generate AI Music</h3>
                <form id="musicForm">
                    <input type="text" id="prompt" placeholder="Enter your music prompt" required>
                    <button type="submit">Generate Music</button>
                </form>
                <div id="musicDownloadLink"></div>
            </div>

            <div class="form-container">
                <h3>Get Available Voices</h3>
                <button id="getVoicesButton">Get Voices</button>
                <div id="voicesList" class="voice-list"></div>
            </div>
        </div>

        <script>
            // Handle file upload
            document.querySelector("form[action='/upload']").onsubmit = async function(event) {
                event.preventDefault();
                let formData = new FormData(this);
                
                let response = await fetch("/upload", { method: "POST", body: formData });
                let text = await response.text();

                document.getElementById("downloadLink").innerHTML = text;
            };

            // Handle AI music generation
            document.querySelector("#musicForm").onsubmit = async function(event) {
                event.preventDefault();
                let prompt = document.getElementById("prompt").value;
                
                let response = await fetch("/generate-music", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                let data = await response.json();
                if (data.file_url) {
                    document.getElementById("musicDownloadLink").innerHTML = `<a href="${data.file_url}" target="_blank">Click here to download generated music</a>`;
                } else {
                    document.getElementById("musicDownloadLink").innerHTML = "Failed to generate music.";
                }
            };

            // Handle Get Voices
            document.querySelector("#getVoicesButton").onclick = async function() {
                let response = await fetch("/get_voices");
                let data = await response.json();
                
                if (data && data.length > 0) {
                    let voicesHtml = "";
                    data.forEach(voice => {
                        voicesHtml += `
                            <div class="voice-card">
                                <h4>${voice.artist}</h4>
                                <button>Choose</button>
                            </div>
                        `;
                    });
                    document.getElementById("voicesList").innerHTML = voicesHtml;
                } else {
                    document.getElementById("voicesList").innerHTML = "No voices available.";
                }
            };
        </script>
    </body>
    </html>
    """

# Route to handle file upload
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        # Ensure the folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return f"File uploaded successfully! <a href='/download/{file.filename}'>Click here to download</a>"

# Route to serve the uploaded file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to generate AI music
@app.route("/generate-music", methods=["POST"])
def generate_music():
    data = request.get_json()
    prompt = data.get("prompt")
    
    # API request to generate music
    url = "https://api.musicfy.lol/v1/generate-music"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_KEY}"  # Include the access key in headers
    }
    payload = {"prompt": prompt}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        # Check if the response contains the file URL
        if response_data and "file_url" in response_data[0]:
            return jsonify({"file_url": response_data[0]["file_url"]})
        else:
            return jsonify({"error": "Failed to generate music"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get voices
@app.route("/get_voices", methods=["GET"])
def get_voices():
    # API request to get available voices
    url = "https://api.musicfy.lol/v1/voices"
    headers = {
        "Authorization": f"Bearer {ACCESS_KEY}"  # Include the access key in headers
    }

    try:
        response = requests.get(url, headers=headers)
        response_data = response.json()
        
        # Return the list of voices if available
        if response_data:
            return jsonify([voice for voice in response_data])
        else:
            return jsonify({"error": "No voices available"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

