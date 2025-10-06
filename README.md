# NudeNet NSFW Tagging API

A simple REST API built with [Flask](https://flask.palletsprojects.com/) and [NudeNet](https://github.com/notAI-tech/NudeNet) for detecting and tagging NSFW content in images.  
Supports **file uploads** and **remote image URLs** (single or multiple).

---

## Features

- 🔥 **Fast inference** — NudeNet model preloaded at container startup
- 🖼️ **Flexible input** — Upload files or pass one/many image URLs
- ⚡ **Production-ready** — Gunicorn + Dockerfile included
- 🛡️ **Safe defaults** — File type validation, max batch size, download timeouts
- ✅ **Health check** — `/health` endpoint for container orchestration

---

## API Endpoints

### Health check
```bash
GET /health
```
Returns:

```json
{ "status": "ok" }
```

### Detect NSFW (single file)

```bash
POST /detect
Content-Type: multipart/form-data
Form field: file=@/path/to/image.jpg
```

Example:

```bash
curl -X POST http://localhost:8080/detect \
  -F "file=@/path/to/image.jpg"
```

### Detect NSFW (multiple files)

```bash
POST /detect
Content-Type: multipart/form-data
Form field: files=@/path/to/a.jpg & files=@/path/to/b.png
```

### Detect NSFW (single URL)

```bash
POST /detect
Content-Type: application/json
Body:
{
  "image_url": "https://example.com/image.jpg"
}
```

### Detect NSFW (multiple URLs)

```bash
POST /detect
Content-Type: application/json
Body:
{
  "image_urls": [
    "https://example.com/a.jpg",
    "https://example.com/b.png"
  ]
}
```

---

## Responses

```json
{
  "ok": true,
  "mode": "urls",
  "count": 2,
  "results": [
    {
      "source": "https://example.com/a.jpg",
      "detections": [
        { "class": "EXPOSED_ANUS", "score": 0.98, "box": [0.2, 0.3, 0.5, 0.7] }
      ]
    },
    {
      "source": "https://example.com/b.png",
      "error": "HTTP 404"
    }
  ]
}
```

* `detections`: each detection contains `class` (NSFW label), `score` (confidence), and `box` (normalized bounding box `[x_min, y_min, x_max, y_max]`).
* `error`: returned if the file/URL failed.

---

## Local Development

### 1️⃣ Clone & install

```bash
git clone https://github.com/yourusername/nsfw-tagging-api.git
cd nsfw-tagging-api
pip install -r requirements.txt
```

### 2️⃣ Run (dev mode)

```bash
python app.py
# or specify port:
python app.py --port 8080
```

Server runs at `http://127.0.0.1:8080`.

---

## Docker

### Build

```bash
docker build -t nsfw-tagging-api .
```

### Run

```bash
docker run --rm -p 8080:8080 nsfw-tagging-api
```

### Test

```bash
curl -X POST http://127.0.0.1:8080/detect \
  -F "file=@/path/to/image.jpg"
```

---

## Deployment (Fly.io Example)

```bash
flyctl launch        # detect port 8080
flyctl deploy
```

Example `fly.toml` snippet:

```toml
[http_service]
  internal_port = 8080
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
```

---

## Environment

* Python 3.11+
* Flask + Flask-RESTful
* NudeNet (downloads pretrained models)
* Requests

Ensure your container/machine has enough memory (>=512 MB recommended).

---

## License

MIT © 2025 [Hrishikesh Kanade]
