from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import tempfile
import os
import uuid
import requests

from nudenet import NudeDetector

app = Flask(__name__)
api = Api(app)

detector = NudeDetector()

ALLOWED_EXTS = {"jpg", "jpeg", "png", "bmp", "webp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS


class Health(Resource):
    def get(self):
        return {"status": "ok"}


class Detect(Resource):
    def post(self):
        if "file" in request.files:
            f = request.files["file"]
            if f.filename == "":
                return {"error": "No file selected"}, 400
            if not allowed_file(f.filename):
                return {
                    "error": f"Unsupported file type. Allowed: {sorted(ALLOWED_EXTS)}"
                }, 415
            filename = secure_filename(f.filename)
            suffix = "." + filename.rsplit(".", 1)[1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                f.save(tmp.name)
                tmp_path = tmp.name

            try:
                detections = detector.detect(tmp_path)
                return {"ok": True, "detections": detections}
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        if request.is_json:
            data = request.get_json(silent=True) or {}
            image_url = data.get("image_url")
            if image_url:
                try:
                    r = requests.get(image_url, timeout=10)
                    if r.status_code != 200:
                        return {
                            "error": f"Could not fetch image_url (status {r.status_code})."
                        }
                    ext = os.path.splitext(image_url)[1].lower()
                    if ext.replace(".", "") not in ALLOWED_EXTS:
                        ext = ".jpg"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(r.content)
                        tmp_path = tmp.name
                    try:
                        detections = detector.detect(tmp_path)
                        return {"ok": True, "detections": detections}
                    finally:
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                except requests.RequestException as e:
                    return {"error": f"Failed to download image url: {str(e)}"}, 400

        return {"error": "Provide image"}, 400


class Hello(Resource):
    # GET request
    def get(self):
        return jsonify({"message": "hello world"})

    # POST
    def post(self):
        data = request.get_json()
        return jsonify({"data": data}), 201


class Square(Resource):
    def get(self, num):
        return jsonify({"square": num**2})


api.add_resource(Hello, "/")
api.add_resource(Square, "/square/<int:num>")
api.add_resource(Detect, "/detect")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
