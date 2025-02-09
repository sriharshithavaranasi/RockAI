import os
from flask import Flask, request, send_from_directory, jsonify, url_for
import requests

app = Flask(__name__)

# Folder where the uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Your API Access Key (
# Ensure it’s correct and has permissions)
ACCESS_KEY = "cm6wfjbgp0001ky0c0ievtcxz"

# Check if the uploads folder has the correct permissions
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                background-color: #7B61FF;
                color: #FFFFFF;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                flex-direction: column;
                font-color: black;
            }
            .container {
                width: 80%;
                max-width: 900px;
                padding: 20px;
                background-color: #9a72ff;
                box-shadow: 0px 0px 10px rgb(0, 0, 0);
                border-radius: 8px;
                text-align: center;
            }
            h1 {
                color: #000;
                margin-top: 20px;
                font-size: 32px;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 30px;
            }
            input[type="file"], input[type="text"] {
                padding: 10px;
                margin: 10px;
                width: 70%;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            button {
                padding: 10px 20px;
                background-color: #6A4CFF;
                color: black;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #5730d4;
            }
            #downloadLink, #musicDownloadLink, #voicesList {
                text-align: center;
                margin-top: 20px;
            }
            a {
                color: #FF7F50;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .header-image {
                width: 100%;
                height: 200px;
                background-image: url('https://i.postimg.cc/RCfMJLLX/Screenshot-2025-02-08-at-10-09-05-PM.png'); 
                background-size: cover;
                background-position: center;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .interactive-section {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                margin-top: 30px;
            }
            .card {
                width: 200px;
                padding: 20px;
                background-color:rgb(3, 1, 3);
                box-shadow: 0 2px 5px rgb(255, 255, 255);
                border-radius: 8px;
                text-align: center;
                margin-bottom: 20px;
                transition: all 0.3s;
            }
            .card:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 10px rgb(255, 255, 255);
            }
            .card img {
                width: 100%;
                height: 100px;
                object-fit: cover;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-image"></div>
            <h1>MP3 Uploader and AI Music Generator</h1>

            <div class="interactive-section">
                <div class="card">
                    <h3>Upload MP3</h3>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".mp3" required>
                        <button type="submit">Upload</button>
                    </form>
                    <div id="downloadLink"></div>
                </div>

                <div class="card">
                    <h3>Generate Music</h3>
                    <form id="musicForm">
                        <input type="text" id="prompt" placeholder="Enter your music prompt" required>
                        <button type="submit">Generate</button>
                    </form>
                    <div id="musicDownloadLink"></div>
                </div>

                <div class="card">
                    <h3>Get Available Voices</h3>
                    <button id="getVoicesButton">Get Voices</button>
                    <div id="voicesList"></div>
                </div>
            </div>
        </div>

        <script>
            // Handle file upload
            document.getElementById("uploadForm").onsubmit = async function(event) {
                event.preventDefault();
                let formData = new FormData();
                formData.append("file", document.getElementById("fileInput").files[0]);

                let response = await fetch("/upload", { method: "POST", body: formData });
                let data = await response.json();

                if (data.file_url) {
                    document.getElementById("downloadLink").innerHTML = 
                        `<p><a href="${data.file_url}" target="_blank">Click here to download</a></p>`;
                } else {
                    document.getElementById("downloadLink").innerHTML = "<p style='color: red;'>Upload failed.</p>";
                }
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
                    let voicesHtml = "<ul>";
                    data.forEach(voice => {
                        voicesHtml += `<li>${voice.artist}</li>`;
                    });
                    voicesHtml += "</ul>";
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
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        # Ensure the folder exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Log the file path for debugging
        print(f"Saving file to {file_path}")

        # Generate download link using url_for
        download_url = url_for('download_file', filename=file.filename, _external=True)
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Uploaded</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                a {{ color: blue; text-decoration: underline; font-weight: bold; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h2>File uploaded successfully!</h2>
            <p><a href="{download_url}" target="_blank">Click here to download</a></p>
        </body>
        </html>
        """

# Route to serve the uploaded file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

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

# Route to get voices (top 10 voices)
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

        # Return the list of top 10 voices if available
        if response_data:
            top_10_voices = response_data[:10]  # Slice to get only the first 10 voices
            return jsonify([voice for voice in top_10_voices])
        else:
            return jsonify({"error": "No voices found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
