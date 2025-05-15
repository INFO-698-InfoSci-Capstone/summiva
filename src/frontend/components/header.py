from nicegui import ui, app
from services.auth_service import get_current_user

def create_header():
    """Create an enhanced header navigation component"""
    
    # Initialize dark mode based on config or localStorage
    dark_mode = ui.dark_mode()
    
    # Create a modern header with responsive design
    with ui.header().classes("bg-gradient-to-r from-blue-800 to-blue-600 text-white shadow-md"):
        with ui.row().classes("w-full items-center justify-between p-2 container mx-auto"):
            # Left section - Logo and maidon navigation
            with ui.row().classes("items-center gap-2"):
                ui.label("📄").classes("text-2xl")  # Logo emoji
                ui.label("Summiva").classes("text-2xl font-bold tracking-tight")
                
                # Responsive navigation
                with ui.element("div").classes("hidden md:flex ml-6"):  # Hide on mobile
                    ui.link("Home", "/").classes("text-white hover:text-blue-200 px-3 py-2 rounded-lg transition-colors")
                    ui.link("Advanced Search", "/advanced").classes("text-white hover:text-blue-200 px-3 py-2 rounded-lg transition-colors")
                    ui.link("Summaries", "/summaries").classes("text-white hover:text-blue-200 px-3 py-2 rounded-lg transition-colors")
            
            # Right section - User account, settings, dark mode toggle
            with ui.row().classes("items-center gap-2"):
                # Dark mode toggle
                with ui.button(icon="dark_mode" if not dark_mode.value else "light_mode").props("flat round").classes("text-white"):
                    ui.tooltip("Toggle dark/light mode")
                    
                def toggle_dark_mode():
                    dark_mode.toggle()
                    
                dark_mode.bind_value_from(toggle_dark_mode)
                
                # Authentication section
                current_user = get_current_user()
                if current_user:
                    with ui.avatar():
                        ui.tooltip(f"Logged in as {current_user['username']}")
                        ui.button(icon="person").props("flat round")
                        
                    with ui.menu().classes("w-48") as menu:
                        ui.menu_item("My Profile", on_click=lambda: ui.navigate("/profile")).props("v-close-popup")
                        ui.menu_item("Settings", on_click=lambda: ui.navigate("/settings")).props("v-close-popup")
                        ui.separator()
                        ui.menu_item("Logout", on_click=lambda: ui.navigate("/logout")).props("v-close-popup")
                else:
                    ui.button("Login", on_click=lambda: ui.navigate("/login")).classes(
                        "bg-blue-800 hover:bg-blue-900 text-white px-4 py-2 rounded-lg transition-colors"
                    )    # Mobile menu (hamburger) - visible only on small screens
    with ui.element("div").classes("md:hidden bg-blue-700 text-white p-2"):
        with ui.row().classes("justify-between items-center"):
            ui.label("Menu").classes("text-sm")            # Hamburger menu button with connected menu
            menu_button = ui.button(icon="menu").props("flat round").classes("text-white")
            with menu_button:
                ui.tooltip("Menu")  # Tooltip directly added to the button context
            
            # Create menu and connect it to the button
            menu = ui.menu().classes("w-full bg-blue-700 text-white")
            menu_button.on("click", menu.open)
            with menu:
                ui.menu_item("Home", on_click=lambda: ui.navigate("/")).props("v-close-popup")
                ui.menu_item("Advanced Search", on_click=lambda: ui.navigate("/advanced")).props("v-close-popup")
                ui.menu_item("Summaries", on_click=lambda: ui.navigate("/summaries")).props("v-close-popup")
                ui.separator()
                
                # Add user-specific menu items
                if current_user:
                    ui.menu_item("My Profile", on_click=lambda: ui.navigate("/profile")).props("v-close-popup")
                    ui.menu_item("Settings", on_click=lambda: ui.navigate("/settings")).props("v-close-popup")
                    ui.menu_item("Logout", on_click=lambda: ui.navigate("/logout")).props("v-close-popup")
                else:
                    ui.menu_item("Login", on_click=lambda: ui.navigate("/login")).props("v-close-popup")