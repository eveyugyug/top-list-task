# Top 10 Swedish Movies → Google Sheets

Fetches the top 10 movies originating from Sweden via the TMDB API and pushes the list to a new Google Sheets spreadsheet.

---

## Requirements

- Python 3.11+
- A [TMDB account](https://www.themoviedb.org/) (free)
- A Google account

---

## Setup

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd <repo-folder>
pip install -r requirements.txt
```

### 2. Get your TMDB API key

1. Create a free account at [themoviedb.org](https://www.themoviedb.org/)
2. Go to **Settings → API** and request an API key (free, instant)
3. Copy the **API Read Access Token**

Create a `.env` file in the project root:

Edit `.env` and paste your key:

```
TMDB_API_KEY=your_actual_API_read_access_token_here
```

### 3. Get your Google OAuth credentials

You have two options:

**Option A — Use the project's existing credentials (easier)**

Contact the repo owner to:
- Be added as a **test user** in the Google Cloud project
- Receive the `credentials.json` file via email or private channel

**Option B — Create your own Google Cloud project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **Google Sheets API**
4. Go to **APIs & Services → OAuth consent screen**
   - Set user type to **External**
   - Fill in the required fields
   - Add your own Google account as a **test user**
5. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
6. Choose **Desktop app** as the application type
7. Download the JSON file and rename it to `credentials.json`

In both cases, place `credentials.json` in the project root.

> ⚠️ `credentials.json` and `token.json` are in `.gitignore` — never commit them.

---

## Run

```bash
python main.py
```

On the **first run**, a browser window will open asking you to authorize access to your Google account. After that, a `token.json` is saved locally and future runs won't require browser interaction.

The script will print the spreadsheet URL when done. ✅

---

## Project Structure

```
├── main.py              # All logic, split into focused functions
├── requirements.txt
├── .env.example         # Template for environment variables
├── .env                 # Your actual keys (gitignored)
├── credentials.json     # Your Google OAuth credentials (gitignored)
├── token.json           # Auto-generated after first auth (gitignored)
└── .gitignore
```

## How it works

| Function | Responsibility |
|---|---|
| `get_top_movies()` | Calls TMDB `/discover/movie` filtered by `with_origin_country=SE` |
| `movies_to_dataframe()` | Transforms raw API response into a clean pandas DataFrame |
| `get_google_credentials()` | Handles OAuth2 flow, caches token locally |
| `create_spreadsheet()` | Creates a new Google Sheet, returns its ID |
| `write_dataframe_to_sheet()` | Writes headers + rows to the sheet |
| `main()` | Orchestrates all of the above |
