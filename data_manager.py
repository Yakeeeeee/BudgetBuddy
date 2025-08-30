"""
Data Manager for Budget Tracker
Handles all CSV data operations using Pandas
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Optional, List, Dict


class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
        self.initialize_csv_files()
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_csv_files(self):
        """Initialize CSV files with headers if they don't exist"""
        files_structure = {
            "income.csv": ["Description", "Amount", "Date"],
            "essentials.csv": ["Category", "Expected", "Actual"],
            "bills.csv": ["Bill Name", "Amount Due", "Due Date", "Status"],
            "non_essentials.csv": ["Expense", "Amount", "Date", "Notes"],
            "savings.csv": ["Deposit", "Date"],
            "settings.csv": ["Key", "Value"]
        }
        
        for filename, columns in files_structure.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                df = pd.DataFrame(columns=columns)
                df.to_csv(filepath, index=False)
    
    def get_file_path(self, filename: str) -> str:
        """Get full file path for CSV file"""
        return os.path.join(self.data_dir, filename)
    
    # Income Management
    def get_income_data(self) -> pd.DataFrame:
        """Load income data from CSV"""
        try:
            df = pd.read_csv(self.get_file_path("income.csv"))
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df = df.sort_values('Date', ascending=False)
            return df
        except Exception as e:
            print(f"Error loading income data: {e}")
            return pd.DataFrame(columns=["Description", "Amount", "Date"])
    
    def add_income(self, description: str, amount: float, date) -> None:
        """Add new income entry"""
        try:
            df = self.get_income_data()
            new_row = {
                "Description": description,
                "Amount": amount,
                "Date": pd.to_datetime(date).date()
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.get_file_path("income.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error adding income: {e}")
    
    def delete_income(self, index: int) -> None:
        """Delete income entry by index"""
        try:
            df = self.get_income_data()
            if 0 <= index < len(df):
                df = df.drop(df.index[index])
                df.to_csv(self.get_file_path("income.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error deleting income: {e}")
    
    # Essentials Management
    def get_essentials_data(self) -> pd.DataFrame:
        """Load essentials data from CSV"""
        try:
            df = pd.read_csv(self.get_file_path("essentials.csv"))
            return df
        except Exception as e:
            print(f"Error loading essentials data: {e}")
            return pd.DataFrame(columns=["Category", "Expected", "Actual"])
    
    def add_essential(self, category: str, expected: float, actual: float) -> None:
        """Add new essential expense"""
        try:
            df = self.get_essentials_data()
            new_row = {
                "Category": category,
                "Expected": expected,
                "Actual": actual
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.get_file_path("essentials.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error adding essential: {e}")
    
    def delete_essential(self, index: int) -> None:
        """Delete essential expense by index"""
        try:
            df = self.get_essentials_data()
            if 0 <= index < len(df):
                df = df.drop(df.index[index])
                df.to_csv(self.get_file_path("essentials.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error deleting essential: {e}")
    
    # Bills Management
    def get_bills_data(self) -> pd.DataFrame:
        """Load bills data from CSV"""
        try:
            df = pd.read_csv(self.get_file_path("bills.csv"))
            if not df.empty:
                df['Due Date'] = pd.to_datetime(df['Due Date']).dt.date
                df = df.sort_values('Due Date')
            return df
        except Exception as e:
            print(f"Error loading bills data: {e}")
            return pd.DataFrame(columns=["Bill Name", "Amount Due", "Due Date", "Status"])
    
    def add_bill(self, bill_name: str, amount_due: float, due_date, status: str = "Unpaid") -> None:
        """Add new bill"""
        try:
            df = self.get_bills_data()
            new_row = {
                "Bill Name": bill_name,
                "Amount Due": amount_due,
                "Due Date": pd.to_datetime(due_date).date(),
                "Status": status
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.get_file_path("bills.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error adding bill: {e}")
    
    def toggle_bill_status(self, index: int) -> None:
        """Toggle bill payment status"""
        try:
            df = self.get_bills_data()
            if 0 <= index < len(df):
                current_status = df.iloc[index]['Status']
                new_status = "Paid" if current_status == "Unpaid" else "Unpaid"
                df.iloc[index, df.columns.get_loc('Status')] = new_status
                df.to_csv(self.get_file_path("bills.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error toggling bill status: {e}")
    
    def delete_bill(self, index: int) -> None:
        """Delete bill by index"""
        try:
            df = self.get_bills_data()
            if 0 <= index < len(df):
                df = df.drop(df.index[index])
                df.to_csv(self.get_file_path("bills.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error deleting bill: {e}")
    
    # Non-Essentials Management
    def get_non_essentials_data(self) -> pd.DataFrame:
        """Load non-essentials data from CSV"""
        try:
            df = pd.read_csv(self.get_file_path("non_essentials.csv"))
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df = df.sort_values('Date', ascending=False)
            return df
        except Exception as e:
            print(f"Error loading non-essentials data: {e}")
            return pd.DataFrame(columns=["Expense", "Amount", "Date", "Notes"])
    
    def add_non_essential(self, expense: str, amount: float, date, notes: str = "") -> None:
        """Add new non-essential expense"""
        try:
            df = self.get_non_essentials_data()
            new_row = {
                "Expense": expense,
                "Amount": amount,
                "Date": pd.to_datetime(date).date(),
                "Notes": notes
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.get_file_path("non_essentials.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error adding non-essential: {e}")
    
    def delete_non_essential(self, index: int) -> None:
        """Delete non-essential expense by index"""
        try:
            df = self.get_non_essentials_data()
            if 0 <= index < len(df):
                df = df.drop(df.index[index])
                df.to_csv(self.get_file_path("non_essentials.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error deleting non-essential: {e}")
    
    # Savings Management
    def get_savings_data(self) -> pd.DataFrame:
        """Load savings data from CSV"""
        try:
            df = pd.read_csv(self.get_file_path("savings.csv"))
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df = df.sort_values('Date', ascending=False)
            return df
        except Exception as e:
            print(f"Error loading savings data: {e}")
            return pd.DataFrame(columns=["Deposit", "Date"])
    
    def add_savings(self, deposit: float, date) -> None:
        """Add new savings deposit"""
        try:
            df = self.get_savings_data()
            new_row = {
                "Deposit": deposit,
                "Date": pd.to_datetime(date).date()
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.get_file_path("savings.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error adding savings: {e}")
    
    def delete_savings(self, index: int) -> None:
        """Delete savings deposit by index"""
        try:
            df = self.get_savings_data()
            if 0 <= index < len(df):
                df = df.drop(df.index[index])
                df.to_csv(self.get_file_path("savings.csv"), index=False)
        except Exception as e:
            raise Exception(f"Error deleting savings: {e}")
    
    # Budget Calculations
    def calculate_budget_allocations(self) -> Dict[str, float]:
        """Calculate 50/30/20 budget allocations"""
        income_data = self.get_income_data()
        total_income = income_data['Amount'].sum() if not income_data.empty else 0
        
        return {
            'total_income': total_income,
            'essentials_target': total_income * 0.5,
            'non_essentials_target': total_income * 0.3,
            'savings_target': total_income * 0.2
        }
    
    def calculate_actual_spending(self) -> Dict[str, float]:
        """Calculate actual spending in each category"""
        essentials_data = self.get_essentials_data()
        non_essentials_data = self.get_non_essentials_data()
        savings_data = self.get_savings_data()
        
        return {
            'essentials_actual': essentials_data['Actual'].sum() if not essentials_data.empty else 0,
            'non_essentials_actual': non_essentials_data['Amount'].sum() if not non_essentials_data.empty else 0,
            'savings_actual': savings_data['Deposit'].sum() if not savings_data.empty else 0
        }
    
    def get_budget_summary(self) -> Dict[str, Dict[str, float]]:
        """Get comprehensive budget summary"""
        allocations = self.calculate_budget_allocations()
        actuals = self.calculate_actual_spending()
        
        return {
            'essentials': {
                'target': allocations['essentials_target'],
                'actual': actuals['essentials_actual'],
                'difference': actuals['essentials_actual'] - allocations['essentials_target'],
                'percentage': (actuals['essentials_actual'] / allocations['total_income'] * 100) if allocations['total_income'] > 0 else 0
            },
            'non_essentials': {
                'target': allocations['non_essentials_target'],
                'actual': actuals['non_essentials_actual'],
                'difference': actuals['non_essentials_actual'] - allocations['non_essentials_target'],
                'percentage': (actuals['non_essentials_actual'] / allocations['total_income'] * 100) if allocations['total_income'] > 0 else 0
            },
            'savings': {
                'target': allocations['savings_target'],
                'actual': actuals['savings_actual'],
                'difference': actuals['savings_actual'] - allocations['savings_target'],
                'percentage': (actuals['savings_actual'] / allocations['total_income'] * 100) if allocations['total_income'] > 0 else 0
            },
            'total_income': allocations['total_income']
        }
    
    # Data Analytics
    def get_spending_trends(self, days: int = 30) -> Dict[str, pd.DataFrame]:
        """Get spending trends for the last N days"""
        end_date = datetime.now().date()
        start_date = end_date - pd.Timedelta(days=days)
        
        trends = {}
        
        # Non-essentials trend
        non_essentials = self.get_non_essentials_data()
        if not non_essentials.empty:
            non_essentials['Date'] = pd.to_datetime(non_essentials['Date'])
            recent_non_essentials = non_essentials[
                (non_essentials['Date'] >= pd.Timestamp(start_date)) &
                (non_essentials['Date'] <= pd.Timestamp(end_date))
            ]
            trends['non_essentials'] = recent_non_essentials.groupby('Date')['Amount'].sum().reset_index()
        
        # Income trend
        income = self.get_income_data()
        if not income.empty:
            income['Date'] = pd.to_datetime(income['Date'])
            recent_income = income[
                (income['Date'] >= pd.Timestamp(start_date)) &
                (income['Date'] <= pd.Timestamp(end_date))
            ]
            trends['income'] = recent_income.groupby('Date')['Amount'].sum().reset_index()
        
        # Savings trend
        savings = self.get_savings_data()
        if not savings.empty:
            savings['Date'] = pd.to_datetime(savings['Date'])
            recent_savings = savings[
                (savings['Date'] >= pd.Timestamp(start_date)) &
                (savings['Date'] <= pd.Timestamp(end_date))
            ]
            savings_cumulative = recent_savings.copy()
            savings_cumulative['Cumulative'] = savings_cumulative['Deposit'].cumsum()
            trends['savings'] = savings_cumulative
        
        return trends
    
    def get_overdue_bills(self) -> pd.DataFrame:
        """Get list of overdue bills"""
        bills = self.get_bills_data()
        if bills.empty:
            return pd.DataFrame()
        
        today = datetime.now().date()
        overdue = bills[
            (bills['Status'] == 'Unpaid') &
            (pd.to_datetime(bills['Due Date']).dt.date < today)
        ]
        
        return overdue.sort_values('Due Date')
    
    def get_upcoming_bills(self, days: int = 7) -> pd.DataFrame:
        """Get bills due in the next N days"""
        bills = self.get_bills_data()
        if bills.empty:
            return pd.DataFrame()
        
        today = datetime.now().date()
        future_date = today + pd.Timedelta(days=days)
        
        upcoming = bills[
            (bills['Status'] == 'Unpaid') &
            (pd.to_datetime(bills['Due Date']).dt.date >= today) &
            (pd.to_datetime(bills['Due Date']).dt.date <= future_date)
        ]
        
        return upcoming.sort_values('Due Date')
    
    # Data Management
    def reset_all_data(self) -> None:
        """Reset all CSV files to empty state"""
        try:
            files_structure = {
                "income.csv": ["Description", "Amount", "Date"],
                "essentials.csv": ["Category", "Expected", "Actual"],
                "bills.csv": ["Bill Name", "Amount Due", "Due Date", "Status"],
                "non_essentials.csv": ["Expense", "Amount", "Date", "Notes"],
                "savings.csv": ["Deposit", "Date"],
                "settings.csv": ["Key", "Value"]
            }
            
            for filename, columns in files_structure.items():
                filepath = os.path.join(self.data_dir, filename)
                df = pd.DataFrame(columns=columns)
                df.to_csv(filepath, index=False)
                
        except Exception as e:
            raise Exception(f"Error resetting data: {e}")
    
    def export_all_data(self, export_path: str) -> None:
        """Export all data to a single Excel file"""
        try:
            with pd.ExcelWriter(export_path, engine='openpyxl') as writer:
                self.get_income_data().to_excel(writer, sheet_name='Income', index=False)
                self.get_essentials_data().to_excel(writer, sheet_name='Essentials', index=False)
                self.get_bills_data().to_excel(writer, sheet_name='Bills', index=False)
                self.get_non_essentials_data().to_excel(writer, sheet_name='Non-Essentials', index=False)
                self.get_savings_data().to_excel(writer, sheet_name='Savings', index=False)
                
                # Add summary sheet
                summary = pd.DataFrame(self.get_budget_summary())
                summary.to_excel(writer, sheet_name='Summary')
                
        except Exception as e:
            raise Exception(f"Error exporting data: {e}")
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """Validate data integrity across all CSV files"""
        issues = {
            'income': [],
            'essentials': [],
            'bills': [],
            'non_essentials': [],
            'savings': []
        }
        
        # Validate income data
        income = self.get_income_data()
        if not income.empty:
            if income['Amount'].min() <= 0:
                issues['income'].append("Negative or zero income amounts found")
            if income.isnull().any().any():
                issues['income'].append("Missing values found")
        
        # Validate essentials data
        essentials = self.get_essentials_data()
        if not essentials.empty:
            if (essentials['Expected'] < 0).any() or (essentials['Actual'] < 0).any():
                issues['essentials'].append("Negative amounts found")
        
        # Validate bills data
        bills = self.get_bills_data()
        if not bills.empty:
            if bills['Amount Due'].min() <= 0:
                issues['bills'].append("Non-positive bill amounts found")
            invalid_status = ~bills['Status'].isin(['Paid', 'Unpaid'])
            if invalid_status.any():
                issues['bills'].append("Invalid status values found")
        
        # Validate non-essentials data
        non_essentials = self.get_non_essentials_data()
        if not non_essentials.empty:
            if non_essentials['Amount'].min() <= 0:
                issues['non_essentials'].append("Non-positive expense amounts found")
        
        # Validate savings data
        savings = self.get_savings_data()
        if not savings.empty:
            if savings['Deposit'].min() <= 0:
                issues['savings'].append("Non-positive savings amounts found")
        
        return {k: v for k, v in issues.items() if v}  # Return only categories with issues
