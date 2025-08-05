

import webbrowser
from stravalib.client import Client
from config.config import settings

def main():
    """
    This script guides you through the Strava OAuth process to generate a new
    access token with the required permissions (scopes).

    Instructions:
    1. Run this script from your terminal: python generate_strava_token.py
    2. The script will print a Strava authorization URL. Copy and paste this
       URL into your web browser.
    3. Authorize the application on the Strava page.
    4. You will be redirected to a non-working URL (e.g., http://localhost/exchange_token?state=&code=...&scope=...).
    5. Copy the entire redirected URL from your browser's address bar.
    6. Paste the URL back into the terminal when prompted.
    7. The script will extract the authorization code, exchange it for a new
       set of tokens, and print them.
    8. Update your .env file with the new STRAVA_ACCESS_TOKEN and
       STRAVA_REFRESH_TOKEN values.
    """
    client = Client()
    client_id = settings.STRAVA_CLIENT_ID
    client_secret = settings.STRAVA_CLIENT_SECRET
    redirect_uri = "http://localhost/exchange_token"

    if not client_id or not client_secret:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in your .env file.")
        return

    # Step 1: Generate and display the authorization URL
    authorize_url = client.authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=["read", "activity:read_all", "profile:read_all"],
        state="strava-auth"
    )

    print("\n--- Strava Token Generation ---\n")
    print("1. Please open the following URL in your browser to authorize the application:")
    print(f"\n{authorize_url}\n")
    
    webbrowser.open(authorize_url)

    # Step 2: Get the authorization code from the user
    redirected_url = input("2. After authorizing, you were redirected. Please paste the full redirected URL here and press Enter:\n")

    # Step 3: Exchange the code for a token
    try:
        code = redirected_url.split("code=")[1].split("&")[0]
        print("\nProcessing...\n")
        
        token_response = client.exchange_code_for_token(
            client_id=client_id,
            client_secret=client_secret,
            code=code
        )

        # Step 4: Print the new token information
        print("✅ Success! Your new tokens are ready.\n")
        print("Please update your .env file with these new values:\n")
        print(f"STRAVA_ACCESS_TOKEN={token_response['access_token']}")
        print(f"STRAVA_REFRESH_TOKEN={token_response['refresh_token']}\n")
        print("(You can now stop this script and run the main application.)")

    except IndexError:
        print("\nError: Could not find 'code=' parameter in the URL you provided.")
        print("Please make sure you copied the full redirected URL.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()

