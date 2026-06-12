import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/blogger']
CLIENT_SECRETS_FILE = os.path.join('auth', 'client_secrets.json')
TOKEN_FILE = os.path.join('auth', 'blogger_token.json')

def get_token():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"ERROR: File not found at {CLIENT_SECRETS_FILE}")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    
    # Run the local server, which will print the URL to stdout
    print("Starting server... check the link below:")
    creds = flow.run_local_server(port=8080, open_browser=False)

    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("SUCCESS")

if __name__ == '__main__':
    get_token()
