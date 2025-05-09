from nicegui import ui
import webbrowser
from models.summary import SummaryItem

def summary_card(item: SummaryItem):
    """Create a card for displaying a summary"""
    with ui.card().classes("w-full mb-4 shadow-md hover:shadow-lg transition-shadow duration-300"):
        with ui.row().classes("w-full justify-between items-center p-2 bg-gray-50"):
            ui.label(item.title).classes("text-lg font-bold truncate max-w-[70%]")
            with ui.row().classes("gap-2"):
                ui.tooltip("Open original URL").classes("bg-gray-800").target(
                    ui.button(icon="open_in_new", on_click=lambda: ui.open(item.url, new_tab=True))
                    .props("flat round").classes("text-green-600")
                )
                ui.tooltip("Copy URL").classes("bg-gray-800").target(
                    ui.button(icon="content_copy", on_click=lambda: copy_to_clipboard(item.url))
                    .props("flat round").classes("text-blue-600")
                )
        
        with ui.row().classes("w-full px-4 py-2"):
            ui.label(f"Group: ").classes("text-sm font-bold text-gray-700")
            ui.badge(item.group).classes("bg-purple-100 text-purple-800")
        
        with ui.row().classes("w-full px-4 py-2"):
            ui.label("Tags: ").classes("text-sm font-bold text-gray-700")
            with ui.row().classes("flex-wrap gap-1"):
                for tag in item.tags:
                    ui.badge(tag).props("outline").classes("text-blue-800 border-blue-500")
        
        ui.separator()
        
        with ui.card().classes("w-full bg-gray-50 rounded-md p-3 my-2"):
            ui.label("Summary").classes("text-sm font-bold text-gray-700 mb-1")
            ui.label(item.short_summary).classes("text-gray-800 whitespace-pre-wrap")
        
        with ui.row().classes("w-full justify-between p-2"):
            ui.button("Full Summary", on_click=lambda: show_full_summary(item)) \
                .props("outline").classes("text-blue-600")
            
            with ui.row().classes("gap-1"):
                ui.button("Share", icon="share", on_click=lambda: share_summary(item)) \
                    .props("outline").classes("text-green-600")
                ui.button("Copy Summary", icon="content_copy", on_click=lambda: copy_to_clipboard(item.short_summary)) \
                    .props("outline").classes("text-gray-600")

def show_full_summary(item: SummaryItem):
    """Open a dialog with the full summary"""
    dialog = ui.dialog().classes("w-full max-w-3xl")
    with dialog:
        with ui.card().classes("p-4"):
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(item.title).classes("text-xl font-bold")
                ui.button(icon="close", on_click=dialog.close).props("flat round")
            
            ui.separator()
            
            with ui.scroll_area().classes("h-[60vh]"):
                with ui.column().classes("p-2"):
                    # URL info
                    with ui.card().classes("w-full bg-blue-50 p-3 mb-3"):
                        ui.label("Source URL").classes("text-sm font-bold text-gray-700")
                        with ui.row().classes("items-center gap-2"): 
                            ui.link(item.url, item.url, new_tab=True).classes("text-blue-600 truncate")
                            ui.button(icon="content_copy", on_click=lambda: copy_to_clipboard(item.url)) \
                                .props("flat round").classes("text-xs")
                    
                    # Summary content
                    ui.label("Full Summary").classes("text-lg font-bold mb-2")
                    ui.markdown(item.full_summary).classes("whitespace-pre-wrap")
                    
                    # Tags and group
                    with ui.row().classes("mt-4 gap-2"):
                        with ui.column().classes("w-1/2"):
                            ui.label("Group").classes("text-sm font-bold")
                            ui.badge(item.group).classes("bg-purple-100 text-purple-800")
                        with ui.column().classes("w-1/2"):
                            ui.label("Tags").classes("text-sm font-bold")
                            with ui.row().classes("flex-wrap gap-1"):
                                for tag in item.tags:
                                    ui.badge(tag).props("outline").classes("text-blue-800 border-blue-500")
            
            ui.separator()
            
            with ui.row().classes("w-full justify-end gap-2 mt-2"):
                ui.button("Copy Full Summary", icon="content_copy", 
                         on_click=lambda: copy_to_clipboard(item.full_summary))
                ui.button("Close", icon="close", on_click=dialog.close) \
                    .classes("bg-blue-500 text-white")
    
    dialog.open()

def copy_to_clipboard(text: str):
    """Copy text to clipboard and show notification"""
    ui.run_javascript(f'navigator.clipboard.writeText({repr(text)})', on_result=lambda _: 
                     ui.notify("Copied to clipboard!", type="positive"))

def share_summary(item: SummaryItem):
    """Show sharing options"""
    share_dialog = ui.dialog().classes("w-full max-w-md")
    with share_dialog:
        with ui.card().classes("p-4"):
            ui.label("Share Summary").classes("text-lg font-bold mb-2")
            
            ui.separator()
            
            with ui.column().classes("gap-2 my-3"):
                ui.label("Share via:").classes("text-sm font-bold")
                
                email_subject = f"Check out this summary: {item.title}"
                email_body = f"I thought you might find this interesting:\n\n{item.title}\n\n{item.short_summary}\n\nOriginal source: {item.url}"
                email_link = f"mailto:?subject={email_subject}&body={email_body}"
                
                twitter_text = f"Check out this summary: {item.title} {item.url}"
                twitter_link = f"https://twitter.com/intent/tweet?text={twitter_text}"
                
                linkedin_link = f"https://www.linkedin.com/sharing/share-offsite/?url={item.url}"
                
                with ui.row().classes("gap-2"):
                    ui.button("Email", icon="email", on_click=lambda: ui.open(email_link)) \
                        .classes("bg-red-500 text-white")
                    ui.button("Twitter", icon="flutter_dash", on_click=lambda: ui.open(twitter_link, new_tab=True)) \
                        .classes("bg-blue-400 text-white")
                    ui.button("LinkedIn", icon="work", on_click=lambda: ui.open(linkedin_link, new_tab=True)) \
                        .classes("bg-blue-700 text-white")
            
            ui.separator()
            
            with ui.column().classes("gap-2 my-3"):
                ui.label("Or copy link:").classes("text-sm font-bold")
                with ui.row().classes("gap-2 items-center"):
                    link_input = ui.input(value=item.url).classes("w-full")
                    ui.button(icon="content_copy", on_click=lambda: copy_to_clipboard(item.url)) \
                        .props("flat round").classes("text-blue-600")
            
            with ui.row().classes("justify-end mt-2"):
                ui.button("Close", on_click=share_dialog.close) \
                    .classes("bg-gray-500 text-white")
    
    share_dialog.open()