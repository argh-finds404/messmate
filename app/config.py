class Config:
    DATABASE = "messmate.db"
    TESTING = False
    PAYMENT_MODE = "sandbox"
    NOTIFY_CHANNEL = "console"
    # Development key only; must be replaced with a secret value in production.
    SECRET_KEY = "dev-secret-change-me"
