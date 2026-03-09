import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import webbrowser

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def main():
    print("Gmail Token Generator")
    print("====================")

    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        print("Loading existing credentials from token.json...")
        with open('token.json', 'r') as token_file:
            token_data = json.load(token_file)

        # Create credentials from the token data
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )

        # Refresh the access token if needed
        if creds.expired and creds.refresh_token:
            try:
                print("Refreshing access token...")
                creds.refresh(Request())
                print("Access token refreshed successfully.")
            except RefreshError as e:
                print(f"Error refreshing token: {e}")
                print("Will need to re-authenticate...")
                creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if os.path.exists('credentials.json'):
            print("Starting OAuth flow...")
            print("Browser should open automatically - complete login there.")

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8080/'
            creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())

            print("Credentials saved to token.json")
        else:
            print("Error: credentials.json not found!")
            print("Please download your OAuth 2.0 credentials from Google Cloud Console")
            print("and save as 'credentials.json' in this directory.")
            return

    # Build the Gmail service
    try:
        print("Building Gmail service...")
        service = build('gmail', 'v1', credentials=creds)

        # Test: List labels to confirm access works
        print("Testing access - fetching labels...")
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if labels:
            print(f"Successfully connected to Gmail API. Found {len(labels)} labels.")
        else:
            print("No labels found, but connection to Gmail API successful.")

        # Prepare the output for .env
        print("\n=== Gmail Tokens for .env ===\n")
        print(f"GMAIL_CLIENT_ID={creds.client_id}")
        print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
        print(f"GMAIL_ACCESS_TOKEN={creds.token}")
        print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")
        print(f"GMAIL_USER_EMAIL=me")  # Use 'me' as the user ID for the authenticated user

        print("\n=== Important Notes ===")
        print("1. Copy the above values to your .env file")
        print("2. The refresh token only appears once during first authorization - keep token.json safe!")
        print("3. Never commit token.json or credentials.json to version control")
        print("4. In your gmail_watcher_impl.py, use google.oauth2.credentials with refresh logic")

    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return

if __name__ == "__main__":
    main()