# Telegram OpenAI Chatbot

A secure, production-ready Telegram bot powered by OpenAI's GPT models. Built with Python, featuring comprehensive input validation, rate limiting, and session management.

## 🎬 Demo

**Video:** [Watch 51-second demo on YouTube Shorts](https://youtube.com/shorts/ZC6TKKdAF5U)

**Try the bot:** [@sami_demo_bot](https://t.me/sami_demo_bot)


![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)

## Features

### Core Functionality
- **AI-Powered Chat** - Natural conversations using OpenAI GPT models
- **Context Awareness** - Remembers last 5 messages for coherent conversations
- **Real-time Responses** - Fast responses with typing indicators
- **Notification System** - Demo webhook integration for external alerts

### Security & Performance
- **Input Validation** - Comprehensive sanitization of all user input
- **Rate Limiting** - Spam protection (10 messages/minute per user)
- **Secure API Handling** - Environment-based configuration, no hardcoded keys
- **Error Handling** - Graceful degradation with user-friendly error messages
- **Automatic Cleanup** - Session expiry after 1 hour of inactivity

### User Experience
- **Inline Buttons** - Quick actions for common tasks
- **Session Management** - Persistent chat history during active sessions
- **Customizable Settings** - Configurable AI parameters
- **Usage Statistics** - Track message count and session info

## Technology Stack

- **Python 3.8+**
- **python-telegram-bot 20.7** - Telegram Bot API wrapper
- **OpenAI API** - GPT-4o-mini for AI responses
- **python-dotenv** - Environment variable management

## Project Structure
```
telegram-openai-bot/
├── bot.py                  # Main application entry point
├── config.py               # Configuration management with validation
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.example           # Environment template
├── handlers/
│   ├── __init__.py
│   ├── commands.py        # Command handlers (/start, /help, etc.)
│   └── chat.py            # Message handler with OpenAI integration
├── utils/
│   ├── __init__.py
│   ├── validators.py      # Input validation and sanitization
│   ├── rate_limiter.py    # Spam prevention
│   ├── session.py         # Chat history management
│   └── openai_client.py   # OpenAI API wrapper with error handling
└── screenshots/           # Demo images for documentation
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Telegram account
- OpenAI API account with credits

### Setup Steps

1. **Clone the repository**
```bash
   git clone https://github.com/Xmas178/telegram-openai-bot.git
   cd telegram-openai-bot
```

2. **Create virtual environment**
```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
   cp .env.example .env
   # Edit .env with your API keys
```

5. **Get Telegram Bot Token**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the token to `.env` file

6. **Get OpenAI API Key**
   - Visit https://platform.openai.com/api-keys
   - Create new API key
   - Add $10+ credits to your account
   - Copy the key to `.env` file

7. **Run the bot**
```bash
   python3 bot.py
```

## Configuration

Edit `.env` file to customize bot behavior:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini          # Model: gpt-4o-mini, gpt-4o, gpt-4
OPENAI_MAX_TOKENS=150             # Response length (50-2000)
OPENAI_TEMPERATURE=0.7            # Creativity (0.0-1.0)

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=10        # Spam protection threshold
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with quick action buttons |
| `/help` | Display all available commands and features |
| `/reset` | Clear chat history and start fresh conversation |
| `/settings` | View current AI configuration and session info |
| `/notify` | Test notification feature (webhook demo) |

## Usage Examples

### Basic Chat
```
User: What's the weather like?
Bot: I don't have access to real-time weather data, but I can help you
     understand weather concepts or suggest weather apps!
```

### Context-Aware Conversation
```
User: Tell me about Python
Bot: Python is a high-level programming language...

User: What are its main advantages?
Bot: Based on our discussion about Python, its main advantages are...
```

## Security Features

### Input Validation
- Maximum message length: 500 characters
- XSS prevention: HTML/script tag stripping
- SQL injection detection
- Command injection prevention

### Rate Limiting
- 10 messages per minute per user
- Automatic user notification when limit reached
- Individual user tracking (no global impact)

### API Key Protection
- Environment-based configuration
- Keys never exposed in code or logs
- Sanitized logging (redacts sensitive data)

## Error Handling

The bot gracefully handles:
- OpenAI API failures (with retry logic)
- Rate limit errors (user-friendly messages)
- Invalid input (validation feedback)
- Network timeouts (automatic retry)
- Unexpected errors (generic error messages)

## Development

### Running Tests
Each module includes self-test functionality:
```bash
# Test configuration
python3 config.py

# Test validators
python3 utils/validators.py

# Test rate limiter
python3 utils/rate_limiter.py

# Test session manager
python3 utils/session.py

# Test OpenAI client
python3 utils/openai_client.py
```

### Code Style
- English comments and documentation
- Type hints where applicable
- Comprehensive docstrings
- Security-first approach

## Cost Estimation

### OpenAI API Costs (GPT-4o-mini)
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Typical costs:**
- Average message: ~$0.0001 per exchange
- 1,000 messages: ~$0.10
- 10,000 messages: ~$1.00

**$10 credits provide:**
- Approximately 10,000-15,000 message exchanges
- Perfect for testing and small-scale deployment

## Deployment

### Local Development
```bash
python3 bot.py
# Keep terminal running
```

### Production Deployment
For 24/7 operation, consider:
- **Render.com** - Free tier with webhook mode
- **Railway.app** - Simple deployment
- **DigitalOcean** - $5/month droplet
- **AWS/GCP** - More advanced setups

## Customization Ideas

### For Client Projects
- Add custom commands (e.g., `/weather`, `/crypto`)
- Integrate external APIs (weather, stock prices, news)
- Database persistence (PostgreSQL, MongoDB)
- Admin panel for configuration
- Multi-language support
- Payment integration (Stripe, PayPal)

### Example Custom Command
```python
# In handlers/commands.py
async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = context.args[0] if context.args else "Helsinki"
    # Call weather API
    # Format and send response
```

## Troubleshooting

### Bot doesn't respond
- Check if bot is running (`python3 bot.py`)
- Verify `.env` file has correct tokens
- Check OpenAI credits balance

### "Invalid request to AI service"
- Verify OpenAI API key is correct
- Check model name in `.env` (use `gpt-4o-mini`)
- Ensure OpenAI account has credits

### Rate limit errors
- Adjust `MAX_REQUESTS_PER_MINUTE` in `.env`
- Use `/reset` command to clear rate limit

## Contributing

This is a portfolio/demo project, but suggestions are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details

## Author

**Sami Tommilammi**
- Portfolio: [tommilammi.fi](https://tommilammi.fi)
- GitHub: [@Xmas178](https://github.com/Xmas178)

## Acknowledgments

- OpenAI for GPT API
- python-telegram-bot community
- CodeNob Dev principles for secure coding practices

## Roadmap

- Add webhook deployment guide
- Docker containerization
- Database integration for persistent history
- Admin dashboard
- Multi-bot support
- Webhook notifications from external services
- Analytics and usage statistics

---

**Built with secure coding principles**

*Last updated: November 2025*
