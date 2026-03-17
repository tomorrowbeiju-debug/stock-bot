try:
    from app import app
    print("OK - App loaded successfully")
    print("Routes:", [str(rule) for rule in app.url_map.iter_rules()])
except Exception as e:
    print(f"Error: {e}")
