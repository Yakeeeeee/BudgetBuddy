"""
Budget Tracker 50/30/20 - Main Application
A comprehensive budget tracking desktop application using the 50/30/20 rule
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar, DateEntry
import json

# Import custom modules
from data_manager import DataManager
from ui_components import UIComponents
from charts import ChartManager
from settings_manager import SettingsManager

class BudgetTrackerApp:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("BudgetBuddy")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Initialize managers
        self.data_manager = DataManager()
        self.ui_components = UIComponents(self.root)
        self.chart_manager = ChartManager()
        self.settings_manager = SettingsManager()
        
        # Load settings and apply theme
        self.settings = self.settings_manager.load_settings()
        self.apply_theme()
        
        # Current page tracking
        self.current_page = "dashboard"
        
        # Initialize UI
        self.setup_ui()
        self.show_dashboard()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def apply_theme(self):
        """Apply the selected theme"""
        theme = self.settings.get('theme', 'dark')
        if theme == 'light':
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create sidebar
        self.setup_sidebar()
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(15, 0))
    
    def setup_sidebar(self):
        """Setup navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self.main_container, width=220)
        self.sidebar.pack(side="left", fill="y", padx=(0, 15))
        self.sidebar.pack_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="BudgetBuddy", 
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "dashboard", self.show_dashboard),
            ("Income", "income", self.show_income),
            ("Essentials", "essentials", self.show_essentials),
            ("Bills", "bills", self.show_bills),
            ("Non-Essentials", "non_essentials", self.show_non_essentials),
            ("Savings", "savings", self.show_savings),
            ("Analytics", "analytics", self.show_analytics),
            ("Calendar", "calendar", self.show_calendar),
            ("Settings", "settings", self.show_settings)
        ]
        
        self.nav_buttons = {}
        for text, key, command in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=200,
                height=45,
                font=("Arial", 13, "bold")
            )
            btn.pack(pady=8, padx=10)
            self.nav_buttons[key] = btn
    
    def clear_content(self):
        """Clear the main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_nav_buttons(self, active_page):
        """Update navigation button states"""
        for key, button in self.nav_buttons.items():
            if key == active_page:
                button.configure(fg_color=("#3B8ED0", "#1F6AA5"))
            else:
                button.configure(fg_color=("#3A7EBF", "#1F538D"))
    
    def show_dashboard(self):
        """Display the main dashboard"""
        self.clear_content()
        self.current_page = "dashboard"
        self.update_nav_buttons("dashboard")
        
        # Main title
        title = ctk.CTkLabel(
            self.content_frame, 
            text="Budget Dashboard", 
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        # Get data for calculations
        income_data = self.data_manager.get_income_data()
        essentials_data = self.data_manager.get_essentials_data()
        bills_data = self.data_manager.get_bills_data()
        non_essentials_data = self.data_manager.get_non_essentials_data()
        savings_data = self.data_manager.get_savings_data()
        
        # Calculate totals
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        total_essentials = essentials_data['Actual'].sum() if not essentials_data.empty else 0
        total_non_essentials = non_essentials_data['Amount'].sum() if not non_essentials_data.empty else 0
        total_savings = savings_data['Deposit'].sum() if not savings_data.empty else 0
        unpaid_bills = len(bills_data[bills_data['Status'] == 'Unpaid']) if not bills_data.empty else 0
        
        # Create enhanced stats cards container
        stats_container = ctk.CTkFrame(self.content_frame)
        stats_container.pack(fill="x", pady=25, padx=25)
        
        # Stats cards
        stats = [
            ("Total Income", f"₱{total_income:,.2f}", "#4CAF50"),
            ("Essentials (50%)", f"₱{total_essentials:,.2f}", "#FF9800"),
            ("Non-Essentials (30%)", f"₱{total_non_essentials:,.2f}", "#2196F3"),
            ("Savings (20%)", f"₱{total_savings:,.2f}", "#9C27B0"),
            ("Unpaid Bills", str(unpaid_bills), "#F44336")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = self.ui_components.create_stats_card(stats_container, label, value, color)
            card.grid(row=0, column=i, padx=15, pady=15, sticky="ew", ipadx=10, ipady=5)
        
        stats_container.grid_columnconfigure(tuple(range(5)), weight=1)
        
        # Charts container with improved layout
        charts_container = ctk.CTkFrame(self.content_frame)
        charts_container.pack(fill="both", expand=True, pady=20, padx=20)
        
        # Left side - Budget charts
        chart_left_frame = ctk.CTkFrame(charts_container)
        chart_left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Budget allocation pie chart
        if total_income > 0:
            allocations = {
                'Essentials (50%)': total_income * 0.5,
                'Non-Essentials (30%)': total_income * 0.3,
                'Savings (20%)': total_income * 0.2
            }
            
            actuals = {
                'Essentials (50%)': total_essentials,
                'Non-Essentials (30%)': total_non_essentials,
                'Savings (20%)': total_savings
            }
            
            pie_chart = self.chart_manager.create_budget_pie_chart(allocations, actuals)
            canvas = FigureCanvasTkAgg(pie_chart, chart_left_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
        
        # Right side - Enhanced summary
        summary_frame = ctk.CTkFrame(charts_container, width=350)
        summary_frame.pack(side="right", fill="y", padx=(10, 0))
        summary_frame.pack_propagate(False)
        
        summary_title = ctk.CTkLabel(summary_frame, text="Financial Overview", font=("Arial", 18, "bold"))
        summary_title.pack(pady=15)
        
        # Quick metrics
        metrics_frame = ctk.CTkFrame(summary_frame)
        metrics_frame.pack(fill="x", padx=15, pady=10)
        
        # Budget targets for 50/30/20 rule
        target_essentials = total_income * 0.5 if total_income > 0 else 0
        target_non_essentials = total_income * 0.3 if total_income > 0 else 0
        target_savings = total_income * 0.2 if total_income > 0 else 0
        
        # Remaining budget percentages
        remaining_essentials = max(0, target_essentials - total_essentials) if total_income > 0 else 0
        remaining_non_essentials = max(0, target_non_essentials - total_non_essentials) if total_income > 0 else 0
        remaining_savings_goal = max(0, target_savings - total_savings) if total_income > 0 else 0
        
        quick_metrics = [
            ("Remaining for Essentials", f"₱{remaining_essentials:,.0f}"),
            ("Remaining for Fun", f"₱{remaining_non_essentials:,.0f}"),
            ("Savings Goal Gap", f"₱{remaining_savings_goal:,.0f}"),
            ("Total Saved This Month", f"₱{total_savings:,.0f}")
        ]
        
        for metric, value in quick_metrics:
            metric_container = ctk.CTkFrame(metrics_frame)
            metric_container.pack(fill="x", pady=5, padx=10)
            
            metric_label = ctk.CTkLabel(metric_container, text=metric, font=("Arial", 11))
            metric_label.pack(side="left", padx=10, pady=8)
            
            value_label = ctk.CTkLabel(metric_container, text=value, font=("Arial", 12, "bold"))
            value_label.pack(side="right", padx=10, pady=8)
        
        # Upcoming bills section with better styling
        if not bills_data.empty:
            upcoming_bills = bills_data[bills_data['Status'] == 'Unpaid'].head(4)
            if not upcoming_bills.empty:
                bills_section = ctk.CTkFrame(summary_frame)
                bills_section.pack(fill="x", padx=15, pady=(20, 10))
                
                bills_label = ctk.CTkLabel(bills_section, text="Upcoming Bills", font=("Arial", 14, "bold"))
                bills_label.pack(anchor="w", padx=15, pady=(15, 10))
                
                for _, bill in upcoming_bills.iterrows():
                    bill_frame = ctk.CTkFrame(bills_section)
                    bill_frame.pack(fill="x", padx=15, pady=2)
                    
                    bill_name = ctk.CTkLabel(bill_frame, text=bill['Bill Name'], font=("Arial", 11))
                    bill_name.pack(side="left", padx=10, pady=8)
                    
                    bill_amount = ctk.CTkLabel(bill_frame, text=f"₱{bill['Amount Due']:,.0f}", 
                                             font=("Arial", 11, "bold"), text_color="#FF9800")
                    bill_amount.pack(side="right", padx=10, pady=8)
    
    def show_income(self):
        """Display income management page"""
        self.clear_content()
        self.current_page = "income"
        self.update_nav_buttons("income")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Income Manager", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Add income form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", pady=10, padx=20)
        
        # Form fields
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(fields_frame, text="Description:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.income_desc_entry = ctk.CTkEntry(fields_frame, width=200)
        self.income_desc_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Amount:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.income_amount_entry = ctk.CTkEntry(fields_frame, width=100)
        self.income_amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Date:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.income_date_entry = DateEntry(fields_frame, width=12, background='darkblue',
                                         foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.income_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Add button
        add_btn = ctk.CTkButton(fields_frame, text="Add Income", command=self.add_income)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Income list
        self.refresh_income_list()
    
    def add_income(self):
        """Add new income entry"""
        try:
            description = self.income_desc_entry.get().strip()
            amount = float(self.income_amount_entry.get())
            date = self.income_date_entry.get()
            
            if not description:
                messagebox.showerror("Error", "Please enter a description")
                return
            
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
            
            # Add to data
            self.data_manager.add_income(description, amount, date)
            
            # Clear form
            self.income_desc_entry.delete(0, 'end')
            self.income_amount_entry.delete(0, 'end')
            self.income_date_entry.set_date(datetime.now().date())
            
            # Refresh list
            self.refresh_income_list()
            
            messagebox.showinfo("Success", "Income added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_income_list(self):
        """Refresh the income list display"""
        # Remove existing list if any
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, 'income_list_frame'):
                widget.destroy()
        
        # Create list frame
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, pady=10, padx=20)
        list_frame.income_list_frame = True
        
        # Headers
        headers = ["Description", "Amount", "Date", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        income_data = self.data_manager.get_income_data()
        for idx, (_, row) in enumerate(income_data.iterrows(), start=1):
            ctk.CTkLabel(list_frame, text=row['Description']).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=f"₱{row['Amount']:,.2f}").grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=str(row['Date'])).grid(row=idx, column=2, padx=10, pady=5, sticky="w")
            
            delete_btn = ctk.CTkButton(
                list_frame, 
                text="Delete", 
                width=80,
                command=lambda i=idx-1: self.delete_income(i)
            )
            delete_btn.grid(row=idx, column=3, padx=10, pady=5)
    
    def delete_income(self, index):
        """Delete income entry"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this income entry?"):
            self.data_manager.delete_income(index)
            self.refresh_income_list()
            messagebox.showinfo("Success", "Income entry deleted successfully!")
    
    def show_essentials(self):
        """Display essentials tracking page"""
        self.clear_content()
        self.current_page = "essentials"
        self.update_nav_buttons("essentials")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Essentials Tracker (50%)", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Calculate 50% allocation
        income_data = self.data_manager.get_income_data()
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        allocation_50 = total_income * 0.5
        
        # Show allocation info
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", pady=10, padx=20)
        
        info_label = ctk.CTkLabel(
            info_frame, 
            text=f"50% Allocation: ₱{allocation_50:,.2f}",
            font=("Arial", 16, "bold")
        )
        info_label.pack(pady=10)
        
        # Add essential form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", pady=10, padx=20)
        
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(fields_frame, text="Category:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.essential_category_entry = ctk.CTkEntry(fields_frame, width=150)
        self.essential_category_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Expected:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.essential_expected_entry = ctk.CTkEntry(fields_frame, width=100)
        self.essential_expected_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Actual:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.essential_actual_entry = ctk.CTkEntry(fields_frame, width=100)
        self.essential_actual_entry.grid(row=0, column=5, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(fields_frame, text="Add Essential", command=self.add_essential)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Essentials list and chart
        self.refresh_essentials_display()
    
    def add_essential(self):
        """Add new essential expense"""
        try:
            category = self.essential_category_entry.get().strip()
            expected = float(self.essential_expected_entry.get())
            actual = float(self.essential_actual_entry.get())
            
            if not category:
                messagebox.showerror("Error", "Please enter a category")
                return
            
            if expected < 0 or actual < 0:
                messagebox.showerror("Error", "Amounts must be non-negative")
                return
            
            self.data_manager.add_essential(category, expected, actual)
            
            # Clear form
            self.essential_category_entry.delete(0, 'end')
            self.essential_expected_entry.delete(0, 'end')
            self.essential_actual_entry.delete(0, 'end')
            
            self.refresh_essentials_display()
            messagebox.showinfo("Success", "Essential expense added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid amounts")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_essentials_display(self):
        """Refresh essentials display with list and chart"""
        # Remove existing display
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, 'essentials_display'):
                widget.destroy()
        
        # Create display container
        display_frame = ctk.CTkFrame(self.content_frame)
        display_frame.pack(fill="both", expand=True, pady=10, padx=20)
        display_frame.essentials_display = True
        
        # Left side - list
        list_frame = ctk.CTkFrame(display_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Headers
        headers = ["Category", "Expected", "Actual", "Difference", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        essentials_data = self.data_manager.get_essentials_data()
        for idx, (_, row) in enumerate(essentials_data.iterrows(), start=1):
            difference = row['Actual'] - row['Expected']
            ctk.CTkLabel(list_frame, text=row['Category']).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=f"₱{row['Expected']:,.2f}").grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=f"₱{row['Actual']:,.2f}").grid(row=idx, column=2, padx=10, pady=5, sticky="w")
            
            diff_color = "red" if difference > 0 else "green"
            diff_label = ctk.CTkLabel(list_frame, text=f"₱{difference:,.2f}", text_color=diff_color)
            diff_label.grid(row=idx, column=3, padx=10, pady=5, sticky="w")
            
            delete_btn = ctk.CTkButton(
                list_frame, 
                text="Delete", 
                width=80,
                command=lambda i=idx-1: self.delete_essential(i)
            )
            delete_btn.grid(row=idx, column=4, padx=10, pady=5)
        
        # Right side - chart
        if not essentials_data.empty:
            chart_frame = ctk.CTkFrame(display_frame)
            chart_frame.pack(side="right", fill="both", expand=True)
            
            chart = self.chart_manager.create_essentials_chart(essentials_data)
            canvas = FigureCanvasTkAgg(chart, chart_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def delete_essential(self, index):
        """Delete essential expense"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this essential expense?"):
            self.data_manager.delete_essential(index)
            self.refresh_essentials_display()
            messagebox.showinfo("Success", "Essential expense deleted successfully!")
    
    def show_bills(self):
        """Display bills management page"""
        self.clear_content()
        self.current_page = "bills"
        self.update_nav_buttons("bills")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Bills Tracker", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Add bill form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", pady=10, padx=20)
        
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(fields_frame, text="Bill Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.bill_name_entry = ctk.CTkEntry(fields_frame, width=150)
        self.bill_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Amount Due:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.bill_amount_entry = ctk.CTkEntry(fields_frame, width=100)
        self.bill_amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Due Date:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.bill_date_entry = DateEntry(fields_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.bill_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(fields_frame, text="Add Bill", command=self.add_bill)
        add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Bills list
        self.refresh_bills_list()
    
    def add_bill(self):
        """Add new bill"""
        try:
            bill_name = self.bill_name_entry.get().strip()
            amount = float(self.bill_amount_entry.get())
            due_date = self.bill_date_entry.get()
            
            if not bill_name:
                messagebox.showerror("Error", "Please enter a bill name")
                return
            
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
            
            self.data_manager.add_bill(bill_name, amount, due_date, "Unpaid")
            
            # Clear form
            self.bill_name_entry.delete(0, 'end')
            self.bill_amount_entry.delete(0, 'end')
            self.bill_date_entry.set_date(datetime.now().date())
            
            self.refresh_bills_list()
            messagebox.showinfo("Success", "Bill added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_bills_list(self):
        """Refresh bills list display"""
        # Remove existing list
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, 'bills_list_frame'):
                widget.destroy()
        
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(fill="both", expand=True, pady=10, padx=20)
        list_frame.bills_list_frame = True
        
        # Headers
        headers = ["Bill Name", "Amount Due", "Due Date", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        bills_data = self.data_manager.get_bills_data()
        today = datetime.now().date()
        
        for idx, (_, row) in enumerate(bills_data.iterrows(), start=1):
            # Check if overdue
            due_date = pd.to_datetime(row['Due Date']).date()
            is_overdue = due_date < today and row['Status'] == 'Unpaid'
            text_color = "red" if is_overdue else None
            
            ctk.CTkLabel(list_frame, text=row['Bill Name'], text_color=text_color).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=f"₱{row['Amount Due']:,.2f}", text_color=text_color).grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=str(row['Due Date']), text_color=text_color).grid(row=idx, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=row['Status'], text_color=text_color).grid(row=idx, column=3, padx=10, pady=5, sticky="w")
            
            # Action buttons
            actions_frame = ctk.CTkFrame(list_frame)
            actions_frame.grid(row=idx, column=4, padx=10, pady=5)
            
            toggle_btn = ctk.CTkButton(
                actions_frame,
                text="Mark Paid" if row['Status'] == 'Unpaid' else "Mark Unpaid",
                width=100,
                command=lambda i=idx-1: self.toggle_bill_status(i)
            )
            toggle_btn.pack(side="left", padx=2)
            
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="Delete",
                width=80,
                command=lambda i=idx-1: self.delete_bill(i)
            )
            delete_btn.pack(side="left", padx=2)
    
    def toggle_bill_status(self, index):
        """Toggle bill payment status"""
        self.data_manager.toggle_bill_status(index)
        self.refresh_bills_list()
    
    def delete_bill(self, index):
        """Delete bill"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this bill?"):
            self.data_manager.delete_bill(index)
            self.refresh_bills_list()
            messagebox.showinfo("Success", "Bill deleted successfully!")
    
    def show_non_essentials(self):
        """Display non-essentials tracking page"""
        self.clear_content()
        self.current_page = "non_essentials"
        self.update_nav_buttons("non_essentials")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Non-Essentials Tracker (30%)", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Calculate 30% allocation
        income_data = self.data_manager.get_income_data()
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        allocation_30 = total_income * 0.3
        
        # Show allocation info
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", pady=10, padx=20)
        
        current_spent = self.data_manager.get_non_essentials_data()['Amount'].sum() if not self.data_manager.get_non_essentials_data().empty else 0
        remaining = allocation_30 - current_spent
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"30% Allocation: ${allocation_30:,.2f} | Spent: ${current_spent:,.2f} | Remaining: ${remaining:,.2f}",
            font=("Arial", 16, "bold")
        )
        info_label.pack(pady=10)
        
        # Add expense form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", pady=10, padx=20)
        
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(fields_frame, text="Expense:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.non_essential_expense_entry = ctk.CTkEntry(fields_frame, width=150)
        self.non_essential_expense_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Amount:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.non_essential_amount_entry = ctk.CTkEntry(fields_frame, width=100)
        self.non_essential_amount_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Date:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.non_essential_date_entry = DateEntry(fields_frame, width=12, background='darkblue',
                                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.non_essential_date_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Notes:").grid(row=0, column=6, sticky="w", padx=5, pady=5)
        self.non_essential_notes_entry = ctk.CTkEntry(fields_frame, width=150)
        self.non_essential_notes_entry.grid(row=0, column=7, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(fields_frame, text="Add Expense", command=self.add_non_essential)
        add_btn.grid(row=0, column=8, padx=10, pady=5)
        
        # Display list and chart
        self.refresh_non_essentials_display()
    
    def add_non_essential(self):
        """Add new non-essential expense"""
        try:
            expense = self.non_essential_expense_entry.get().strip()
            amount = float(self.non_essential_amount_entry.get())
            date = self.non_essential_date_entry.get()
            notes = self.non_essential_notes_entry.get().strip()
            
            if not expense:
                messagebox.showerror("Error", "Please enter an expense description")
                return
            
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
            
            self.data_manager.add_non_essential(expense, amount, date, notes)
            
            # Clear form
            self.non_essential_expense_entry.delete(0, 'end')
            self.non_essential_amount_entry.delete(0, 'end')
            self.non_essential_date_entry.set_date(datetime.now().date())
            self.non_essential_notes_entry.delete(0, 'end')
            
            self.refresh_non_essentials_display()
            messagebox.showinfo("Success", "Non-essential expense added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_non_essentials_display(self):
        """Refresh non-essentials display with list and chart"""
        # Remove existing display
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, 'non_essentials_display'):
                widget.destroy()
        
        display_frame = ctk.CTkFrame(self.content_frame)
        display_frame.pack(fill="both", expand=True, pady=10, padx=20)
        display_frame.non_essentials_display = True
        
        # Left side - list
        list_frame = ctk.CTkFrame(display_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Headers
        headers = ["Expense", "Amount", "Date", "Notes", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        non_essentials_data = self.data_manager.get_non_essentials_data()
        for idx, (_, row) in enumerate(non_essentials_data.iterrows(), start=1):
            ctk.CTkLabel(list_frame, text=row['Expense']).grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=f"₱{row['Amount']:,.2f}").grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=str(row['Date'])).grid(row=idx, column=2, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=row.get('Notes', '')).grid(row=idx, column=3, padx=10, pady=5, sticky="w")
            
            delete_btn = ctk.CTkButton(
                list_frame,
                text="Delete",
                width=80,
                command=lambda i=idx-1: self.delete_non_essential(i)
            )
            delete_btn.grid(row=idx, column=4, padx=10, pady=5)
        
        # Right side - chart
        if not non_essentials_data.empty:
            chart_frame = ctk.CTkFrame(display_frame)
            chart_frame.pack(side="right", fill="both", expand=True)
            
            chart = self.chart_manager.create_non_essentials_chart(non_essentials_data)
            canvas = FigureCanvasTkAgg(chart, chart_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def delete_non_essential(self, index):
        """Delete non-essential expense"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            self.data_manager.delete_non_essentials(index)
            self.refresh_non_essentials_display()
            messagebox.showinfo("Success", "Expense deleted successfully!")
    
    def show_savings(self):
        """Display savings tracking page"""
        self.clear_content()
        self.current_page = "savings"
        self.update_nav_buttons("savings")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Savings Tracker (20%)", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Calculate 20% target
        income_data = self.data_manager.get_income_data()
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        target_savings = total_income * 0.2
        
        # Show savings info
        savings_data = self.data_manager.get_savings_data()
        current_savings = savings_data['Deposit'].sum() if not savings_data.empty else 0
        progress = (current_savings / target_savings * 100) if target_savings > 0 else 0
        
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", pady=10, padx=20)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"Target (20%): ${target_savings:,.2f} | Current: ${current_savings:,.2f} | Progress: {progress:.1f}%",
            font=("Arial", 16, "bold")
        )
        info_label.pack(pady=10)
        
        # Add savings form
        form_frame = ctk.CTkFrame(self.content_frame)
        form_frame.pack(fill="x", pady=10, padx=20)
        
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(fields_frame, text="Deposit Amount:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.savings_deposit_entry = ctk.CTkEntry(fields_frame, width=150)
        self.savings_deposit_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(fields_frame, text="Date:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.savings_date_entry = DateEntry(fields_frame, width=12, background='darkblue',
                                          foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.savings_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        add_btn = ctk.CTkButton(fields_frame, text="Add Deposit", command=self.add_savings)
        add_btn.grid(row=0, column=4, padx=10, pady=5)
        
        # Display list and chart
        self.refresh_savings_display()
    
    def add_savings(self):
        """Add new savings deposit"""
        try:
            deposit = float(self.savings_deposit_entry.get())
            date = self.savings_date_entry.get()
            
            if deposit <= 0:
                messagebox.showerror("Error", "Deposit amount must be greater than 0")
                return
            
            self.data_manager.add_savings(deposit, date)
            
            # Clear form
            self.savings_deposit_entry.delete(0, 'end')
            self.savings_date_entry.set_date(datetime.now().date())
            
            self.refresh_savings_display()
            messagebox.showinfo("Success", "Savings deposit added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid deposit amount")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def refresh_savings_display(self):
        """Refresh savings display with list and chart"""
        # Remove existing display
        for widget in self.content_frame.winfo_children():
            if hasattr(widget, 'savings_display'):
                widget.destroy()
        
        display_frame = ctk.CTkFrame(self.content_frame)
        display_frame.pack(fill="both", expand=True, pady=10, padx=20)
        display_frame.savings_display = True
        
        # Left side - list
        list_frame = ctk.CTkFrame(display_frame)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Headers
        headers = ["Deposit Amount", "Date", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(list_frame, text=header, font=("Arial", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Data rows
        savings_data = self.data_manager.get_savings_data()
        for idx, (_, row) in enumerate(savings_data.iterrows(), start=1):
            ctk.CTkLabel(list_frame, text=f"₱{row['Deposit']:,.2f}").grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(list_frame, text=str(row['Date'])).grid(row=idx, column=1, padx=10, pady=5, sticky="w")
            
            delete_btn = ctk.CTkButton(
                list_frame,
                text="Delete",
                width=80,
                command=lambda i=idx-1: self.delete_savings(i)
            )
            delete_btn.grid(row=idx, column=2, padx=10, pady=5)
        
        # Right side - chart
        if not savings_data.empty:
            chart_frame = ctk.CTkFrame(display_frame)
            chart_frame.pack(side="right", fill="both", expand=True)
            
            chart = self.chart_manager.create_savings_chart(savings_data)
            canvas = FigureCanvasTkAgg(chart, chart_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def delete_savings(self, index):
        """Delete savings deposit"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this savings deposit?"):
            self.data_manager.delete_savings(index)
            self.refresh_savings_display()
            messagebox.showinfo("Success", "Savings deposit deleted successfully!")
    
    def show_calendar(self):
        """Display calendar view"""
        self.clear_content()
        self.current_page = "calendar"
        self.update_nav_buttons("calendar")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Calendar View", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Calendar container
        cal_frame = ctk.CTkFrame(self.content_frame)
        cal_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        # Create calendar
        self.calendar = Calendar(
            cal_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            font=('Arial', 12),
            cursor="hand2"
        )
        self.calendar.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        # Legend and events panel
        info_panel = ctk.CTkFrame(cal_frame)
        info_panel.pack(side="right", fill="y", padx=20, pady=20)
        
        # Legend
        legend_label = ctk.CTkLabel(info_panel, text="Legend:", font=("Arial", 16, "bold"))
        legend_label.pack(pady=(10, 5))
        
        legends = [
            ("Income", "#4CAF50"),
            ("Bills Due", "#F44336"),
            ("Savings", "#9C27B0"),
            ("Non-Essentials", "#2196F3")
        ]
        
        for text, color in legends:
            legend_item = ctk.CTkFrame(info_panel)
            legend_item.pack(fill="x", pady=2, padx=10)
            
            color_box = ctk.CTkLabel(legend_item, text="■", text_color=color, font=("Arial", 16))
            color_box.pack(side="left", padx=5)
            
            text_label = ctk.CTkLabel(legend_item, text=text)
            text_label.pack(side="left")
        
        # Highlight calendar dates
        self.highlight_calendar_dates()
        
        # Selected date events
        events_label = ctk.CTkLabel(info_panel, text="Selected Date Events:", font=("Arial", 16, "bold"))
        events_label.pack(pady=(20, 10))
        
        self.events_display = ctk.CTkTextbox(info_panel, height=200)
        self.events_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind calendar selection
        self.calendar.bind("<<CalendarSelected>>", self.show_date_events)
    
    def highlight_calendar_dates(self):
        """Highlight important dates on calendar"""
        # Get all data
        income_data = self.data_manager.get_income_data()
        bills_data = self.data_manager.get_bills_data()
        savings_data = self.data_manager.get_savings_data()
        non_essentials_data = self.data_manager.get_non_essentials_data()
        
        # Highlight income dates (green)
        if not income_data.empty:
            for _, row in income_data.iterrows():
                try:
                    date = pd.to_datetime(row['Date']).date()
                    self.calendar.calevent_create(date, "Income", "income")
                except:
                    pass
        
        # Highlight bill due dates (red)
        if not bills_data.empty:
            for _, row in bills_data.iterrows():
                try:
                    date = pd.to_datetime(row['Due Date']).date()
                    self.calendar.calevent_create(date, f"Bill: {row['Bill Name']}", "bills")
                except:
                    pass
        
        # Highlight savings dates (purple)
        if not savings_data.empty:
            for _, row in savings_data.iterrows():
                try:
                    date = pd.to_datetime(row['Date']).date()
                    self.calendar.calevent_create(date, "Savings", "savings")
                except:
                    pass
        
        # Highlight non-essential expenses (blue)
        if not non_essentials_data.empty:
            for _, row in non_essentials_data.iterrows():
                try:
                    date = pd.to_datetime(row['Date']).date()
                    self.calendar.calevent_create(date, f"Expense: {row['Expense']}", "expenses")
                except:
                    pass
        
        # Configure event tags
        self.calendar.tag_config("income", background="#4CAF50", foreground="white")
        self.calendar.tag_config("bills", background="#F44336", foreground="white")
        self.calendar.tag_config("savings", background="#9C27B0", foreground="white")
        self.calendar.tag_config("expenses", background="#2196F3", foreground="white")
    
    def show_date_events(self, event=None):
        """Show events for selected date"""
        selected_date = self.calendar.selection_get()
        
        # Clear previous events
        self.events_display.delete("1.0", "end")
        
        # Find events for selected date
        events = []
        
        # Check income
        income_data = self.data_manager.get_income_data()
        if not income_data.empty:
            day_income = income_data[pd.to_datetime(income_data['Date']).dt.date == selected_date]
            for _, row in day_income.iterrows():
                events.append(f"Income: {row['Description']} - ${row['Amount']:,.2f}")
        
        # Check bills
        bills_data = self.data_manager.get_bills_data()
        if not bills_data.empty:
            day_bills = bills_data[pd.to_datetime(bills_data['Due Date']).dt.date == selected_date]
            for _, row in day_bills.iterrows():
                events.append(f"Bill Due: {row['Bill Name']} - ₱{row['Amount Due']:,.2f} ({row['Status']})")
        
        # Check savings
        savings_data = self.data_manager.get_savings_data()
        if not savings_data.empty:
            day_savings = savings_data[pd.to_datetime(savings_data['Date']).dt.date == selected_date]
            for _, row in day_savings.iterrows():
                events.append(f"Savings Deposit: ₱{row['Deposit']:,.2f}")
        
        # Check non-essentials
        non_essentials_data = self.data_manager.get_non_essentials_data()
        if not non_essentials_data.empty:
            day_expenses = non_essentials_data[pd.to_datetime(non_essentials_data['Date']).dt.date == selected_date]
            for _, row in day_expenses.iterrows():
                events.append(f"Expense: {row['Expense']} - ₱{row['Amount']:,.2f}")
        
        # Display events
        if events:
            self.events_display.insert("1.0", f"Events for {selected_date}:\n\n" + "\n".join(events))
        else:
            self.events_display.insert("1.0", f"No events for {selected_date}")
    
    def show_analytics(self):
        """Display comprehensive analytics page"""
        self.clear_content()
        self.current_page = "analytics"
        self.update_nav_buttons("analytics")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Financial Analytics", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Create scrollable content
        analytics_container = ctk.CTkScrollableFrame(self.content_frame)
        analytics_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get data for analytics
        income_data = self.data_manager.get_income_data()
        essentials_data = self.data_manager.get_essentials_data()
        bills_data = self.data_manager.get_bills_data()
        non_essentials_data = self.data_manager.get_non_essentials_data()
        savings_data = self.data_manager.get_savings_data()
        
        # Calculate key metrics
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        total_essentials = essentials_data['Actual'].sum() if not essentials_data.empty else 0
        total_non_essentials = non_essentials_data['Amount'].sum() if not non_essentials_data.empty else 0
        total_savings = savings_data['Deposit'].sum() if not savings_data.empty else 0
        total_expenses = total_essentials + total_non_essentials
        
        # Budget adherence metrics
        target_essentials = total_income * 0.5
        target_non_essentials = total_income * 0.3
        target_savings = total_income * 0.2
        
        # Key Performance Indicators
        kpi_frame = ctk.CTkFrame(analytics_container)
        kpi_frame.pack(fill="x", pady=10)
        
        kpi_title = ctk.CTkLabel(kpi_frame, text="Key Performance Indicators", font=("Arial", 18, "bold"))
        kpi_title.pack(pady=10)
        
        # KPI Cards
        kpi_cards_frame = ctk.CTkFrame(kpi_frame)
        kpi_cards_frame.pack(fill="x", pady=10, padx=20)
        
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        expense_ratio = (total_expenses / total_income * 100) if total_income > 0 else 0
        budget_variance = abs((total_essentials + total_non_essentials + total_savings) - total_income)
        
        kpi_stats = [
            ("Savings Rate", f"{savings_rate:.1f}%", "#4CAF50" if savings_rate >= 20 else "#FF9800"),
            ("Expense Ratio", f"{expense_ratio:.1f}%", "#2196F3"),
            ("Budget Variance", f"₱{budget_variance:,.2f}", "#F44336" if budget_variance > total_income * 0.1 else "#4CAF50"),
            ("Emergency Fund", f"₱{total_savings * 6:,.2f}", "#9C27B0")
        ]
        
        for i, (label, value, color) in enumerate(kpi_stats):
            card = self.ui_components.create_stats_card(kpi_cards_frame, label, value, color)
            card.grid(row=0, column=i, padx=15, pady=10, sticky="ew")
        
        kpi_cards_frame.grid_columnconfigure(tuple(range(4)), weight=1)
        
        # Budget Adherence Analysis
        adherence_frame = ctk.CTkFrame(analytics_container)
        adherence_frame.pack(fill="x", pady=20)
        
        adherence_title = ctk.CTkLabel(adherence_frame, text="Budget Adherence Analysis", font=("Arial", 18, "bold"))
        adherence_title.pack(pady=10)
        
        adherence_content = ctk.CTkFrame(adherence_frame)
        adherence_content.pack(fill="both", expand=True, pady=10, padx=20)
        
        # Progress bars for each category
        categories = [
            ("Essentials (50%)", total_essentials, target_essentials, "#FF9800"),
            ("Non-Essentials (30%)", total_non_essentials, target_non_essentials, "#2196F3"),
            ("Savings (20%)", total_savings, target_savings, "#9C27B0")
        ]
        
        for i, (category, actual, target, color) in enumerate(categories):
            cat_frame = ctk.CTkFrame(adherence_content)
            cat_frame.grid(row=i, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
            adherence_content.grid_columnconfigure(0, weight=1)
            
            cat_label = ctk.CTkLabel(cat_frame, text=category, font=("Arial", 14, "bold"))
            cat_label.pack(anchor="w", padx=20, pady=(10, 5))
            
            progress_frame = ctk.CTkFrame(cat_frame)
            progress_frame.pack(fill="x", padx=20, pady=(0, 5))
            
            actual_label = ctk.CTkLabel(progress_frame, text=f"Actual: ₱{actual:,.2f}")
            actual_label.pack(side="left")
            
            target_label = ctk.CTkLabel(progress_frame, text=f"Target: ₱{target:,.2f}")
            target_label.pack(side="right")
            
            progress_value = (actual / target) if target > 0 else 0
            progress_bar = self.ui_components.create_progress_bar(cat_frame, actual, target, color)
            progress_bar.pack(fill="x", padx=20, pady=(0, 10))
            
            # Variance indicator
            variance = ((actual - target) / target * 100) if target > 0 else 0
            variance_color = "#4CAF50" if abs(variance) <= 10 else "#FF9800" if abs(variance) <= 20 else "#F44336"
            variance_text = f"{'Over' if variance > 0 else 'Under'} by {abs(variance):.1f}%"
            variance_label = ctk.CTkLabel(cat_frame, text=variance_text, text_color=variance_color)
            variance_label.pack(pady=(0, 10))
        
        # Charts Section with proper scrolling support
        charts_frame = ctk.CTkFrame(analytics_container)
        charts_frame.pack(fill="x", pady=20)
        
        charts_title = ctk.CTkLabel(charts_frame, text="Financial Trends", font=("Arial", 18, "bold"))
        charts_title.pack(pady=10)
        
        # Create chart views with fixed heights to prevent cutoff
        chart_container = ctk.CTkFrame(charts_frame, height=400)
        chart_container.pack(fill="x", padx=20, pady=10)
        chart_container.pack_propagate(False)
        
        # Budget progress chart
        if total_income > 0:
            budget_chart_frame = ctk.CTkFrame(chart_container)
            budget_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            budget_chart = self.chart_manager.create_budget_progress_chart(
                total_income, total_essentials, total_non_essentials, total_savings
            )
            canvas = FigureCanvasTkAgg(budget_chart, budget_chart_frame)
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Monthly summary chart if there's data
        if not all(df.empty for df in [income_data, essentials_data, non_essentials_data, savings_data]):
            monthly_chart_frame = ctk.CTkFrame(chart_container)
            monthly_chart_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            
            monthly_chart = self.chart_manager.create_monthly_summary_chart(
                income_data, essentials_data, non_essentials_data, savings_data
            )
            canvas2 = FigureCanvasTkAgg(monthly_chart, monthly_chart_frame)
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Financial Health Score
        health_frame = ctk.CTkFrame(analytics_container)
        health_frame.pack(fill="x", pady=20)
        
        health_title = ctk.CTkLabel(health_frame, text="Financial Health Score", font=("Arial", 18, "bold"))
        health_title.pack(pady=10)
        
        # Calculate health score
        score_components = {
            "Savings Rate": min(savings_rate / 20 * 25, 25),  # Max 25 points
            "Budget Adherence": max(0, 25 - abs(variance) / 10 * 25),  # Max 25 points  
            "Emergency Fund": min(total_savings / (total_expenses * 3) * 25, 25) if total_expenses > 0 else 0,  # Max 25 points
            "Expense Control": max(0, 25 - (expense_ratio - 80) / 20 * 25) if expense_ratio > 80 else 25  # Max 25 points
        }
        
        total_score = sum(score_components.values())
        
        score_frame = ctk.CTkFrame(health_frame)
        score_frame.pack(pady=10, padx=20)
        
        score_label = ctk.CTkLabel(score_frame, text=f"Overall Score: {total_score:.0f}/100", 
                                  font=("Arial", 20, "bold"))
        score_label.pack(pady=10)
        
        # Score interpretation
        if total_score >= 80:
            interpretation = "Excellent financial health!"
            color = "#4CAF50"
        elif total_score >= 60:
            interpretation = "Good financial management"
            color = "#FF9800"
        elif total_score >= 40:
            interpretation = "Needs improvement"
            color = "#FF5722"
        else:
            interpretation = "Critical - Review budget immediately"
            color = "#F44336"
        
        interpretation_label = ctk.CTkLabel(score_frame, text=interpretation, 
                                          font=("Arial", 16), text_color=color)
        interpretation_label.pack(pady=(0, 10))
        
        # Recommendations
        recommendations_frame = ctk.CTkFrame(analytics_container)
        recommendations_frame.pack(fill="x", pady=20)
        
        rec_title = ctk.CTkLabel(recommendations_frame, text="Smart Recommendations", font=("Arial", 18, "bold"))
        rec_title.pack(pady=10)
        
        recommendations = []
        if savings_rate < 20:
            recommendations.append("• Increase your savings rate to reach the 20% target")
        if total_essentials > target_essentials:
            recommendations.append("• Review essential expenses - you're over the 50% target")
        if total_non_essentials > target_non_essentials:
            recommendations.append("• Reduce non-essential spending to stay within 30% budget")
        if len(bills_data[bills_data['Status'] == 'Unpaid']) > 0:
            recommendations.append("• Pay outstanding bills to avoid late fees")
        if total_savings < total_expenses * 3:
            recommendations.append("• Build emergency fund to cover 3-6 months of expenses")
        
        if not recommendations:
            recommendations.append("• Great job! Your budget is well-balanced")
        
        rec_content = ctk.CTkTextbox(recommendations_frame, height=150)
        rec_content.pack(fill="x", padx=20, pady=(0, 20))
        rec_content.insert("1.0", "\n".join(recommendations))
        rec_content.configure(state="disabled")

    def show_settings(self):
        """Display settings page"""
        self.clear_content()
        self.current_page = "settings"
        self.update_nav_buttons("settings")
        
        # Page title
        title = ctk.CTkLabel(self.content_frame, text="Settings", font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        # Settings container
        settings_container = ctk.CTkScrollableFrame(self.content_frame)
        settings_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(settings_container)
        theme_frame.pack(fill="x", pady=10)
        
        theme_title = ctk.CTkLabel(theme_frame, text="Theme Settings", font=("Arial", 16, "bold"))
        theme_title.pack(pady=10)
        
        current_theme = self.settings.get('theme', 'dark')
        self.theme_var = ctk.StringVar(value=current_theme)
        
        theme_options = ctk.CTkFrame(theme_frame)
        theme_options.pack(pady=10)
        
        dark_radio = ctk.CTkRadioButton(theme_options, text="Dark Mode", variable=self.theme_var, value="dark")
        dark_radio.pack(side="left", padx=20)
        
        light_radio = ctk.CTkRadioButton(theme_options, text="Light Mode", variable=self.theme_var, value="light")
        light_radio.pack(side="left", padx=20)
        
        apply_theme_btn = ctk.CTkButton(theme_frame, text="Apply Theme", command=self.apply_theme_change)
        apply_theme_btn.pack(pady=10)
        
        # Data management
        data_frame = ctk.CTkFrame(settings_container)
        data_frame.pack(fill="x", pady=20)
        
        data_title = ctk.CTkLabel(data_frame, text="Data Management", font=("Arial", 16, "bold"))
        data_title.pack(pady=10)
        
        data_buttons = ctk.CTkFrame(data_frame)
        data_buttons.pack(pady=10)
        
        backup_btn = ctk.CTkButton(data_buttons, text="Backup Data", command=self.backup_data)
        backup_btn.pack(side="left", padx=10)
        
        restore_btn = ctk.CTkButton(data_buttons, text="Restore Data", command=self.restore_data)
        restore_btn.pack(side="left", padx=10)
        
        export_btn = ctk.CTkButton(data_buttons, text="Export Report", command=self.export_report)
        export_btn.pack(side="left", padx=10)
        
        reset_btn = ctk.CTkButton(data_buttons, text="Reset All Data", command=self.reset_data)
        reset_btn.pack(side="left", padx=10)
    
    def apply_theme_change(self):
        """Apply theme change"""
        new_theme = self.theme_var.get()
        self.settings['theme'] = new_theme
        self.settings_manager.save_settings(self.settings)
        self.apply_theme()
        messagebox.showinfo("Success", "Theme updated successfully!")
    
    def backup_data(self):
        """Backup all data files"""
        backup_dir = filedialog.askdirectory(title="Select Backup Directory")
        if backup_dir:
            try:
                import shutil
                data_dir = "data"
                backup_name = f"budget_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                backup_path = os.path.join(backup_dir, backup_name)
                shutil.copytree(data_dir, backup_path)
                messagebox.showinfo("Success", f"Data backed up to: {backup_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_data(self):
        """Restore data from backup"""
        backup_dir = filedialog.askdirectory(title="Select Backup Directory to Restore")
        if backup_dir:
            if messagebox.askyesno("Confirm", "This will overwrite all current data. Continue?"):
                try:
                    import shutil
                    data_dir = "data"
                    if os.path.exists(data_dir):
                        shutil.rmtree(data_dir)
                    shutil.copytree(backup_dir, data_dir)
                    self.data_manager = DataManager()  # Reload data manager
                    messagebox.showinfo("Success", "Data restored successfully!")
                    self.show_dashboard()  # Refresh display
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def export_report(self):
        """Export comprehensive report"""
        file_path = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.export_excel_report(file_path)
                else:
                    self.export_pdf_report(file_path)
                messagebox.showinfo("Success", f"Report exported to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_excel_report(self, file_path):
        """Export Excel report"""
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Export all data to separate sheets
            self.data_manager.get_income_data().to_excel(writer, sheet_name='Income', index=False)
            self.data_manager.get_essentials_data().to_excel(writer, sheet_name='Essentials', index=False)
            self.data_manager.get_bills_data().to_excel(writer, sheet_name='Bills', index=False)
            self.data_manager.get_non_essentials_data().to_excel(writer, sheet_name='Non-Essentials', index=False)
            self.data_manager.get_savings_data().to_excel(writer, sheet_name='Savings', index=False)
            
            # Summary sheet
            summary_data = {
                'Category': ['Total Income', 'Essentials', 'Non-Essentials', 'Savings'],
                'Amount': [
                    self.data_manager.get_income_data()['Amount'].sum() if not self.data_manager.get_income_data().empty else 0,
                    self.data_manager.get_essentials_data()['Actual'].sum() if not self.data_manager.get_essentials_data().empty else 0,
                    self.data_manager.get_non_essentials_data()['Amount'].sum() if not self.data_manager.get_non_essentials_data().empty else 0,
                    self.data_manager.get_savings_data()['Deposit'].sum() if not self.data_manager.get_savings_data().empty else 0
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
    
    def export_pdf_report(self, file_path):
        """Export PDF report (simplified version)"""
        # This would require additional PDF libraries like reportlab
        # For now, we'll create a simple text report
        with open(file_path.replace('.pdf', '.txt'), 'w') as f:
            f.write("Budget Tracker Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary
            income_total = self.data_manager.get_income_data()['Amount'].sum() if not self.data_manager.get_income_data().empty else 0
            essentials_total = self.data_manager.get_essentials_data()['Actual'].sum() if not self.data_manager.get_essentials_data().empty else 0
            non_essentials_total = self.data_manager.get_non_essentials_data()['Amount'].sum() if not self.data_manager.get_non_essentials_data().empty else 0
            savings_total = self.data_manager.get_savings_data()['Deposit'].sum() if not self.data_manager.get_savings_data().empty else 0
            
            f.write(f"Total Income: ${income_total:,.2f}\n")
            f.write(f"Essentials (50%): ${essentials_total:,.2f}\n")
            f.write(f"Non-Essentials (30%): ${non_essentials_total:,.2f}\n")
            f.write(f"Savings (20%): ${savings_total:,.2f}\n\n")
            
            f.write("Budget Allocation vs Actual:\n")
            f.write(f"Essentials Target: ${income_total * 0.5:,.2f} | Actual: ${essentials_total:,.2f}\n")
            f.write(f"Non-Essentials Target: ${income_total * 0.3:,.2f} | Actual: ${non_essentials_total:,.2f}\n")
            f.write(f"Savings Target: ${income_total * 0.2:,.2f} | Actual: ${savings_total:,.2f}\n")
    
    def reset_data(self):
        """Reset all application data"""
        if messagebox.askyesno("Confirm Reset", "This will delete ALL data permanently. Are you sure?"):
            if messagebox.askyesno("Final Confirmation", "This action cannot be undone. Continue?"):
                try:
                    self.data_manager.reset_all_data()
                    messagebox.showinfo("Success", "All data has been reset successfully!")
                    self.show_dashboard()  # Refresh display
                except Exception as e:
                    messagebox.showerror("Error", f"Reset failed: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askyesno("Quit", "Do you want to quit the application?"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = BudgetTrackerApp()
        app.run()
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
