# MYMFIT AI

### Your Body. Your Goals. Your Journey.

MYMFIT AI is an AI-powered personal fitness and wellness assistant designed to help women receive personalised fitness guidance, practical nutrition suggestions and motivational support.

The application uses conversational AI to understand user goals and provide recommendations based on their preferences and circumstances.

## Project Information

- Institution: WeCan Academy
- Course: Artificial Intelligence
- Season: 12
- Group: Jupiter Group
- Project: AI-Powered Smart Assistant with Memory
- Deadline: 27 November 2026

## Features

- AI-powered fitness coaching
- Conversational memory
- Structured JSON responses
- JSON validation and automatic retry
- AI-generated session summaries
- Conversation storage
- SQLite response caching
- Kenyan food and lifestyle context

## Technologies

- Python
- Anthropic Claude API
- SQLite
- JSON
- Git and GitHub

## Project Structure

```text
mymfit-ai/
├── ai/
├── memory/
├── cache/
├── tests/
├── main.py
├── requirements.txt
├── .gitignore
└── README.md


## Installation

1. **Clone the repository:**
   ```bash
   git clone YOUR_REPOSITORY_URL
   ```

2. **Enter the project directory:**
   ```bash
   cd YOUR_PROJECT_FOLDER
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```
   *(On Windows Command Prompt, use `venv\Scripts\activate` instead.)*

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## API Configuration

1. Create a `.env` file in the root of your project directory:
   ```bash
   touch .env
   ```

2. Add your Anthropic API key to the `.env` file, replacing the placeholder with your actual key:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

> **Security Note:** Never commit or upload your `.env` file to GitHub. Ensure `.env` is listed in your `.gitignore` file.

---

## Running the Command-Line Application

With your virtual environment activated, launch the application:

```bash
python main.py
```
## Responsible AI
MYMFIT AI gives general fitness and wellness guidance only. It is not
a substitute for professional medical advice, diagnosis or treatment.
 
## Acknowledgement
Developed for the WeCan Academy Season 12 Group Project as a complete project

