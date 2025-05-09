from nicegui import ui
from services.auth_service import login
from services.summary_service import load_summaries

def login_page():
    """Login page UI with enhanced form validation and styling"""
    ui.label("🔐 Summiva - Login").classes("text-3xl font-bold text-center mb-8")
    
    with ui.card().classes("w-full p-6 shadow-lg bg-white dark:bg-gray-800"):
        # Form layout
        with ui.tabs().classes("w-full mb-6") as tabs:
            login_tab = ui.tab("Login")
            register_tab = ui.tab("Register")
            
        with ui.tab_panels(tabs, value=login_tab).classes("w-full"):
            # Login Panel
            with ui.tab_panel(login_tab):
                with ui.column().classes("gap-4 w-full"):
                    # Username field with validation
                    username = ui.input("Username", validation={"Required": lambda val: val != ""})
                    username.classes("w-full").props('outlined')
                    
                    # Password field with validation
                    password = ui.input("Password", password=True, 
                                      validation={"Required": lambda val: val != ""})
                    password.classes("w-full").props('outlined')
                    
                    # Remember me checkbox
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.checkbox("Remember me").classes("text-sm")
                        ui.link("Forgot password?", "#").classes("text-sm text-blue-600 hover:text-blue-800")
                    
                    # Error message container
                    error_container = ui.element('div').classes("mt-2")
                    error_label = ui.label("").classes("text-red-500 text-sm")
                    error_label.set_visibility(False)
                    
                    # Login button
                    login_button = ui.button("Sign In", on_click=lambda: on_login())
                    login_button.classes("w-full bg-blue-600 hover:bg-blue-700 text-white py-2 mt-2")
                    
                    def on_login():
                        # Validate form
                        if not username.value or not password.value:
                            error_label.set_text("Please fill in all required fields")
                            error_label.set_visibility(True)
                            return
                            
                        # Attempt login
                        with ui.spinner("dots").classes("text-blue-500"):
                            if login(username.value, password.value):
                                load_summaries()  # Load user's summaries after login
                                ui.notify("Successfully logged in!", type="positive")
                                ui.navigate.to("/")
                            else:
                                error_label.set_text("Login failed. Please check your credentials.")
                                error_label.set_visibility(True)
                    
                    # Guest login option            
                    ui.separator().classes("my-4")
                    
                    ui.button("Continue as Guest", on_click=lambda: ui.navigate.to("/")) \
                        .classes("w-full border border-gray-300 hover:bg-gray-100 py-2 mt-2")
            
            # Register Panel (placeholder for future implementation)
            with ui.tab_panel(register_tab):
                with ui.column().classes("gap-4 w-full"):
                    ui.input("Username").props('outlined').classes("w-full")
                    ui.input("Email").props('outlined').classes("w-full")
                    ui.input("Password", password=True).props('outlined').classes("w-full")
                    ui.input("Confirm Password", password=True).props('outlined').classes("w-full")
                    
                    ui.button("Create Account", on_click=lambda: ui.notify("Registration will be implemented soon!", type="info")) \
                        .classes("w-full bg-green-600 hover:bg-green-700 text-white py-2 mt-2")
        
        # Social login options
        ui.separator().classes("my-6")
        
        ui.label("Or sign in with").classes("text-center text-gray-500 my-2")
        
        with ui.row().classes("gap-2 justify-center"):
            ui.button(icon="mail", on_click=lambda: ui.notify("Google login coming soon!", type="info")) \
                .props("round flat").classes("text-red-600")
            ui.button(icon="fingerprint", on_click=lambda: ui.notify("GitHub login coming soon!", type="info")) \
                .props("round flat").classes("text-gray-800")
            ui.button(icon="work", on_click=lambda: ui.notify("LinkedIn login coming soon!", type="info")) \
                .props("round flat").classes("text-blue-700")
    
    # Footer
    with ui.element('footer').classes("mt-8 text-center text-sm text-gray-500"):
        ui.label("© 2025 Summiva. All rights reserved.")