

import sys
from stravalib.client import Client
from config.config import settings

def main():
    """
    This script exchanges the authorization code from Strava for a new access
    and refresh token.

    Instructions:
    1.  After authorizing the application in your browser, you were redirected
        to a URL containing a 'code' parameter.
    2.  Run this script from your terminal, passing the full redirected URL
        as an argument, enclosed in quotes.
        e.g., python exchange_token.py "http://localhost/exchange_token?state=...&code=...&scope=..."
    3.  The script will print your new tokens.
    4.  Update your .env file with the new STRAVA_ACCESS_TOKEN and
        STRAVA_REFRESH_TOKEN values.
    """
    if len(sys.argv) < 2:
        print("Error: Please provide the full redirected URL as a command-line argument.")
        print('Example: python exchange_token.py "<your_redirected_url>"')
        sys.exit(1)

    redirected_url = sys.argv[1]

    client = Client()
    client_id = settings.STRAVA_CLIENT_ID
    client_secret = settings.STRAVA_CLIENT_SECRET

    if not client_id or not client_secret:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in your .env file.")
        return

    try:
        # Extract the code from the URL
        code = redirected_url.split("code=")[1].split("&")[0]
        print("\nExchanging code for token...")

        token_response = client.exchange_code_for_token(
            client_id=client_id,
            client_secret=client_secret,
            code=code
        )

        print("\n✅ Success! Your new tokens are ready.\n")
        print("Please update your .env file with these new values:\n")
        print(f"STRAVA_ACCESS_TOKEN={token_response['access_token']}")
        print(f"STRAVA_REFRESH_TOKEN={token_response['refresh_token']}\n")
        print("You can now run the main application.")

    except IndexError:
        print("\nError: Could not find 'code=' parameter in the URL.")
        print("Please make sure you pasted the full redirected URL.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

