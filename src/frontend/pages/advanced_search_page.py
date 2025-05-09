from nicegui import ui
from typing import List, Literal, Dict, Set
from datetime import datetime, timedelta

from models.summary import SummaryItem
from services.summary_service import get_all_tags, get_all_groups, search_summaries
from components.summary_card import summary_card

def advanced_search_page():
    """Advanced search page UI with comprehensive filtering and visualization options"""
    ui.label("🔍 Summiva - Advanced Search").classes("text-2xl font-bold mb-4")
    
    # Get all available tags and groups for filtering
    tags_set = get_all_tags()
    groups_set = get_all_groups()
    
    # State for tracking selected filters
    selected_tags: Set[str] = set()
    selected_groups: Set[str] = set()
    date_range: Dict[str, str] = {"from": "", "to": ""}
    search_query = ""
    search_in = "title"  # Default search field
    
    # Results container
    results_container = ui.card().classes("w-full mt-4")
    results_stats = ui.label("").classes("text-sm text-gray-600 mb-2")
    results_column = ui.column().classes("w-full")
    
    # Main layout with filters and results sections
    with ui.row().classes("gap-4 w-full"):
        # Left sidebar with all filters
        with ui.card().classes("w-1/3 p-4"):
            ui.label("Search & Filters").classes("font-bold text-xl mb-4")
            
            # Search box
            with ui.card().classes("mb-4 p-3 bg-blue-50"):
                ui.label("Search Content").classes("font-bold mb-2")
                with ui.row().classes("gap-2 items-center"):
                    search_input = ui.input("Enter keywords...").classes("w-full")
                    search_field = ui.select(
                        ["title", "content", "tags", "group"],
                        value="title", 
                        label="In"
                    ).classes("w-1/3")
            
            # Tag filter section with search and checkboxes
            with ui.expansion("Filter by Tags", icon="sell").classes("w-full mb-2").props("expand-separator"):
                tag_search = ui.input("Search tags...").classes("w-full mb-2")
                
                tag_container = ui.column().classes("max-h-48 overflow-y-auto")
                
                # Create tag checkboxes
                def render_tags(filter_text=""):
                    tag_container.clear()
                    filtered_tags = [tag for tag in tags_set if filter_text.lower() in tag.lower()] if filter_text else tags_set
                    
                    if not filtered_tags:
                        with tag_container:
                            ui.label("No matching tags").classes("text-gray-500")
                        return
                    
                    with tag_container:
                        for tag in sorted(filtered_tags):
                            with ui.row().classes("items-center w-full"):
                                tag_cb = ui.checkbox(tag)
                                tag_cb.classes("text-sm")
                                # Fix lambda parameter order
                                def make_tag_handler(tag_value):
                                    return lambda val: toggle_tag(tag_value, val)
                                tag_cb.bind_value_to(make_tag_handler(tag))
                                ui.badge(str(len([s for s in search_summaries("", "title") if tag in s.tags])))
                
                # Tag search functionality
                tag_search.on("input", lambda e: render_tags(e.value))
                
                # Buttons for tag selection
                with ui.row().classes("gap-2 mt-2"):
                    ui.button("Select All", on_click=lambda: select_all_tags(True)) \
                        .props("outline size=sm").classes("text-blue-600")
                    ui.button("Clear All", on_click=lambda: select_all_tags(False)) \
                        .props("outline size=sm").classes("text-gray-600")
            
            # Group filter
            with ui.expansion("Filter by Groups", icon="folder").classes("w-full mb-2").props("expand-separator"):
                group_container = ui.column().classes("max-h-48 overflow-y-auto")
                
                # Create group checkboxes
                with group_container:
                    for group in sorted(groups_set):
                        with ui.row().classes("items-center w-full"):
                            group_cb = ui.checkbox(group)
                            group_cb.classes("text-sm")
                            # Fix lambda parameter order
                            def make_group_handler(group_value):
                                return lambda val: toggle_group(group_value, val)
                            group_cb.bind_value_to(make_group_handler(group))
                            # Fix reference to group variable
                            ui.badge(str(len([s for s in search_summaries("", "title") if group == s.group])))
                
                # Buttons for group selection
                with ui.row().classes("gap-2 mt-2"):
                    ui.button("Select All", on_click=lambda: select_all_groups(True)) \
                        .props("outline size=sm").classes("text-purple-600")
                    ui.button("Clear All", on_click=lambda: select_all_groups(False)) \
                        .props("outline size=sm").classes("text-gray-600")
            
            # Date range filter (placeholder - would need actual date fields in SummaryItem)
            with ui.expansion("Filter by Date", icon="calendar_today").classes("w-full mb-2").props("expand-separator"):
                with ui.column().classes("gap-2"):
                    ui.date(value=datetime.now() - timedelta(days=30), label="From") \
                        .classes("w-full").bind_value_to(lambda d: set_date_range("from", d))
                    ui.date(value=datetime.now(), label="To") \
                        .classes("w-full").bind_value_to(lambda d: set_date_range("to", d))
            
            # Apply filters button
            ui.button("Apply Filters", on_click=apply_filters).classes("w-full bg-blue-600 text-white mt-4")
        
        # Right content area with visualization and results
        with ui.column().classes("w-2/3 gap-4"):
            # Visualization toggle and controls
            with ui.card().classes("w-full p-4"):
                with ui.row().classes("justify-between items-center"):
                    ui.label("Result Visualization").classes("font-bold text-lg")
                    
                    with ui.toggle({
                        "list": "List View", 
                        "grid": "Grid View",
                        "chart": "Chart View"
                    }, value="list").classes("ml-auto") as view_toggle:
                        pass
            
            # Main results area
            with results_container:
                ui.label("Results").classes("font-bold text-lg mb-2")
                results_stats
                
                # Create a conditional container for different views
                list_view = ui.element("div")
                grid_view = ui.element("div").classes("hidden grid grid-cols-2 gap-4")
                chart_view = ui.element("div").classes("hidden h-96 w-full")
                
                # Setup different views
                with list_view:
                    results_column
                
                with chart_view:
                    ui.label("Tag Distribution").classes("font-bold text-center")
                    # This would be a placeholder for an actual chart visualization
                    with ui.row().classes("h-80 items-end gap-1 pt-4 justify-center"):
                        for i, tag in enumerate(tags_set[:8]):  # Show only first 8 tags for demo
                            height = 20 + (i * 10)  # Demo heights
                            with ui.column().classes(f"items-center"):
                                ui.element("div").style(f"height: {height}px; width: 40px").classes("bg-blue-500 rounded-t-lg")
                                ui.label(tag).classes("text-xs mt-2 rotate-45 origin-top-left")
    
    # Helper functions for filter state management
    def toggle_tag(tag: str, selected: bool):
        if selected:
            selected_tags.add(tag)
        else:
            selected_tags.discard(tag)
    
    def toggle_group(group: str, selected: bool):
        if selected:
            selected_groups.add(group)
        else:
            selected_groups.discard(group)
    
    def select_all_tags(selected: bool):
        if selected:
            selected_tags.update(tags_set)
        else:
            selected_tags.clear()
        render_tags()  # Refresh UI
    
    def select_all_groups(selected: bool):
        if selected:
            selected_groups.update(groups_set)
        else:
            selected_groups.clear()
        # Refresh UI (would need to implement this)
    
    def set_date_range(which: str, date_val: datetime):
        date_range[which] = date_val.strftime("%Y-%m-%d") if date_val else ""
    
    # Function to apply all filters and search
    def apply_filters():
        nonlocal search_query, search_in
        search_query = search_input.value
        search_in = search_field.value
        
        # Get base results from search
        results = search_summaries(search_query, search_in)
        
        # Apply tag filters if any are selected
        if selected_tags:
            results = [item for item in results if any(tag in item.tags for tag in selected_tags)]
        
        # Apply group filters if any are selected
        if selected_groups:
            results = [item for item in results if item.group in selected_groups]
        
        # Update stats and render results
        results_stats.set_text(f"Found {len(results)} matching summaries")
        render_results(results)
        
        # Update view based on selected view mode
        update_view()
    
    # Function to render results based on current filters
    def render_results(filtered_items: List[SummaryItem]):
        # Clear both views
        results_column.clear()
        grid_view.clear()
        
        if not filtered_items:
            with results_column:
                ui.label("No matching summaries found").classes("text-lg text-gray-500 p-4")
            return
        
        # Render list view
        for item in filtered_items:
            with results_column:
                summary_card(item)
        
        # Render grid view
        with grid_view:
            for item in filtered_items:
                with ui.card().classes("p-3"):
                    ui.label(item.title).classes("font-bold truncate")
                    ui.label(item.short_summary[:100] + "...").classes("text-sm text-gray-600 line-clamp-2 h-12")
                    with ui.row().classes("mt-2 justify-between items-center"):
                        ui.badge(item.group).classes("bg-purple-100 text-purple-800")
                        ui.button("View", on_click=lambda i=item: show_full_summary(i)) \
                            .props("flat dense").classes("text-blue-600")
    
    # Function to show full summary in a dialog
    def show_full_summary(item: SummaryItem):
        from components.summary_card import show_full_summary
        show_full_summary(item)
    
    # Function to update view based on toggle
    def update_view():
        if view_toggle.value == "list":
            list_view.classes("block")
            grid_view.classes("hidden")
            chart_view.classes("hidden")
        elif view_toggle.value == "grid":
            list_view.classes("hidden")
            grid_view.classes("grid")
            chart_view.classes("hidden")
        else:  # chart view
            list_view.classes("hidden")
            grid_view.classes("hidden")
            chart_view.classes("block")
    
    # Connect view toggle to view update function
    view_toggle.on("change", lambda _: update_view())
    
    # Initial render
    render_tags()
    render_results([])  # Start with empty results
    ui.label("Use the filters on the left to find summaries").classes("text-gray-500 p-4")