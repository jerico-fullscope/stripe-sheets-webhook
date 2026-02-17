"""
Helper script to run the Flask app locally with better error handling
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    print("\n" + "="*60)
    print("Checking Environment Configuration")
    print("="*60)

    required_vars = {
        'STRIPE_API_KEY': 'Get from Stripe Dashboard > Developers > API Keys',
        'STRIPE_WEBHOOK_SECRET': 'Get after creating webhook endpoint in Stripe',
        'TARGET_SHEET_NAME': 'Name of your Google Sheet',
        'GOOGLE_SHEET_ID': 'ID from Google Sheet URL'
    }

    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"❌ {var} not set")
            print(f"   → {description}")
            missing.append(var)
        else:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")

    if missing:
        print(f"\n⚠️  Please set the following variables in .env file:")
        for var in missing:
            print(f"   - {var}")
        print("\nRefer to .env.example for the template")
        return False

    return True


def check_credentials():
    """Check if credentials.json exists"""
    print("\n" + "="*60)
    print("Checking Google Service Account Credentials")
    print("="*60)

    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("   → Place your Google service account credentials file here")
        return False


def run_app():
    """Run the Flask application"""
    print("\n" + "="*60)
    print("Starting Flask Application")
    print("="*60)

    try:
        # Import app after environment is set
        from app import app

        print("\n✅ Flask app loaded successfully!")
        print("\nEndpoints available:")
        print("  - http://localhost:5000/health")
        print("  - http://localhost:5000/webhook (POST)")
        print("\nPress Ctrl+C to stop the server")
        print("="*60 + "\n")

        # Run the app
        app.run(debug=True, port=5000, host='0.0.0.0')

    except ImportError as e:
        print(f"\n❌ Failed to import app: {e}")
        print("\nPossible issues:")
        print("  - Missing dependencies (run: pip install -r requirements.txt)")
        print("  - Syntax error in app.py or sheets_service.py")
        return False
    except Exception as e:
        print(f"\n❌ Failed to start app: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Stripe → Google Sheets Webhook Server")
    print("="*60)

    # Run checks
    env_ok = check_environment()
    creds_ok = check_credentials()

    if not env_ok or not creds_ok:
        print("\n" + "="*60)
        print("⚠️  Setup incomplete - please fix the issues above")
        print("="*60)
        sys.exit(1)

    print("\n✅ All checks passed! Starting server...")

    # Run the app
    run_app()
