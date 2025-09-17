from flask import Flask, request, jsonify, send_file
from services.db_service import get_vulnerabilities
from services.report_service import generate_report
from flask_cors import CORS
import datetime
import os

app = Flask(__name__)
CORS(app)

@app.route("/generate-report", methods=["POST"])
def generate_report_api():
    try:
        data = request.get_json()
        vulnerabilities = data.get("vulnerabilities", [])

        if not vulnerabilities:
            return jsonify({"status": "error", "message": "No vulnerabilities provided"}), 400
        

        vuln_data = get_vulnerabilities(vulnerabilities) 

        filename = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)  
        filepath = os.path.join(downloads_dir, filename)

        generate_report(vuln_data, filepath)


        return jsonify({
            "status": "success",
            "message": "Report generated",
            "file_url": f"/downloads/{filename}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to serve generated files
@app.route("/downloads/<filename>", methods=["GET"])
def download_file(filename):
    return send_file(os.path.join("downloads", filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
