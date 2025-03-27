from app import db, AnalyticsLog, app

# Add logs inside the app context
def add_dummy_logs():
    with app.app_context():  # Ensure proper application context
        # Create dummy logs
        log1 = AnalyticsLog(action="add_policy", details="Added policy: Whistleblowing process")
        log2 = AnalyticsLog(action="user_query", details="User asked: What is whistleblowing?")
        log3 = AnalyticsLog(action="delete_policy", details="Deleted policy ID 1")
        
        db.session.add_all([log1, log2, log3])
        db.session.commit()
        print("Dummy data added to AnalyticsLog table.")

if __name__ == "__main__":
    add_dummy_logs()
