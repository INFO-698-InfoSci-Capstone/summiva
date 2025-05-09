"""
Summiva - NLP Summarization System
Main application entry point
"""
from nicegui import ui, app

from config.settings import (
    APP_TITLE, APP_PORT, APP_DARK_MODE, 
    logger
)
from services.summary_service import load_summaries
from components.header import create_header
from pages.home_page import home_page
from pages.login_page import login_page
from pages.advanced_search_page import advanced_search_page
from pages.profile_page import user_profile_page

# --- Routing ---
@ui.page("/")
def route_home():
    create_header()
    with ui.column().classes("p-4 max-w-6xl mx-auto"):
        home_page()

@ui.page("/advanced")
def route_advanced():
    create_header()
    with ui.column().classes("p-4 max-w-6xl mx-auto"):
        advanced_search_page()

@ui.page("/login")
def route_login():
    create_header()
    with ui.column().classes("p-4 max-w-md mx-auto"):
        login_page()

@ui.page("/profile")
def route_profile():
    create_header()
    with ui.column().classes("p-4 max-w-md mx-auto"):
        user_profile_page()

# --- Application Initialization ---
@app.on_startup
def startup():
    load_summaries()
    logger.info("Summiva frontend application started")

# --- Run Application ---
if __name__ == "__main__":
    ui.run(
        title=APP_TITLE,
        favicon="🔍",
        dark=APP_DARK_MODE,
        reload=False,
        port=APP_PORT,
        show=False
    )