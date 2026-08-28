# PROJECT ULTRON — Environment Variables Reference

| Variable Name | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `mysql+aiomysql://root:password@localhost:3306/ultron` | Async MySQL connection URI |
| `JWT_SECRET` | `SUPER_SECRET_PRODUCTION_KEY` | Secret key for signing access & refresh tokens |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Short-lived token expiration duration |
| `AI_PROVIDER` | `gemini` | Configured AI provider (`gemini`, `openai`, `anthropic`, `mock`) |
| `AI_MODEL_NAME` | `gemini-2.5-flash` | Default target model identifier |
| `AI_API_KEY` | `""` | Provider API key |
| `MAX_WORKFLOW_DURATION` | `600` | Hard cap on execution runtime in seconds |
| `MAX_TOOL_CALLS` | `50` | Hard limit on tool invocations per workflow |
| `MAX_BROWSER_ACTIONS` | `20` | Max Playwright browser steps per execution |
| `MAX_COMPUTER_ACTIONS` | `15` | Max visual grounding computer perception actions |
