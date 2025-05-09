from nicegui import ui

from services.auth_service import get_current_user, logout
from services.summary_service import summary_list

def user_profile_page():
    """User profile page UI"""
    ui.label("👤 Summiva - User Profile").classes("text-2xl font-bold")
    
    current_user = get_current_user()
    if current_user:
        ui.label(f"Username: {current_user['username']}").classes("text-lg")
        ui.label(f"Summaries: {len(summary_list)}").classes("text-lg")
        ui.button("Logout", on_click=lambda: handle_logout()).classes("bg-red-500 text-white mt-4")
    else:
        ui.label("You are not logged in").classes("text-lg")
        ui.button("Login", on_click=lambda: ui.navigate.to("/login")).classes("bg-blue-500 text-white mt-4")
    
    def handle_logout():
        logout()
        ui.navigate.to("/login")
        ui.notify("Logged out successfully", type="positive")