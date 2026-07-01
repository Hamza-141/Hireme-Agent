# HireMe Agent

HireMe is an AI-powered job matching tool that helps users discover relevant job listings by combining the Adzuna Jobs API with Google's Generative AI. Built with Streamlit during an AI Agents hackathon, it takes a user's skills, interests, or resume details and surfaces tailored job matches with AI-generated insights on fit and relevance cutting through generic keyword search to give more personalized recommendations.
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
