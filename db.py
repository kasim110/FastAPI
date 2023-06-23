import urllib.parse

def db():
    # Replace the values below with your actual MySQL connection details
    username = "kasim"
    password = "kasim@123"
    hostname = "localhost"
    port = 3306
    database_name = "fastapi"

    # Encode the password
    encoded_password = urllib.parse.quote_plus(password)

    # Construct the connection string
    db_connection_string = f"mysql+mysqlconnector://{username}:{encoded_password}@{hostname}:{port}/{database_name}"
    return db_connection_string