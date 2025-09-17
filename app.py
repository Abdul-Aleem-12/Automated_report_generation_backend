from flask import Flask, request, jsonify, send_file
from services.db_service import get_vulnerabilities
from services.report_service import generate_report
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app)

# Directory for temporary downloads
DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Clean old leftover files on startup
for f in os.listdir(DOWNLOADS_DIR):
    try:
        os.remove(os.path.join(DOWNLOADS_DIR, f))
        print(f"Deleted old file: {f}")
    except Exception as e:
        print(f"Error deleting file {f}: {e}")

@app.route("/generate-report", methods=["POST"])
def generate_report_api():
    try:
        data = request.get_json()
        vulnerabilities = data.get("vulnerabilities", [])

        if not vulnerabilities:
            return jsonify({"status": "error", "message": "No vulnerabilities provided"}), 400

        vuln_data = get_vulnerabilities(vulnerabilities)

        # Create a timestamped filename
        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(DOWNLOADS_DIR, filename)

        # Generate the PDF report
        generate_report(vuln_data, filepath)

        return jsonify({
            "status": "success",
            "message": "Report generated",
            "file_url": f"/downloads/{filename}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/downloads/<filename>", methods=["GET"])
def download_file(filename):
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "File not found"}), 404

    try:
        # Send the file to the client
        response = send_file(file_path, as_attachment=True)
    finally:
        # Delete the file after serving
        try:
            os.remove(file_path)
            print(f"Deleted file after download: {file_path}")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
