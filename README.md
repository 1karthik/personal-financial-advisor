# Personal Financial Advisor with LangChain and FastAPI

## Overview
This is a sample project demonstrating a simple LangChain agent integrated with FastAPI for a personal financial advisor assistant.

The agent can:
- Answer financial planning queries
- Fetch stock prices (demo mode or using Alpha Vantage API)
- Do math calculations
- Explain basic financial concepts
- Process and analyze PDF documents
- Read and summarize CSV files

---

## Requirements

- Python 3.8+
- OpenAI API key (for the language model)
- (Optional) Alpha Vantage API key for real stock prices (https://www.alphavantage.co/)

---

## Setup Instructions

1. Clone or unzip the project files.

2. Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
ALPHAVANTAGE_API_KEY=your_alpha_vantage_api_key_here (optional)
```

5. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

6. The API will be running at `http://127.0.0.1:8000`

---

## Usage

### Query Endpoint
Send POST requests to `/query` with JSON body:

```json
{
  "query": "What is the current price of AAPL?"
}
```

For document analysis, include the filename:
```json
{
  "query": "What is the net profit",
  "filename": "sample_financial_summary.pdf"
}
```

For math calculations:
```json
{
  "query": "What is 5 * (3+2) ?"
}
```

### File Upload
Upload documents using the `/upload` endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/upload" -H "Content-Type: multipart/form-data" -F "file=@path/to/your/file.pdf"
```

Example with `curl` for querying:

```bash
curl -X POST "http://127.0.0.1:8000/query" -H "Content-Type: application/json" -d '{"query":"Explain compound interest"}'
```

You will get a JSON response like:

```json
{
  "response": "Compound interest is the interest on a loan or deposit calculated based on both the initial principal and the accumulated interest from previous periods."
}
```

---

## Notes

- The stock price tool uses dummy data if no Alpha Vantage API key is provided.
- The math tool evaluates simple math expressions safely.
- The concept explainer has some hardcoded definitions but can be extended.
- The OpenAI LLM is used for language understanding and generation.
- Supported file formats: PDF and CSV
- Uploaded files are stored in the `uploaded_docs` directory
