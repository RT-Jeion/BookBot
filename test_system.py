# test_system.py
import os
print("Project structure check:")
files = ['bot.py', 'books.py', 'orders.py', 'courier.py', 'dashboard.py', 'utils.py', 'requirements.txt']
for f in files:
    print(f"  {f}: {'OK' if os.path.exists(f) else 'MISSING'}")

# Confirm no .env
print(f"  .env: {'MISSING (good)' if not os.path.exists('.env') else 'EXISTS (remove it)'}")

# Test imports
try:
    import telegram, requests, streamlit
    from bs4 import BeautifulSoup
    print("All packages imported: OK")
except Exception as e:
    print(f"Import failed: {e}")