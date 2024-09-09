from app import app, db, User, EthicalDecision, Interaction, Feedback, Log

# Create the application context
with app.app_context():
    # Create a new user
    new_user = User(username='testuser', email='testuser@example.com')

    # Add user to the database
    db.session.add(new_user)
    db.session.commit()

    print(f"User: {new_user.username}, Email: {new_user.email}")

    # Create a new ethical decision for the user
    ethical_decision = EthicalDecision(
        decision_type='Sample Decision Type',
        decision_detail='Sample Decision Detail',
        user_id=new_user.user_id
    )

    # Add ethical decision to the database
    db.session.add(ethical_decision)
    db.session.commit()

    # Create a new interaction
    interaction = Interaction(
        user_input='Sample User Input',
        bot_response='Sample Bot Response',
        decision_id=ethical_decision.decision_id,
        user_id=new_user.user_id
    )

    # Add interaction to the database
    db.session.add(interaction)
    db.session.commit()

    # Create feedback for the ethical decision
    feedback = Feedback(
        feedback_text='Sample Feedback Text',
        rating=5,
        user_id=new_user.user_id
    )

    # Add feedback to the database
    db.session.add(feedback)
    db.session.commit()

    # Create a log entry
    log = Log(
        log_message='Sample Log Message',
        user_id=new_user.user_id
    )

    # Add log entry to the database
    db.session.add(log)
    db.session.commit()

    print("Test data inserted successfully.")
