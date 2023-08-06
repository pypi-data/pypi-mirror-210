from keyauth import KeyAuth 

authenticator = KeyAuth(app_id="cfc0a6cbf910c73b")  # Replace with your actual app_id

if authenticator.authenticate():
    print("Authentication successful!")
else:
    print("Authentication failed.")
