from app import app, db, User, EthicalDecision

# Create the application context
with app.app_context():
    # Define the username of the user to delete
    username_to_delete = 'testuser'
    
    # Find the user by username
    user = User.query.filter_by(username=username_to_delete).first()
    
    if user:
        # Print the IDs to be deleted (for confirmation)
        print(f"User ID to be deleted: {user.user_id}")

        # Delete the user (this will also delete related ethical decisions due to ON DELETE CASCADE)
        db.session.delete(user)
        db.session.commit()
        
        # Verify deletion
        user_after_delete = User.query.filter_by(username=username_to_delete).first()
        if user_after_delete is None:
            print("User and related ethical decisions successfully deleted.")
        else:
            print(f"User still exists: {user_after_delete.username}")

    else:
        print("User not found.")
