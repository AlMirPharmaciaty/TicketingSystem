import os
from dotenv import load_dotenv
from fastapi import FastAPI
from src.utils.database import init_db
from src.api import auth, user, ticket, ticket_notes


def my_app():
    """
    Loading environment variables
    and initializing the app
    """

    load_dotenv()
    init_db()

    app = FastAPI(title=os.getenv("TITLE"))
    app.include_router(auth.auth)
    app.include_router(user.users)
    app.include_router(ticket.tickets)
    app.include_router(ticket_notes.ticket_notes)

    return app
