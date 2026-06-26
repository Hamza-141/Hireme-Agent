# HireMe Agent

An AI-powered job search assistant that parses your CV and finds matching opportunities.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env` file and fill in your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
ADZUNA_APP_ID=your_adzuna_app_id_here
ADZUNA_APP_KEY=your_adzuna_app_key_here
ADZUNA_COUNTRY=gb
```

- **OPENAI_API_KEY**: Your OpenAI API key from [platform.openai.com](https://platform.openai.com/)
- **ADZUNA_APP_ID** / **ADZUNA_APP_KEY**: Your Adzuna API credentials from [developer.adzuna.com](https://developer.adzuna.com/)
- **ADZUNA_COUNTRY**: Country code for job searches (defaults to `gb` if not set)

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.
