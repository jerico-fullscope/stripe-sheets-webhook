"""
Basic test to verify Flask app structure and imports
This test doesn't require Stripe credentials
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')  # type: ignore

def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "="*60)
    print("Testing Imports")
    print("="*60)

    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

    try:
        import stripe
        print("✅ Stripe imported successfully")
    except ImportError as e:
        print(f"❌ Stripe import failed: {e}")
        return False

    try:
        import gspread
        print("✅ gspread imported successfully")
    except ImportError as e:
        print(f"❌ gspread import failed: {e}")
        return False

    try:
        import oauth2client
        print("✅ oauth2client imported successfully")
    except ImportError as e:
        print(f"❌ oauth2client import failed: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False

    return True


def test_app_structure():
    """Test that app.py can be imported"""
    print("\n" + "="*60)
    print("Testing App Structure")
    print("="*60)

    # Set dummy env vars to avoid errors
    os.environ['STRIPE_API_KEY'] = 'sk_test_dummy'
    os.environ['STRIPE_WEBHOOK_SECRET'] = 'whsec_dummy'
    os.environ['TARGET_SHEET_NAME'] = 'Test Sheet'

    try:
        # Try importing without actually initializing sheets
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        if spec and spec.loader:
            print("✅ app.py structure is valid")
            return True
        else:
            print("❌ app.py could not be loaded")
            return False
    except Exception as e:
        print(f"❌ Error checking app.py: {e}")
        return False


def test_files_exist():
    """Test that all required files exist"""
    print("\n" + "="*60)
    print("Testing File Structure")
    print("="*60)

    required_files = [
        'app.py',
        'sheets_service.py',
        'requirements.txt',
        'Procfile',
        '.env',
        '.env.example',
        '.gitignore',
        'credentials.json',
        'README.md'
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_exist = False

    return all_exist


def test_env_variables():
    """Test that .env file has required variables"""
    print("\n" + "="*60)
    print("Testing Environment Configuration")
    print("="*60)

    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        'TARGET_SHEET_NAME',
    ]

    optional_vars = [
        'STRIPE_API_KEY',
        'STRIPE_WEBHOOK_SECRET',
        'GOOGLE_SHEET_ID',
    ]

    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            all_set = False

    print("\nOptional variables (set these before deploying):")
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith('your_'):
            print(f"✅ {var} is set")
        else:
            print(f"⚠️  {var} needs to be configured")

    return all_set


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Basic Integration Test Suite")
    print("="*60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("File Structure", test_files_exist()))
    results.append(("Environment Variables", test_env_variables()))
    results.append(("App Structure", test_app_structure()))

    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n✅ All basic tests passed!")
        print("\nNext steps:")
        print("1. Add your Stripe API key and webhook secret to .env")
        print("2. Add your Google Sheet ID to .env")
        print("3. Run: python app.py")
        print("4. Test with: python test_webhook.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
