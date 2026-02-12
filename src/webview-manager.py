from flask import Flask, render_template_string, request, jsonify
import subprocess
import os
import json
from datetime import datetime
import threading

import socket

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

app = Flask(__name__)

# --- Configurations ---
PSScriptRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAILBOX_DIR = os.path.join(PSScriptRoot, "data", "mailbox")
INBOX_DIR = os.path.join(MAILBOX_DIR, "inbox")
SENT_DIR = os.path.join(MAILBOX_DIR, "sent")

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(SENT_DIR, exist_ok=True)

# --- Helper Functions ---
def run_command(command):
    """Run shell command and return output"""
    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        stdout, stderr = process.communicate()
        return {"status": "success" if process.returncode == 0 else "error", "output": stdout, "error": stderr}
    except Exception as e:
        return {"status": "error", "output": "", "error": str(e)}

# --- API Endpoints ---
@app.route('/api/actions', methods=['POST'])
def handle_action():
    data = request.json
    action = data.get('action')
    
    commands = {
        "cleanup": "docker system prune -a -f && docker builder prune -a -f && docker buildx prune -f --all",
        "build": "docker build -t snsw-ai-image -f Dockerfile.optimized .",
        "load": "docker run --rm -v C:\\Models\\TTS:/app/models snsw-ai-image python3 src/setup-common-env.py",
        "tts": "docker run --rm -v " + PSScriptRoot + ":/app -v C:\\Models\\TTS:/app/models snsw-ai-image python3 src/tts-multi-selector.py",
        "image": "docker run --rm -v " + PSScriptRoot + ":/app snsw-ai-image python3 src/image-generator.py"
    }
    
    cmd = commands.get(action)
    if not cmd:
        return jsonify({"status": "error", "error": "Invalid action"})
    
    # Run in background to avoid timeout
    result = run_command(cmd)
    return jsonify(result)

@app.route('/api/mailbox', methods=['GET'])
def get_mailbox():
    mails = []
    if os.path.exists(SENT_DIR):
        for f in sorted(os.listdir(SENT_DIR), reverse=True):
            if f.endswith(".json"):
                with open(os.path.join(SENT_DIR, f), "r", encoding="utf-8") as file:
                    mails.append(json.load(file))
    return jsonify(mails)

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.json
    order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    order_data = {
        "id": order_id,
        "timestamp": datetime.now().isoformat(),
        "subject": data.get('subject', 'No Subject'),
        "body": data.get('body', ''),
        "status": "pending"
    }
    file_path = os.path.join(INBOX_DIR, f"{order_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(order_data, f, indent=4, ensure_ascii=False)
    return jsonify({"status": "success", "id": order_id})

# --- HTML Template (Single File JS/CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SNSW-AI WebView Manager</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 15px; }
        .container { display: flex; flex-direction: column; gap: 20px; }
        .section { border: 1px solid #333; padding: 15px; border-radius: 8px; background: #252526; }
        h2 { margin-top: 0; color: #007acc; border-bottom: 1px solid #333; padding-bottom: 5px; font-size: 1.2em; }
        .btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        button { background: #0e639c; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; transition: 0.2s; }
        button:hover { background: #1177bb; }
        button:disabled { background: #444; cursor: not-allowed; }
        .console { background: #000; color: #0f0; padding: 10px; font-family: monospace; height: 150px; overflow-y: auto; border-radius: 4px; margin-top: 10px; font-size: 0.85em; }
        .mail-item { border-left: 3px solid #007acc; background: #2d2d2d; padding: 10px; margin-bottom: 10px; border-radius: 0 4px 4px 0; }
        .mail-meta { font-size: 0.75em; color: #888; }
        .mail-body { margin-top: 5px; font-size: 0.9em; }
        .input-group { display: flex; flex-direction: column; gap: 8px; }
        input, textarea { background: #3c3c3c; border: 1px solid #555; color: white; padding: 8px; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Control Panel -->
        <div class="section">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h2>🛠 Quick Actions</h2>
                <div id="access-info"></div>
            </div>
            <div class="btn-grid">
                <button onclick="runAction('cleanup')">Clean System</button>
                <button onclick="runAction('build')">Build Image</button>
                <button onclick="runAction('load')">Load Models</button>
                <button onclick="runAction('tts')">Run TTS</button>
                <button onclick="runAction('image')">Run Image Gen</button>
            </div>
            <div id="console" class="console">Ready for commands...</div>
        </div>

        <!-- Mailer Panel -->
        <div class="section">
            <h2>📧 New Order (Mail)</h2>
            <div class="input-group">
                <input type="text" id="subject" placeholder="Subject (e.g. 風景画の作成)">
                <textarea id="body" rows="3" placeholder="Prompt details..."></textarea>
                <button onclick="sendOrder()">Send Request</button>
            </div>
        </div>

        <!-- Delivery Panel -->
        <div class="section">
            <h2>📦 Deliveries <button onclick="loadMailbox()" style="font-size: 0.7em; padding: 2px 8px;">Refresh</button></h2>
            <div id="mailbox">Loading deliveries...</div>
        </div>
    </div>

    <script>
        const log = (msg) => {
            const c = document.getElementById('console');
            c.innerHTML += `<div>[${new Date().toLocaleTimeString()}] ${msg}</div>`;
            c.scrollTop = c.scrollHeight;
        };

        async function runAction(action) {
            log(`Running action: ${action}...`);
            const btns = document.querySelectorAll('button');
            btns.forEach(b => b.disabled = true);
            
            try {
                const res = await fetch('/api/actions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action})
                });
                const data = await res.json();
                if (data.status === 'success') {
                    log(`SUCCESS: ${action} completed.`);
                } else {
                    log(`ERROR: ${data.error || 'Unknown error'}`);
                }
            } catch (e) {
                log(`FETCH ERROR: ${e}`);
            }
            btns.forEach(b => b.disabled = false);
        }

        async function sendOrder() {
            const subject = document.getElementById('subject').value;
            const body = document.getElementById('body').value;
            if(!subject || !body) return alert("Please fill both fields");

            log("Sending order...");
            const res = await fetch('/api/order', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({subject, body})
            });
            const data = await res.json();
            if(data.status === 'success') {
                log(`Order ${data.id} sent!`);
                document.getElementById('subject').value = '';
                document.getElementById('body').value = '';
            }
        }

        async function loadMailbox() {
            const res = await fetch('/api/mailbox');
            const mails = await res.json();
            const box = document.getElementById('mailbox');
            if (mails.length === 0) {
                box.innerHTML = "No deliveries yet.";
                return;
            }
            box.innerHTML = mails.map(m => `
                <div class="mail-item">
                    <div class="mail-meta">FROM: ${m.from} | ${m.delivered_at}</div>
                    <div style="font-weight:bold">RE: ${m.subject}</div>
                    <div class="mail-body">${m.body}</div>
                    <div style="color:#0f0; font-size:0.8em; margin-top:5px">✓ Delivered: ${m.artifacts.image}</div>
                </div>
            `).join('');
        }

        async function getAccessInfo() {
            const res = await fetch('/api/access');
            const data = await res.json();
            document.getElementById('access-info').innerHTML = `
                <div style="background:#333; padding:5px; border-radius:4px; font-size:0.8em;">
                    Mobile Access: http://${data.ip}:7860
                </div>
            `;
        }

        // Initial load
        loadMailbox();
        getAccessInfo();
    </script>
</body>
</html>
"""

@app.route('/api/access')
def get_access():
    return jsonify({"ip": get_ip_address()})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Run Flask on 7860 and listen on all interfaces (0.0.0.0) for mobile access
    ip = get_ip_address()
    print(f"\n" + "="*50)
    print(f" SNSW-AI WebView Manager is running!")
    print(f" Local:  http://localhost:7860")
    print(f" Mobile: http://{ip}:7860")
    print(f"="*50 + "\n")
    app.run(host='0.0.0.0', port=7860, debug=True)
