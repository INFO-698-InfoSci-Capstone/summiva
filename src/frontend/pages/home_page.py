from nicegui import ui
from typing import List

from models.summary import SummaryItem
from services.summary_service import add_summary, search_summaries, get_all_tags, get_all_groups
from components.summary_card import summary_card

def home_page():
    """Home page UI with summary list and search functionality"""
    ui.label("🔗 Summiva - Home").classes("text-2xl font-bold")
    
    # URL input and generation section
    with ui.card().classes("w-full shadow-md mb-4"):
        ui.label("Generate New Summary").classes("text-lg font-bold")
        with ui.row().classes("w-full items-center gap-2"):
            url_input = ui.input("Enter URL to summarize...").classes("w-3/4")
            generate_btn = ui.button("Generate Summary", on_click=lambda: generate_and_refresh(url_input.value))
            generate_btn.classes("bg-blue-500 text-white")
    
    # Search section with more options
    with ui.card().classes("w-full shadow-md mb-4"):
        ui.label("Search Summaries").classes("text-lg font-bold")
        with ui.row().classes("w-full items-center gap-2"):
            search_field = ui.select(
                ["title", "content", "tags", "group"], 
                value="title", 
                label="Search by"
            ).classes("w-1/4")
            search_input = ui.input("Search here...").classes("w-2/4")
            
            # Add filter dropdowns
            tags = get_all_tags()
            groups = get_all_groups()
            tag_filter = ui.select(options=["All Tags"] + tags, value="All Tags", label="Filter by Tag").classes("w-1/4")
            group_filter = ui.select(options=["All Groups"] + groups, value="All Groups", label="Filter by Group").classes("w-1/4")
    
    # Status indicators
    with ui.row().classes("w-full items-center justify-between mb-4"):
        status_label = ui.label("Ready").classes("text-sm text-gray-500")
        loading_indicator = ui.spinner("dots").classes("text-blue-500 text-2xl")
        loading_indicator.set_visibility(False)
    
    # Results section
    result_container = ui.card().classes("w-full")
    result_column = ui.column().classes("w-full")
    
    def generate_and_refresh(url):
        if not url:
            ui.notify("Please enter a valid URL", type="warning")
            return
            
        loading_indicator.set_visibility(True)
        status_label.set_text("Generating summary...")
        generate_btn.set_enabled(False)
        
        try:
            new_summary = add_summary(url)
            
            if new_summary:
                refresh_cards(search_summaries("", "title"))  # Show all summaries
                url_input.set_value("")
                ui.notify(f"Summary generated for {url}", type="positive")
                status_label.set_text(f"Summary for {url} created successfully")
            else:
                ui.notify("Failed to generate summary", type="negative")
                status_label.set_text("Error: Failed to generate summary")
        except Exception as e:
            ui.notify(f"Error: {str(e)}", type="negative")
            status_label.set_text(f"Error: {str(e)}")
        finally:
            loading_indicator.set_visibility(False)
            generate_btn.set_enabled(True)
    
    def refresh_cards(items: List[SummaryItem]):
        result_column.clear()
        
        if not items:
            with result_column:
                ui.label("No summaries found").classes("text-lg text-gray-500 p-4")
                return
        
        status_label.set_text(f"Displaying {len(items)} summaries")
                
        for item in items:
            with result_column:
                summary_card(item)
    
    def apply_filters():
        query = search_input.value
        field = search_field.value
        filtered = search_summaries(query, field)
        
        # Apply tag filter if selected
        if tag_filter.value != "All Tags":
            filtered = [item for item in filtered if tag_filter.value in item.tags]
            
        # Apply group filter if selected
        if group_filter.value != "All Groups":
            filtered = [item for item in filtered if item.group == group_filter.value]
            
        refresh_cards(filtered)
        
    def on_search_change(e):
        apply_filters()
    
    search_input.on("input", on_search_change)
    search_field.on("change", lambda: apply_filters())
    tag_filter.on("change", lambda: apply_filters())
    group_filter.on("change", lambda: apply_filters())
    
    # Show all summaries initially
    refresh_cards(search_summaries("", "title"))