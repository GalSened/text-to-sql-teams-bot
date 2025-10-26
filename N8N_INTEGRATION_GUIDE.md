# 🔄 n8n Integration Guide for Text-to-SQL

## What is n8n?

n8n is a fair-code workflow automation tool that lets you visually build integrations. Think of it as Zapier but:
- ✅ Self-hosted (you control the data)
- ✅ Open source
- ✅ Can run locally
- ✅ Supports custom nodes

## Why Use n8n with Text-to-SQL?

### Benefits:
1. **Visual Workflow Designer**: Drag-and-drop AI logic
2. **Multi-Provider Testing**: Compare Claude vs OpenAI easily
3. **Advanced Routing**: Route queries based on complexity
4. **Logging & Monitoring**: Built-in execution history
5. **Error Handling**: Automatic retries and fallbacks
6. **Webhooks**: Easy integration with other tools
7. **Scheduling**: Automated report generation

---

## Installation Options

### Option 1: NPM (Quick Start)
```bash
npm install -g n8n
n8n
# Opens at http://localhost:5678
```

### Option 2: Docker (Recommended)
```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Option 3: Docker Compose (Production)
```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
      - WEBHOOK_URL=http://localhost:5678/
    volumes:
      - ~/.n8n:/home/node/.n8n
    restart: unless-stopped
```

---

## Integration Architecture

### Simple Workflow
```
Text-to-SQL App → n8n Webhook → Claude API → Return SQL
```

### Advanced Workflow with Multi-Provider
```
                    ┌─────────────┐
                    │ Text-to-SQL │
                    │     App     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   n8n       │
                    │  Webhook    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Router    │
                    │   (Switch)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐     ┌─────▼──────┐
   │ Claude  │       │  OpenAI   │     │   Human    │
   │   API   │       │    API    │     │  Approval  │
   └────┬────┘       └─────┬─────┘     └─────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Validator  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Execute   │
                    │     SQL     │
                    └─────────────┘
```

---

## Example n8n Workflows

### 1. Basic Text-to-SQL with Claude

**Workflow Steps**:
1. **Webhook Node**: Receive request
2. **HTTP Request Node**: Call Claude API
3. **Code Node**: Parse response
4. **Webhook Response**: Return SQL

**n8n JSON** (import this):
```json
{
  "name": "Text-to-SQL with Claude",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "text-to-sql",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "parameters": {
        "url": "https://api.anthropic.com/v1/messages",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "x-api-key",
              "value": "={{$credentials.anthropicApiKey}}"
            },
            {
              "name": "anthropic-version",
              "value": "2023-06-01"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "model",
              "value": "claude-3-5-sonnet-20241022"
            },
            {
              "name": "max_tokens",
              "value": 4096
            },
            {
              "name": "messages",
              "value": "={{[{role: 'user', content: $json.question}]}}"
            }
          ]
        }
      },
      "name": "Claude API",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{$json}}"
      },
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Claude API", "type": "main", "index": 0}]]
    },
    "Claude API": {
      "main": [[{"node": "Response", "type": "main", "index": 0}]]
    }
  }
}
```

---

### 2. Multi-Provider Comparison Workflow

**This workflow tests both Claude and OpenAI, compares results**:

**Steps**:
1. Webhook receives question
2. Split into two paths
3. Path A: Call Claude
4. Path B: Call OpenAI
5. Merge results
6. Compare SQL outputs
7. Return best result

---

### 3. Advanced Workflow with Validation

**Features**:
- Query complexity analysis
- Model selection based on complexity
- Multi-model validation for writes
- Human approval for risky operations
- Automatic logging to database

---

## Setting Up Text-to-SQL with n8n

### Step 1: Start n8n
```bash
n8n
# Opens http://localhost:5678
```

### Step 2: Create Credentials

1. Go to **Credentials** → **New**
2. Search for "HTTP Header Auth"
3. Add Claude API:
   - Name: `claude-api-key`
   - Header Name: `x-api-key`
   - Header Value: Your Claude API key

### Step 3: Create Workflow

1. **Add Webhook Node**:
   - Path: `text-to-sql`
   - Method: POST
   - Response Mode: "Using 'Respond to Webhook' node"

2. **Add HTTP Request Node** (Claude):
   - URL: `https://api.anthropic.com/v1/messages`
   - Method: POST
   - Authentication: Use credential from Step 2
   - Headers:
     - `anthropic-version`: `2023-06-01`
     - `content-type`: `application/json`
   - Body:
     ```json
     {
       "model": "claude-3-5-sonnet-20241022",
       "max_tokens": 4096,
       "system": "You are a SQL expert...",
       "messages": [
         {
           "role": "user",
           "content": "{{$json.question}}"
         }
       ]
     }
     ```

3. **Add Code Node** (Parse Response):
   ```javascript
   // Extract SQL from Claude response
   const response = items[0].json.content[0].text;
   const result = JSON.parse(response);

   return items.map(item => ({
     json: result
   }));
   ```

4. **Add Respond to Webhook Node**:
   - Response: `{{$json}}`

### Step 4: Test the Workflow

**Activate** the workflow, then test:

```bash
curl -X POST http://localhost:5678/webhook/text-to-sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me all customers",
    "schema": {...}
  }'
```

---

## Integrating n8n with Text-to-SQL App

### Option 1: Replace AI Client

Modify `app/core/ai_client.py`:

```python
class N8nAIClient:
    """Use n8n workflow as AI provider."""

    def __init__(self):
        self.n8n_webhook_url = settings.n8n_webhook_url

    def generate_sql(self, question, schema_info):
        import requests

        response = requests.post(
            self.n8n_webhook_url,
            json={
                "question": question,
                "schema": schema_info
            }
        )

        return response.json()
```

Add to `.env`:
```env
N8N_WEBHOOK_URL=http://localhost:5678/webhook/text-to-sql
USE_N8N=true
```

### Option 2: Add as Provider

Keep existing providers, add n8n as option:

```python
# In ai_client.py
if settings.use_n8n:
    self.providers['n8n'] = N8nAIClient()
```

---

## Advanced n8n Features

### 1. Query Caching

Add **Redis** or **Memory** node to cache results:
- Hash: Question + Schema
- Cache Hit: Return immediately
- Cache Miss: Generate SQL, store in cache

### 2. Rate Limiting

Add **Function** node to track API usage:
- Count requests per user
- Enforce limits
- Queue overflow requests

### 3. A/B Testing

Split traffic between providers:
- 50% → Claude
- 50% → OpenAI
- Compare quality metrics
- Adjust split based on results

### 4. Cost Tracking

Log token usage:
- Track per provider
- Calculate costs
- Alert on budget threshold

### 5. Human-in-the-Loop

For risky operations:
- Send to Slack/Email for approval
- Wait for response
- Execute only if approved

---

## n8n vs Direct API Integration

### Use n8n When:
✅ You want visual workflow design
✅ Need to compare multiple AI providers
✅ Want built-in monitoring/logging
✅ Need complex routing logic
✅ Want to integrate with other tools
✅ Need human approval steps
✅ Want no-code modifications

### Use Direct API When:
✅ Simple single-provider setup
✅ Need lowest latency
✅ Want minimal dependencies
✅ Have coding expertise
✅ Need fine-grained control

---

## Example: Complete n8n Setup

### 1. Install n8n
```bash
docker-compose up -d n8n
```

### 2. Configure Text-to-SQL
```env
# .env
PRIMARY_AI_PROVIDER=n8n
N8N_WEBHOOK_URL=http://localhost:5678/webhook/text-to-sql
```

### 3. Import Workflow
- Download workflow JSON (provided above)
- n8n → Import from File
- Configure credentials

### 4. Test Integration
```bash
python test_ai_providers.py
```

---

## Troubleshooting

### "Connection refused"
- Ensure n8n is running: `docker ps`
- Check port: `netstat -an | grep 5678`

### "Webhook not found"
- Activate workflow in n8n
- Check webhook URL matches

### "API key invalid"
- Verify credentials in n8n
- Test Claude API directly first

---

## Next Steps

1. **Install n8n**: `npm install -g n8n`
2. **Start n8n**: `n8n`
3. **Import workflow**: Use JSON above
4. **Configure credentials**: Add API keys
5. **Test**: Use curl or test script
6. **Integrate**: Update Text-to-SQL config

---

## Resources

- **n8n Docs**: https://docs.n8n.io/
- **n8n Community**: https://community.n8n.io/
- **Claude API Docs**: https://docs.anthropic.com/
- **Example Workflows**: https://n8n.io/workflows/

---

**Ready to use n8n?** Let me know if you want me to:
1. Set up n8n locally
2. Create a specific workflow
3. Integrate with the app
4. Build advanced features
