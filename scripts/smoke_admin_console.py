import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
DB_PATH = BACKEND_DIR / "chem_teacher.db"
FIXTURE_IMAGE = BACKEND_DIR / "uploads" / "fixture-ocr.png"
ADMIN_USERNAME = os.environ.get("ADMIN_SMOKE_USERNAME", "teacher1")
ADMIN_PASSWORD = os.environ.get("ADMIN_SMOKE_PASSWORD", "123456")
PORT = int(os.environ.get("ADMIN_SMOKE_PORT", "8016"))
STDOUT_LOG = ROOT_DIR / ".tmp_admin_smoke_backend.out.log"
STDERR_LOG = ROOT_DIR / ".tmp_admin_smoke_backend.err.log"


def json_request(url: str, method: str = "GET", payload: dict | None = None, token: str | None = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def text_request(url: str) -> tuple[int, str]:
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.status, response.read().decode("utf-8")


def ensure_fixture_image() -> None:
    FIXTURE_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    if FIXTURE_IMAGE.exists():
        return
    png_bytes = bytes(
        [
            137, 80, 78, 71, 13, 10, 26, 10,
            0, 0, 0, 13, 73, 72, 68, 82,
            0, 0, 0, 1, 0, 0, 0, 1,
            8, 6, 0, 0, 0, 31, 21, 196,
            137, 0, 0, 0, 13, 73, 68, 65,
            84, 120, 156, 99, 248, 255, 255, 63,
            0, 5, 254, 2, 254, 167, 53, 129,
            153, 0, 0, 0, 0, 73, 69, 78,
            68, 174, 66, 96, 130,
        ]
    )
    FIXTURE_IMAGE.write_bytes(png_bytes)


def ensure_ocr_fixture(user_id: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("delete from ocr_record where id = ?", ("ocradminfixture000000000000000001",))
    cur.execute(
        """
        insert into ocr_record (
            id, user_id, origin_image_url, ocr_result_raw, ocr_result_latex,
            ocr_result_text, ocr_engine, confidence, manual_corrections, created_at
        )
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "ocradminfixture000000000000000001",
            user_id,
            "/uploads/fixture-ocr.png",
            '{"demo": true}',
            "H_2O",
            "H2O",
            "tesseract",
            0.98,
            "[]",
            datetime.now().isoformat(sep=" "),
        ),
    )
    conn.commit()
    conn.close()


def resolve_backend_python() -> str:
    return os.environ.get("ADMIN_SMOKE_BACKEND_PYTHON", "").strip() or sys.executable


def tail_text(path: Path, max_chars: int = 1200) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8", errors="ignore")
    if len(content) <= max_chars:
        return content.strip()
    return content[-max_chars:].strip()


def build_backend_failure_message(process: subprocess.Popen, stdout_path: Path, stderr_path: Path) -> str:
    returncode = process.poll()
    stdout_tail = tail_text(stdout_path)
    stderr_tail = tail_text(stderr_path)
    parts = [f"backend exited with code {returncode}"]
    if stdout_tail:
        parts.append(f"stdout tail:\n{stdout_tail}")
    if stderr_tail:
        parts.append(f"stderr tail:\n{stderr_tail}")
    return "\n\n".join(parts)


def start_backend() -> subprocess.Popen:
    env = os.environ.copy()
    env["ADMIN_USERNAMES"] = ADMIN_USERNAME
    STDOUT_LOG.write_text("", encoding="utf-8")
    STDERR_LOG.write_text("", encoding="utf-8")
    stdout_handle = STDOUT_LOG.open("w", encoding="utf-8")
    stderr_handle = STDERR_LOG.open("w", encoding="utf-8")
    return subprocess.Popen(
        [
            resolve_backend_python(),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(PORT),
        ],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=stdout_handle,
        stderr=stderr_handle,
    )


def wait_for_health(server: subprocess.Popen) -> None:
    url = f"http://127.0.0.1:{PORT}/health"
    for _ in range(30):
        if server.poll() is not None:
            raise RuntimeError(build_backend_failure_message(server, STDOUT_LOG, STDERR_LOG))
        try:
            payload = json_request(url)
            if payload.get("status") == "ok":
                return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("backend health check failed")


def ensure_admin_seed(base_url: str) -> tuple[str, str]:
    register_payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "role": "teacher",
        "nickname": "后台联调老师",
        "school": "联调学校",
    }
    try:
        json_request(f"{base_url}/api/auth/register", method="POST", payload=register_payload)
    except urllib.error.HTTPError:
        pass

    login_payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
    }
    login_resp = json_request(f"{base_url}/api/auth/login", method="POST", payload=login_payload)
    return login_resp["data"]["access_token"], login_resp["data"]["user"]["id"]


def create_smoke_data(base_url: str, token: str) -> None:
    tag_name = f"联调知识点-{datetime.now().strftime('%H%M%S')}"
    tag_resp = json_request(
        f"{base_url}/api/admin/tags",
        method="POST",
        payload={"name": tag_name, "tag_type": "knowledge", "sort_order": 1},
        token=token,
    )
    tag_id = tag_resp["data"]["tag_id"]

    question_resp = json_request(
        f"{base_url}/api/questions",
        method="POST",
        payload={
            "content": "联调用选择题：下列关于 NaCl 的说法正确的是？",
            "answer": "A",
            "analysis": "联调解析",
            "question_type": "choice",
            "difficulty": 3,
            "source": "后台联调",
            "tag_ids": [tag_id],
            "options": [
                {"label": "A", "text": "属于离子化合物"},
                {"label": "B", "text": "常温下为气体"},
            ],
        },
        token=token,
    )
    question_id = question_resp["data"]["question_id"]

    json_request(
        f"{base_url}/api/papers/manual",
        method="POST",
        payload={
            "title": "联调试卷",
            "subtitle": "后台验证",
            "question_ids": [question_id],
            "total_score": 100,
            "exam_duration": 60,
        },
        token=token,
    )


def main() -> int:
    ensure_fixture_image()
    server = start_backend()
    try:
        wait_for_health(server)
        base_url = f"http://127.0.0.1:{PORT}"
        token, user_id = ensure_admin_seed(base_url)
        create_smoke_data(base_url, token)
        ensure_ocr_fixture(user_id)

        admin_status, admin_html = text_request(f"{base_url}/admin-console/")
        js_status, _ = text_request(f"{base_url}/admin-console/admin.js")
        css_status, _ = text_request(f"{base_url}/admin-console/asset-index.css")
        dashboard = json_request(f"{base_url}/api/admin/dashboard/summary", token=token)
        questions = json_request(f"{base_url}/api/admin/questions?page=1&page_size=10", token=token)
        tags = json_request(f"{base_url}/api/admin/tags", token=token)
        ocr_records = json_request(f"{base_url}/api/admin/ocr-records?page=1&page_size=10", token=token)
        system = json_request(f"{base_url}/api/admin/system/status", token=token)

        result = {
            "admin_index": admin_status,
            "admin_js": js_status,
            "admin_css": css_status,
            "html_has_console_title": "化学教学后台控制台" in admin_html,
            "question_count": dashboard["data"]["question_count"],
            "question_rows": len(questions["data"]["items"]),
            "tag_rows": len(tags["data"]),
            "ocr_rows": len(ocr_records["data"]["items"]),
            "system_health": system["data"]["health"],
        }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    finally:
        if server.poll() is None:
            server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
