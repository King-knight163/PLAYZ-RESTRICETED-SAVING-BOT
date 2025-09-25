import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8142366006:AAGMRm166OnRDQBY-VBhyhyg1fyzPnrrWcY")

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

# PREMIUM/FREEMIUM SYSTEM CONFIGURATION
# ShrinkMe API Configuration
SHRINKME_API_KEY = os.environ.get("SHRINKME_API_KEY", "6a5a6ce8d33950c63502d761ae11bf36632f08ca")
SHRINKME_BASE_URL = os.environ.get("SHRINKME_BASE_URL", "https://shrinkme.io/api")

# Freemium Duration (24 hours in seconds)
FREEMIUM_DURATION = int(os.environ.get("FREEMIUM_DURATION", "86400"))

# File Size Limits (in GB)
FILE_LIMITS = {
    "freemium": {"max_size": 2, "files_per_batch": 3, "daily_batches": 4},
    "standard": {"max_size": 4, "files_per_batch": 20, "daily_batches": 10},
    "pro": {"max_size": 4, "files_per_batch": 50, "daily_batches": 15},
    "elite": {"max_size": 4, "files_per_batch": 100, "daily_batches": 15},
    "premium": {"max_size": 100, "files_per_batch": 1000, "daily_batches": 1000},
    "free": {"max_size": 0, "files_per_batch": 0, "daily_batches": 0}
}

# Plan Pricing (in USD)
PLAN_PRICES = {
    "standard": 8,
    "pro": 20,
    "elite": 45,
    "premium": 99
}

# Bot Features Toggle
ENABLE_VERIFICATION = bool(os.environ.get("ENABLE_VERIFICATION", True))
ENABLE_PREMIUM_SYSTEM = bool(os.environ.get("ENABLE_PREMIUM_SYSTEM", True))
ENABLE_USAGE_LIMITS = bool(os.environ.get("ENABLE_USAGE_LIMITS", True))
ENABLE_ANALYTICS = bool(os.environ.get("ENABLE_ANALYTICS", True))

# Rate Limiting Configuration
RATE_LIMIT_MESSAGES = int(os.environ.get("RATE_LIMIT_MESSAGES", "5"))  # messages per minute
RATE_LIMIT_DOWNLOADS = int(os.environ.get("RATE_LIMIT_DOWNLOADS", "10"))  # downloads per hour for free users

# Session Configuration
SESSION_STRING_SIZE = int(os.environ.get("SESSION_STRING_SIZE", "351"))
SESSION_TIMEOUT = int(os.environ.get("SESSION_TIMEOUT", "1800"))  # 30 minutes

# Bot Information
BOT_USERNAME = os.environ.get("BOT_USERNAME", "your_bot_username")  # Your bot username without @
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/PLAY_Z_HACKING_DISCUSSION")
UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "https://t.me/+ahE-9i84aFxkOWNl")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "PLAYZ_90")

# Payment Configuration (Optional)
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

# Broadcast Configuration
BROADCAST_AS_COPY = bool(os.environ.get("BROADCAST_AS_COPY", True))
DELETE_BROADCAST_AFTER = int(os.environ.get("DELETE_BROADCAST_AFTER", "0"))  # 0 means don't delete

# Security Configuration
MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "3"))
LOGIN_ATTEMPT_TIMEOUT = int(os.environ.get("LOGIN_ATTEMPT_TIMEOUT", "300"))  # 5 minutes

# Performance Configuration
MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", "3"))
DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", "300"))  # 5 minutes
UPLOAD_TIMEOUT = int(os.environ.get("UPLOAD_TIMEOUT", "600"))  # 10 minutes

# Logging Configuration
LOG_CHANNEL = os.environ.get("LOG_CHANNEL", "")  # Channel ID for logging (optional)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Webhook Configuration (for deployment)
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", "")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "8080"))
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", f"/{BOT_TOKEN}")

# Advanced Features
ENABLE_REFERRAL_SYSTEM = bool(os.environ.get("ENABLE_REFERRAL_SYSTEM", False))
REFERRAL_BONUS_HOURS = int(os.environ.get("REFERRAL_BONUS_HOURS", "24"))  # Bonus hours for referrals

# Content Filtering
BLOCKED_KEYWORDS = os.environ.get("BLOCKED_KEYWORDS", "").split(",") if os.environ.get("BLOCKED_KEYWORDS") else []
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "2000"))  # 2GB default

# Multi-language Support
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "en")
SUPPORTED_LANGUAGES = os.environ.get("SUPPORTED_LANGUAGES", "en,hi").split(",")

# Database Backup Configuration
AUTO_BACKUP = bool(os.environ.get("AUTO_BACKUP", False))
BACKUP_INTERVAL_HOURS = int(os.environ.get("BACKUP_INTERVAL_HOURS", "24"))

# Notification Settings
NOTIFY_ON_NEW_USER = bool(os.environ.get("NOTIFY_ON_NEW_USER", True))
NOTIFY_ON_PREMIUM_PURCHASE = bool(os.environ.get("NOTIFY_ON_PREMIUM_PURCHASE", True))
NOTIFY_ON_ERROR = bool(os.environ.get("NOTIFY_ON_ERROR", True))
