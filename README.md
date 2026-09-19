# 🤖 AI-Powered Discord Assistant

An AI-powered Discord chatbot built with Python that can hold conversations, search the internet for up-to-date information, and generate images directly inside Discord.

## 🚀 Features

- 💬 AI-powered conversational responses
- 🔎 Internet search using Tavily
- 🖼️ AI image generation using Pollinations AI
- 🤖 Discord bot integration
- ⚡ Groq-powered LLM responses
- 🧰 Tool-based AI workflow using LangChain
- 🔐 Environment-variable based API key management
- 📤 Automatically sends generated images directly to Discord
- 📄 Handles long Discord responses by splitting messages

## 🛠️ Tech Stack

- Python
- Discord.py
- Groq
- LangChain
- Tavily
- Pollinations AI
- aiohttp
- python-dotenv

## 🏗️ Project Structure

```text
AI-Powered-Discord-Assistant/
│
├── agent.py
├── bot.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── screenshots/
    └── discord-bot.png
````

## 📸 Demo

![Discord Bot Demo](Discord%20Bot%20Demo.png)

## ⚙️ How It Works

```text
User
  ↓
Discord Bot
  ↓
Groq LLM
  ↓
Intent Detection
  ├── Normal Question → AI Response
  │
  ├── Internet Search → Tavily
  │                         ↓
  │                    Search Results
  │                         ↓
  │                    Groq Summary
  │
  └── Image Request → Pollinations AI
                            ↓
                       Generated Image
                            ↓
                         Discord
```

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/Gargik283/AI-Powered-Discord-Assistant.git
cd AI-Powered-Discord-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project directory:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
POLLINATIONS_API_KEY=your_pollinations_api_key
DISCORD_TOKEN=your_discord_bot_token
```

### 5. Run the bot

```bash
python bot.py
```

Once the bot is running, send a message in your Discord server.

## 💡 Example Requests

### Normal Conversation

```text
Hello!
```

### Internet Search

```text
What are the latest developments in AI?
```

### Image Generation

```text
Generate a picture of a golden retriever puppy playing in a garden.
```

The generated image is automatically sent to the Discord channel.

## 🧰 Tool Workflow

The assistant routes requests based on the user's intent.

### 💬 Normal Conversation

The user's request is sent to the Groq-powered language model and a conversational response is returned directly to Discord.

### 🔎 Internet Search

Search-related requests are routed to the Tavily search tool.

The retrieved information is then passed back to the language model to generate a clear and useful response.

### 🖼️ Image Generation

Image-related requests are converted into a detailed image prompt and sent to Pollinations AI.

The generated image is downloaded and uploaded directly to the Discord channel.

## 🔐 Security

API keys are stored using environment variables and are not included in the repository.

Make sure `.env` is included in `.gitignore`.

Never commit:

```text
.env
```

Use `.env.example` to show the required environment variables without exposing your actual credentials.

## 📌 Future Improvements

* Add conversation memory
* Add more AI tools
* Add Discord slash commands
* Add richer Discord embeds
* Add voice interaction
* Add persistent conversation history
* Add additional image-generation controls
* Improve error handling and logging
* Add more advanced agent-based tool routing

## 👩‍💻 Author

**Gargi Kundu**

GitHub: [https://github.com/Gargik283](https://github.com/Gargik283)
