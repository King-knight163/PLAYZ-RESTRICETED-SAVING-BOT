import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8142366006:AAE6f36M24cGmjTELOYHXg2ui-J1GacKR5I")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "22161204"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "fdffc74281153b3338e4474f5640095e")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "7107162691"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://panigrahij844:9huIJ6yBXCjAxeBT@cluster0.huwvh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
