import os
from dotenv import load_dotenv
import requests
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

load_dotenv()

TMDB_BASE_URL =  "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_top_movies(n: int =10) -> list[dict]:
    """
    Fetches the top N popular Swedish movies from TMDB API.
    :param n: Number of top movies to fetch (default: 10)
    :return:  List of movie dicts with details like title, release date, popularity, etc.
    """
    url = f"{TMDB_BASE_URL}/discover/movie"  # /discover is de accurate endpoint to fetch the movies

    params = {
        "with_origin_country": "SE", # Swedish movies
        "sort_by": "popularity.desc" # Top popular movies
    }

    headers = {
        "Authorization": f"Bearer {TMDB_API_KEY}",
        "accept": "application/json"
    }
    response = requests.get(url,headers=headers, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])
    return results[:n]

def movies_to_dataframe(movies: list[dict]) -> pd.DataFrame:
    """
    Transforms a list of TMDB movie dicts into a clean DataFrame.
    """
    rows = []
    for i, movie in enumerate(movies, start=1):
        rows.append({
            "Rank":          i,
            "Title":         movie.get("title", "N/A"),
            "Original Title": movie.get("original_title", "N/A"),
            "Original Language": movie.get("original_language", "N/A"),
            "Popularity":    movie.get("popularity", 0),
            "Release Date":  movie.get("release_date", "N/A"),
            "Vote Average":  movie.get("vote_average", 0),
            "Vote Count":    movie.get("vote_count", 0),
            "Overview":      movie.get("overview", "N/A"),
        })
    df = pd.DataFrame(rows)
    return df


def get_google_credentials() -> Credentials:
    """
    Handles OAuth2 flow. Opens browser on first run, uses cached token afterwards.
    Requires credentials.json in the project root (see README).
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def create_spreadsheet(service, title: str) -> str:
    """
    Creates a new Google Spreadsheet and returns its ID.
    """
    spreadsheet = service.spreadsheets().create(
        body={"properties": {"title": title}}
    ).execute()
    return spreadsheet["spreadsheetId"]


def write_dataframe_to_sheet(service, spreadsheet_id: str, df: pd.DataFrame) -> None:
    """
    Writes a DataFrame (headers + rows) into the first sheet starting at A1.
    """
    values = [df.columns.tolist()] + df.values.tolist()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="A1",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()


def main():
    res = get_top_movies()
    df = movies_to_dataframe(res)

    # Google Authentication
    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)

    print(" ################### Authenticated ###################\n")

    # Google Spreadsheet creation
    print(" ################### Creating Google Spreadsheet ###################")

    spreadsheet_id = create_spreadsheet(service, title="Top 10 Swedish Movies (TMDB)")
    write_dataframe_to_sheet(service, spreadsheet_id, df)

    print(f" ################### Spreadsheet created: https://docs.google.com/spreadsheets/d/{spreadsheet_id} ###################\n")


if __name__ == "__main__":
    main()

