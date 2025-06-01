from app import app, db, GoLink, User

# Change this to the user ID you want to assign the links to
USER_ID = 1

sample_links = [
    ("google", "https://www.google.com"),
    ("github", "https://github.com"),
    ("stackoverflow", "https://stackoverflow.com"),
    ("python", "https://www.python.org"),
    ("flask", "https://flask.palletsprojects.com"),
    ("sqlite", "https://www.sqlite.org"),
    ("wikipedia", "https://en.wikipedia.org"),
    ("youtube", "https://www.youtube.com"),
    ("reddit", "https://www.reddit.com"),
    ("twitter", "https://twitter.com"),
    ("apple", "https://www.apple.com"),
    ("microsoft", "https://www.microsoft.com"),
    ("amazon", "https://www.amazon.com"),
    ("facebook", "https://www.facebook.com"),
    ("netflix", "https://www.netflix.com"),
    ("openai", "https://www.openai.com"),
    ("cursor", "https://www.cursor.so"),
    ("news", "https://news.ycombinator.com"),
    ("medium", "https://medium.com"),
    ("devto", "https://dev.to"),
]

with app.app_context():
    for short_path, target_url in sample_links:
        if not GoLink.query.filter_by(short_path=short_path).first():
            link = GoLink(short_path=short_path, target_url=target_url, user_id=USER_ID)
            db.session.add(link)
    db.session.commit()
    print("Added 20 sample links.")
