import os
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load .env from the root directory
load_dotenv(os.path.join(BASE_DIR, "../.env"))

# Now you can use these directly
MONGO = {"MONGO_URL": os.getenv("MONGO_URL"), "MONGO_DB": os.getenv("MONGO_DB")}

SUPABASE = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_API_KEY": os.getenv("SUPABASE_API_KEY"),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    "SUPABASE_BEARER_TOKEN": os.getenv("SUPABASE_BEARER_TOKEN"),
}


DB_CONNECTION = os.getenv("DB_CONNECTION")
APPNAME = os.getenv("APPNAME")

QBTBASEURL = os.getenv("QBTBASEURL")
QBTCLINETID = os.getenv("QBTCLINETID")
QBTCLINETSECRET = os.getenv("QBTCLINETSECRET")

APIKEY = os.getenv("X-API-KEY")

# Authentication settings
AUTH = {
    "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
    "ADMIN_PASSWORD": os.getenv("ADMIN_PASSWORD", "admin123"),
    "SESSION_SECRET_KEY": os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-this-in-production"),
    "SESSION_EXPIRE_HOURS": int(os.getenv("SESSION_EXPIRE_HOURS", "24"))
}

# Email settings
EMAIL = {
    "IMAP_SERVER": os.getenv("IMAP_SERVER", "imap.gmail.com"),
    "IMAP_PORT": int(os.getenv("IMAP_PORT", "993")),
    "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS"),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
    "USE_SSL": os.getenv("USE_SSL", "True").lower() == "true"
}

# WhatsApp settings
WHATSAPP = {
    "ACCESS_TOKEN": os.getenv("WHATSAPP_ACCESS_TOKEN"),
    "PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
    "WEBHOOK_VERIFY_TOKEN": os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "test123"),
    "API_VERSION": os.getenv("WHATSAPP_API_VERSION", "v22.0")
}