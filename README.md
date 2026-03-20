# LedgerMind AI Relay Server
**Built by Dennisys** · hello@dennisys.co.za

A lightweight Flask proxy that sits between the LedgerMind app and OpenAI.
Your API key lives only on the server — never in the APK.

---

## Deploy to Render (5 minutes)

### 1. Push to GitHub
Create a new GitHub repo and push this folder to it.

### 2. Create Render Web Service
1. Go to **render.com** and sign in
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Render auto-detects Python — leave all settings as default
5. Click **Create Web Service**

### 3. Add Environment Variables
In your Render service dashboard → **Environment**:

| Key | Value |
|-----|-------|
| `OPENAI_KEY` | `sk-your-openai-key-here` |
| `APP_SECRET` | `any-secret-string-you-choose` |

### 4. Get your URL
Once deployed, your URL will be:
`https://ledgermind-api.onrender.com`

Copy this URL and the APP_SECRET into the Flutter app config.

---

## Endpoints

### GET /
Health check — returns service status.

### POST /chat
Proxies a chat message to OpenAI GPT-4o.

**Headers:**
```
X-App-Secret: your-app-secret
Content-Type: application/json
```

**Body:**
```json
{
  "system_prompt": "You are Ledger AI...",
  "messages": [
    {"role": "user", "content": "How is my budget?"}
  ]
}
```

**Response:**
```json
{
  "reply": "Your food budget is at 82%..."
}
```

---

## Security
- `X-App-Secret` header required on all `/chat` requests
- OpenAI key never exposed to client
- Rate limiting can be added via Render or a Flask middleware
