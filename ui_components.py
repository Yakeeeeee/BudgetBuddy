"""
UI Components for Budget Tracker
Custom UI components and utilities using CustomTkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class UIComponents:
    def __init__(self, root):
        self.root = root
        self.setup_styles()
    
    def setup_styles(self):
        """Setup custom styles and colors"""
        self.colors = {
            'primary': "#1f538d",
            'secondary': "#3a7ebf",
            'success': "#4CAF50",
            'warning': "#FF9800",
            'info': "#2196F3",
            'danger': "#F44336",
            'purple': "#9C27B0",
            'light_gray': "#f0f0f0",
            'dark_gray': "#333333"
        }
    
    def create_stats_card(self, parent, title: str, value: str, color: str = None) -> ctk.CTkFrame:
        """Create a statistics card widget"""
        card = ctk.CTkFrame(parent)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12, "bold"),
            text_color="gray70"
        )
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 18, "bold"),
            text_color=color if color else None
        )
        value_label.pack(pady=(5, 15))
        
        return card
    
    def create_data_table(self, parent, headers: List[str], data: List[List[Any]], 
                         actions: List[Dict[str, Callable]] = None) -> ctk.CTkFrame:
        """Create a data table with optional action buttons"""
        table_frame = ctk.CTkFrame(parent)
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(table_frame)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Headers
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                scrollable_frame,
                text=header,
                font=("Arial", 12, "bold")
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        for row_idx, row_data in enumerate(data, start=1):
            for col_idx, cell_data in enumerate(row_data):
                cell_label = ctk.CTkLabel(
                    scrollable_frame,
                    text=str(cell_data)
                )
                cell_label.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")
            
            # Action buttons
            if actions:
                action_frame = ctk.CTkFrame(scrollable_frame)
                action_frame.grid(row=row_idx, column=len(headers), padx=10, pady=5)
                
                for action in actions:
                    btn = ctk.CTkButton(
                        action_frame,
                        text=action['text'],
                        width=80,
                        command=lambda r=row_idx-1, cmd=action['command']: cmd(r)
                    )
                    btn.pack(side="left", padx=2)
        
        return table_frame
    
    def create_form_field(self, parent, label_text: str, field_type: str = "entry", 
                         options: List[str] = None, **kwargs) -> tuple:
        """Create a form field with label"""
        field_frame = ctk.CTkFrame(parent)
        
        # Label
        label = ctk.CTkLabel(field_frame, text=label_text)
        label.pack(side="left", padx=(10, 5))
        
        # Field
        if field_type == "entry":
            field = ctk.CTkEntry(field_frame, **kwargs)
        elif field_type == "combobox":
            field = ctk.CTkComboBox(field_frame, values=options or [], **kwargs)
        elif field_type == "checkbox":
            field = ctk.CTkCheckBox(field_frame, text="", **kwargs)
        elif field_type == "textbox":
            field = ctk.CTkTextbox(field_frame, **kwargs)
        else:
            field = ctk.CTkEntry(field_frame, **kwargs)
        
        field.pack(side="left", padx=(5, 10))
        
        return field_frame, field
    
    def create_chart_container(self, parent, title: str = "") -> ctk.CTkFrame:
        """Create a container for matplotlib charts"""
        chart_frame = ctk.CTkFrame(parent)
        
        if title:
            title_label = ctk.CTkLabel(
                chart_frame,
                text=title,
                font=("Arial", 16, "bold")
            )
            title_label.pack(pady=(10, 0))
        
        return chart_frame
    
    def create_progress_bar(self, parent, value: float, max_value: float = 100, 
                           color: str = None) -> ctk.CTkProgressBar:
        """Create a progress bar"""
        progress = ctk.CTkProgressBar(parent)
        if color:
            progress.configure(progress_color=color)
        
        progress.set(value / max_value if max_value > 0 else 0)
        return progress
    
    def create_info_panel(self, parent, title: str, content: List[str]) -> ctk.CTkFrame:
        """Create an information panel"""
        panel = ctk.CTkFrame(parent)
        
        # Title
        title_label = ctk.CTkLabel(
            panel,
            text=title,
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Content
        for item in content:
            content_label = ctk.CTkLabel(
                panel,
                text=item,
                font=("Arial", 11),
                wraplength=250
            )
            content_label.pack(pady=2, padx=15, anchor="w")
        
        return panel
    
    def create_alert_banner(self, parent, message: str, alert_type: str = "info") -> ctk.CTkFrame:
        """Create an alert banner"""
        color_map = {
            'info': self.colors['info'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'danger': self.colors['danger']
        }
        
        banner = ctk.CTkFrame(
            parent,
            fg_color=color_map.get(alert_type, self.colors['info'])
        )
        
        alert_label = ctk.CTkLabel(
            banner,
            text=message,
            font=("Arial", 12, "bold"),
            text_color="white"
        )
        alert_label.pack(pady=10, padx=15)
        
        return banner
    
    def create_sidebar_button(self, parent, text: str, command: Callable, 
                             active: bool = False) -> ctk.CTkButton:
        """Create a sidebar navigation button"""
        if active:
            fg_color = self.colors['primary']
            hover_color = self.colors['secondary']
        else:
            fg_color = "transparent"
            hover_color = self.colors['secondary']
        
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=180,
            height=40,
            fg_color=fg_color,
            hover_color=hover_color,
            anchor="w"
        )
        
        return button
    
    def create_card_layout(self, parent, cards_data: List[Dict[str, Any]], 
                          columns: int = 3) -> ctk.CTkFrame:
        """Create a grid layout of cards"""
        cards_container = ctk.CTkFrame(parent)
        
        for i, card_data in enumerate(cards_data):
            row = i // columns
            col = i % columns
            
            card = self.create_stats_card(
                cards_container,
                card_data.get('title', ''),
                card_data.get('value', ''),
                card_data.get('color', None)
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights
        for i in range(columns):
            cards_container.grid_columnconfigure(i, weight=1)
        
        return cards_container
    
    def create_tabview(self, parent, tabs: Dict[str, Callable]) -> ctk.CTkTabview:
        """Create a tab view with multiple tabs"""
        tabview = ctk.CTkTabview(parent)
        
        for tab_name, tab_content_func in tabs.items():
            tab = tabview.add(tab_name)
            if tab_content_func:
                tab_content_func(tab)
        
        return tabview
    
    def create_modal_dialog(self, title: str, content_func: Callable, 
                           width: int = 400, height: int = 300) -> ctk.CTkToplevel:
        """Create a modal dialog window"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add content
        content_frame = ctk.CTkFrame(dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if content_func:
            content_func(content_frame)
        
        return dialog
    
    def create_search_filter_bar(self, parent, search_callback: Callable = None,
                                filter_options: List[str] = None,
                                filter_callback: Callable = None) -> ctk.CTkFrame:
        """Create a search and filter bar"""
        filter_frame = ctk.CTkFrame(parent)
        
        # Search entry
        if search_callback:
            search_label = ctk.CTkLabel(filter_frame, text="Search:")
            search_label.pack(side="left", padx=(10, 5))
            
            search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="Enter search term...")
            search_entry.pack(side="left", padx=(5, 10))
            
            search_btn = ctk.CTkButton(
                filter_frame,
                text="Search",
                width=80,
                command=lambda: search_callback(search_entry.get())
            )
            search_btn.pack(side="left", padx=(0, 10))
        
        # Filter dropdown
        if filter_options and filter_callback:
            filter_label = ctk.CTkLabel(filter_frame, text="Filter:")
            filter_label.pack(side="left", padx=(10, 5))
            
            filter_combo = ctk.CTkComboBox(
                filter_frame,
                values=filter_options,
                command=filter_callback
            )
            filter_combo.pack(side="left", padx=(5, 10))
        
        return filter_frame
    
    def create_loading_spinner(self, parent) -> ctk.CTkFrame:
        """Create a loading spinner (simplified)"""
        spinner_frame = ctk.CTkFrame(parent)
        
        spinner_label = ctk.CTkLabel(
            spinner_frame,
            text="Loading...",
            font=("Arial", 12)
        )
        spinner_label.pack(pady=20)
        
        progress = ctk.CTkProgressBar(spinner_frame, mode="indeterminate")
        progress.pack(pady=10)
        progress.start()
        
        return spinner_frame
    
    def create_confirmation_dialog(self, title: str, message: str, 
                                  confirm_callback: Callable = None) -> None:
        """Create a confirmation dialog"""
        def on_confirm():
            dialog.destroy()
            if confirm_callback:
                confirm_callback()
        
        def on_cancel():
            dialog.destroy()
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (175)
        y = (dialog.winfo_screenheight() // 2) - (75)
        dialog.geometry(f"350x150+{x}+{y}")
        
        # Message
        message_label = ctk.CTkLabel(dialog, text=message, wraplength=300)
        message_label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=10)
        
        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Confirm",
            command=on_confirm,
            fg_color=self.colors['danger']
        )
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=10)
    
    def create_notification_toast(self, message: str, duration: int = 3000,
                                 notification_type: str = "info") -> None:
        """Create a toast notification"""
        toast = ctk.CTkToplevel(self.root)
        toast.title("")
        toast.geometry("300x80")
        toast.overrideredirect(True)
        
        # Position at top-right
        x = self.root.winfo_rootx() + self.root.winfo_width() - 320
        y = self.root.winfo_rooty() + 20
        toast.geometry(f"300x80+{x}+{y}")
        
        # Color based on type
        color_map = {
            'info': self.colors['info'],
            'success': self.colors['success'],
            'warning': self.colors['warning'],
            'error': self.colors['danger']
        }
        
        toast.configure(fg_color=color_map.get(notification_type, self.colors['info']))
        
        # Message
        message_label = ctk.CTkLabel(
            toast,
            text=message,
            text_color="white",
            font=("Arial", 11, "bold"),
            wraplength=280
        )
        message_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Auto-close
        toast.after(duration, toast.destroy)
    
    def update_table_data(self, table_frame: ctk.CTkFrame, headers: List[str], 
                         data: List[List[Any]], actions: List[Dict[str, Callable]] = None):
        """Update existing table with new data"""
        # Clear existing content
        for widget in table_frame.winfo_children():
            widget.destroy()
        
        # Recreate table
        self.create_data_table(table_frame, headers, data, actions)
    
    def get_color_scheme(self, theme: str = "dark") -> Dict[str, str]:
        """Get color scheme based on theme"""
        if theme == "light":
            return {
                'background': "#ffffff",
                'foreground': "#000000",
                'primary': "#0066cc",
                'secondary': "#4d94ff",
                'accent': "#f0f0f0",
                'success': "#28a745",
                'warning': "#ffc107",
                'danger': "#dc3545",
                'info': "#17a2b8"
            }
        else:
            return {
                'background': "#2b2b2b",
                'foreground': "#ffffff",
                'primary': "#1f538d",
                'secondary': "#3a7ebf",
                'accent': "#404040",
                'success': "#4CAF50",
                'warning': "#FF9800",
                'danger': "#F44336",
                'info': "#2196F3"
            }
