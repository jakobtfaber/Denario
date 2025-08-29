# API keys

Denario requires access to large language models (LLMs) to function. Currently, Denario supports LLMs from Google (Gemini series), OpenAI (GPT and o series), Anthropic (Claude), Perplexity (Sonar), and agents from [Futurehouse](https://platform.futurehouse.org/) (Owl). Access to all these models is not mandatory for experimentation; however, **at least OpenAI API access is required**, so an OpenAI API key must be configured.

API access is managed via keys generated on each provider's platform and set as environment variables. Most LLM providers require a small amount of credit to be added to your account, as usage typically incurs a cost (though this is relatively minor for experimentation).

The required and optional models for Denario's subsystems are summarized below:

| Subsystem         | Required Models           | Optional Models                                         |
|-------------------|--------------------------|---------------------------------------------------------|
| Research Ideas    | OpenAI (gpt-4o-mini)     | Gemini (gemini-2.5-pro), Claude (claude-3.7-sonnet)     |
| Literature Search | OpenAI (gpt-4o-mini)     | Gemini (gemini-2.5-pro), Claude (claude-3.7-sonnet)     |
| Analysis          | OpenAI (gpt-4o-mini)     | Gemini (gemini-2.5-pro), Claude (claude-3.7-sonnet)     |
| Paper Writing     | OpenAI (gpt-4o-mini)     | Gemini (gemini-2.5-pro), Claude (claude-3.7-sonnet)     |


---

### How Much Money Is Needed?

With \$10, it is possible to generate hundreds of ideas, methods, and draft hundreds of papers, provided the analysis has already been completed. Running analyses (i.e., obtaining actual results) remains inexpensive when using lightweight models such as gpt-4o-mini. Most papers produced with the first public release of Denario were generated using either gemini-2.5-pro or gpt-4.1, which are more resource-intensive and costly. Generating research analysis for a single idea typically costs around \$2–\$5 with these models.

---

### Risk of Overspending

Careful monitoring of LLM provider usage is essential. API keys should never be shared, and it is important to supervise Denario's output to avoid unnecessary expenses, such as the system getting stuck on an indentation bug or other irrelevant issues. The same precautions apply as with other AI automation tools, such as Claude Code or Cursor agents.

---

### Rate Limits

New users are likely to encounter token rate limits when using OpenAI models. This may cause Denario to pause temporarily if too much text or code is generated. To increase token rate limits, refer to [OpenAI's rate limit documentation](https://platform.openai.com/docs/guides/rate-limits).

---


## Obtaining API Keys

### OpenAI API Key

To obtain an OpenAI API key, visit [this page](https://platform.openai.com/api-keys) and follow the instructions.

### Gemini API Key

To obtain a Gemini API key, visit [this page](https://ai.google.dev/gemini-api/docs/api-key) and follow the link to Google AI Studio to generate your key.

### Anthropic API Key

To obtain an Anthropic API key, visit [this page](https://console.anthropic.com/settings/keys) and follow the instructions.

### Perplexity API Key

To obtain a Perplexity API key, visit [this page](https://docs.perplexity.ai/getting-started/quickstart) and follow the instructions.

---

## Vertex AI Setup

Denario agents built with LangGraph can be run using a Gemini API key (see above). However, agents built using [AG2](https://ag2.ai/) require a different setup to access Gemini models via the [Vertex AI](https://cloud.google.com/vertex-ai?hl=en) API.

If you plan to run the analysis module with Gemini models accessed through Vertex AI, for example:

```python
den.get_results(engineer_model='gemini-2.5-pro',
                researcher_model='gemini-2.5-pro')
```

the following steps are required:

1. **Create a Google service account key file** (JSON format; see instructions below).
2. **Download** the file to the machine where Denario will run.
3. **Rename** the file to `gemini.json`.
4. **Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable** to the path of this file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gemini.json
```

This environment variable must be set whenever Denario requires Vertex AI access.

#### Enabling Vertex AI

1. **Google Account**: If you do not have a Google account, create one [here](https://www.google.com/intl/en-GB/account/about/).
2. **Google Cloud Console**: Log in at [Google Cloud Console](https://console.cloud.google.com/).

#### Create a Google Cloud Project

- Click "Select a project" (top left) and choose an existing project or click "New project" (top right) to create a new one (e.g., "denario").
- Once created, select the project.

#### Enable Vertex AI API

- With the project selected, its name will appear next to the Google Cloud logo.
- Open the navigation menu (three horizontal lines), find "Vertex AI", hover, and select "Dashboard".
- Click "Enable all recommended APIs".

#### Create a Service Account Key

- In the navigation menu, go to "IAM & Admin" > "Service Accounts".
- Click "Create Service Account".
- Name the account (e.g., "denario"). The description is optional.
- Click "Create and Continue".
- In "Select a Role", enter "Vertex AI User" and select it. Click "Continue".
- Skip "Principals with access". Click "Done".
- In the list view, find your account (e.g., `denario@denario-1234.iam.gserviceaccount.com`).
- Click the three dots under "Actions" and select "Manage Keys".
- Click "Add key" > "Create new key" > select "JSON".
- Download the JSON file and rename it to `gemini.json`.

#### Enable Billing

- In the navigation menu, select "Billing".
- Click "Link a billing account" and follow the prompts to create a billing account.
- Choose your country, enter contact information, and add a payment method.

---

## FutureHouse

Denario uses [FutureHouse](https://www.futurehouse.org/)'s Owl agent for precedent search (i.e., checking if an idea has been previously explored). To obtain an API key, visit [this page](https://platform.futurehouse.org/) and follow the instructions.

---

## Where to Store API Keys

API keys can be set in one of the following ways:

1. **Add to `~/.bashrc` or `~/.bash_profile`**  
   Insert the following lines, replacing with your actual API keys. If you do not have an optional API key (e.g., Anthropic), leave the value blank.

```bash
export GOOGLE_API_KEY=your_gemini_api_key
export GOOGLE_APPLICATION_CREDENTIALS=path/to/gemini.json
export OPENAI_API_KEY=your_openai_api_key
export PERPLEXITY_API_KEY=your_perplexity_api_key
export ANTHROPIC_API_KEY=your_anthropic_api_key
export FUTURE_HOUSE_API_KEY=your_fh_key
```

2. **Set in the Terminal**  
   Copy and paste the above lines directly into your terminal session.

3. **Create a `.env` File**  
   In the directory where Denario will be run, create a `.env` file containing:

```bash
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/gemini.json
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
FUTURE_HOUSE_API_KEY=your_fh_key
```

---

**Note:**  
Never share your API keys. Always monitor your usage and costs on each provider's platform.