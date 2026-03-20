import os
import json
import requests
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
OPENAI_KEY   = os.environ.get('OPENAI_KEY', '')
APP_SECRET   = os.environ.get('APP_SECRET', 'ledgermind-dennisys-2024')
OPENAI_URL   = 'https://api.openai.com/v1/chat/completions'
MODEL        = 'gpt-4o'
MAX_TOKENS   = 600
TEMPERATURE  = 0.5

# ─── Auth middleware ──────────────────────────────────────────────────────────
# The app sends X-App-Secret header — prevents random people hitting your relay

def require_app_secret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        secret = request.headers.get('X-App-Secret', '')
        if secret != APP_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# ─── Health check ─────────────────────────────────────────────────────────────

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'LedgerMind AI Relay',
        'powered_by': 'Dennisys',
        'timestamp': datetime.utcnow().isoformat(),
    })

# ─── Chat endpoint ────────────────────────────────────────────────────────────

@app.route('/chat', methods=['POST'])
@require_app_secret
def chat():
    if not OPENAI_KEY:
        return jsonify({'error': 'OpenAI key not configured on server'}), 500

    body = request.get_json(silent=True)
    if not body:
        return jsonify({'error': 'Invalid JSON body'}), 400

    messages      = body.get('messages', [])
    system_prompt = body.get('system_prompt', '')

    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    # Build the OpenAI payload
    openai_messages = []
    if system_prompt:
        openai_messages.append({'role': 'system', 'content': system_prompt})
    openai_messages.extend(messages)

    try:
        response = requests.post(
            OPENAI_URL,
            headers={
                'Authorization': f'Bearer {OPENAI_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': MODEL,
                'messages': openai_messages,
                'max_tokens': MAX_TOKENS,
                'temperature': TEMPERATURE,
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content']
            return jsonify({'reply': reply})
        elif response.status_code == 401:
            return jsonify({'error': 'Invalid OpenAI key on server'}), 502
        elif response.status_code == 429:
            return jsonify({'error': 'Rate limit reached. Please try again shortly.'}), 429
        else:
            return jsonify({'error': f'OpenAI error {response.status_code}'}), 502

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out. Please try again.'}), 504
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
