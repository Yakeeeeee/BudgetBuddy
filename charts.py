"""
Chart Manager for Budget Tracker
Handles all chart creation and visualization using Matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import seaborn as sns

# Set style for better-looking charts
plt.style.use('default')
sns.set_palette("husl")


class ChartManager:
    def __init__(self):
        self.setup_chart_defaults()
    
    def setup_chart_defaults(self):
        """Setup default chart configurations"""
        self.colors = {
            'essentials': '#FF9800',
            'non_essentials': '#2196F3', 
            'savings': '#9C27B0',
            'income': '#4CAF50',
            'bills': '#F44336',
            'expected': '#1f77b4',
            'actual': '#ff7f0e',
            'positive': '#4CAF50',
            'negative': '#F44336'
        }
        
        self.figure_size = (10, 6)
        self.dpi = 100
        # Suppress matplotlib memory warnings and enable tight layout
        plt.rcParams['figure.max_open_warning'] = 50
    
    def create_budget_pie_chart(self, allocations: Dict[str, float], 
                               actuals: Dict[str, float]) -> Figure:
        """Create pie chart showing budget allocation vs actual spending"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Budget allocation (target)
        labels = list(allocations.keys())
        sizes = list(allocations.values())
        colors = [self.colors['essentials'], self.colors['non_essentials'], self.colors['savings']]
        
        # Only show pie chart if there are non-zero values
        if sum(sizes) > 0:
            wedges1, texts1, autotexts1 = ax1.pie(
                sizes, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10}
            )
            ax1.set_title('Budget Allocation (Target)', fontsize=14, fontweight='bold', pad=20)
        else:
            ax1.text(0.5, 0.5, 'No budget data', transform=ax1.transAxes, 
                    ha='center', va='center', fontsize=12)
            ax1.set_title('Budget Allocation (Target)', fontsize=14, fontweight='bold', pad=20)
        
        # Actual spending
        actual_sizes = list(actuals.values())
        if sum(actual_sizes) > 0:
            wedges2, texts2, autotexts2 = ax2.pie(
                actual_sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10}
            )
            ax2.set_title('Actual Spending', fontsize=14, fontweight='bold', pad=20)
        else:
            ax2.text(0.5, 0.5, 'No spending data', transform=ax2.transAxes,
                    ha='center', va='center', fontsize=12)
            ax2.set_title('Actual Spending', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return fig
    
    def create_essentials_chart(self, essentials_data: pd.DataFrame) -> Figure:
        """Create bar chart comparing expected vs actual essentials spending"""
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        if essentials_data.empty:
            ax.text(0.5, 0.5, 'No essentials data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title('Essentials: Expected vs Actual', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        categories = essentials_data['Category'].tolist()
        expected = essentials_data['Expected'].tolist()
        actual = essentials_data['Actual'].tolist()
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, expected, width, label='Expected', 
                      color=self.colors['expected'], alpha=0.8)
        bars2 = ax.bar(x + width/2, actual, width, label='Actual', 
                      color=self.colors['actual'], alpha=0.8)
        
        ax.set_xlabel('Categories', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₱)', fontsize=12, fontweight='bold')
        ax.set_title('Essentials: Expected vs Actual', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        self._add_value_labels(ax, bars1)
        self._add_value_labels(ax, bars2)
        
        plt.tight_layout()
        return fig
    
    def create_non_essentials_chart(self, non_essentials_data: pd.DataFrame) -> Figure:
        """Create line chart showing non-essentials spending trend"""
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        if non_essentials_data.empty:
            ax.text(0.5, 0.5, 'No non-essentials data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title('Non-Essentials Spending Trend', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        # Prepare data
        data = non_essentials_data.copy()
        data['Date'] = pd.to_datetime(data['Date'])
        
        # Group by date and sum amounts
        daily_spending = data.groupby('Date')['Amount'].sum().reset_index()
        daily_spending = daily_spending.sort_values('Date')
        
        # Create cumulative spending
        daily_spending['Cumulative'] = daily_spending['Amount'].cumsum()
        
        # Plot both daily and cumulative
        ax2 = ax.twinx()
        
        # Daily spending (bars)
        ax.bar(daily_spending['Date'], daily_spending['Amount'], 
               color=self.colors['non_essentials'], alpha=0.6, label='Daily Spending')
        
        # Cumulative spending (line)
        ax2.plot(daily_spending['Date'], daily_spending['Cumulative'], 
                color=self.colors['negative'], marker='o', linewidth=2, 
                label='Cumulative Spending')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Daily Amount ($)', fontsize=12, fontweight='bold', color=self.colors['non_essentials'])
        ax2.set_ylabel('Cumulative Amount ($)', fontsize=12, fontweight='bold', color=self.colors['negative'])
        ax.set_title('Non-Essentials Spending Trend', fontsize=16, fontweight='bold', pad=20)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(daily_spending) // 10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        
        plt.tight_layout()
        return fig
    
    def create_savings_chart(self, savings_data: pd.DataFrame) -> Figure:
        """Create line chart showing savings growth over time"""
        fig, ax = plt.subplots(figsize=self.figure_size)
        
        if savings_data.empty:
            ax.text(0.5, 0.5, 'No savings data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title('Savings Growth', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        # Prepare data
        data = savings_data.copy()
        data['Date'] = pd.to_datetime(data['Date'])
        data = data.sort_values('Date')
        
        # Calculate cumulative savings
        data['Cumulative'] = data['Deposit'].cumsum()
        
        # Plot savings deposits and cumulative line
        ax.scatter(data['Date'], data['Deposit'], color=self.colors['savings'], 
                  s=60, alpha=0.7, label='Deposits', zorder=3)
        
        ax.plot(data['Date'], data['Cumulative'], color=self.colors['positive'], 
               linewidth=3, marker='o', markersize=4, label='Cumulative Savings')
        
        # Fill area under cumulative line
        ax.fill_between(data['Date'], data['Cumulative'], alpha=0.2, 
                       color=self.colors['positive'])
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₱)', fontsize=12, fontweight='bold')
        ax.set_title('Savings Growth', fontsize=16, fontweight='bold', pad=20)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(data) // 10)))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add annotations for milestones
        max_savings = data['Cumulative'].max()
        if max_savings > 0:
            max_date = data.loc[data['Cumulative'].idxmax(), 'Date']
            ax.annotate(f'Peak: ${max_savings:,.2f}', 
                       xy=(max_date, max_savings),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.tight_layout()
        return fig
    
    def create_monthly_summary_chart(self, income_data: pd.DataFrame, 
                                   essentials_data: pd.DataFrame,
                                   non_essentials_data: pd.DataFrame,
                                   savings_data: pd.DataFrame) -> Figure:
        """Create monthly summary comparison chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Prepare monthly data
        current_month = datetime.now().replace(day=1)
        
        # Calculate monthly totals
        monthly_data = {
            'Income': 0,
            'Essentials': 0,
            'Non-Essentials': 0,
            'Savings': 0
        }
        
        if not income_data.empty:
            income_data['Date'] = pd.to_datetime(income_data['Date'])
            monthly_income = income_data[income_data['Date'] >= current_month]
            monthly_data['Income'] = monthly_income['Amount'].sum()
        
        if not essentials_data.empty:
            monthly_data['Essentials'] = essentials_data['Actual'].sum()
        
        if not non_essentials_data.empty:
            non_essentials_data['Date'] = pd.to_datetime(non_essentials_data['Date'])
            monthly_non_essentials = non_essentials_data[non_essentials_data['Date'] >= current_month]
            monthly_data['Non-Essentials'] = monthly_non_essentials['Amount'].sum()
        
        if not savings_data.empty:
            savings_data['Date'] = pd.to_datetime(savings_data['Date'])
            monthly_savings = savings_data[savings_data['Date'] >= current_month]
            monthly_data['Savings'] = monthly_savings['Deposit'].sum()
        
        # Create stacked bar chart
        categories = list(monthly_data.keys())
        values = list(monthly_data.values())
        colors = [self.colors['income'], self.colors['essentials'], 
                 self.colors['non_essentials'], self.colors['savings']]
        
        bars = ax.bar(categories, values, color=colors, alpha=0.8)
        
        ax.set_ylabel('Amount (₱)', fontsize=12, fontweight='bold')
        ax.set_title(f'Monthly Summary - {current_month.strftime("%B %Y")}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        self._add_value_labels(ax, bars)
        
        # Add budget allocation lines for comparison
        if monthly_data['Income'] > 0:
            income = monthly_data['Income']
            ax.axhline(y=income * 0.5, color='red', linestyle='--', alpha=0.7, 
                      label='50% Target (Essentials)')
            ax.axhline(y=income * 0.3, color='blue', linestyle='--', alpha=0.7,
                      label='30% Target (Non-Essentials)')
            ax.axhline(y=income * 0.2, color='purple', linestyle='--', alpha=0.7,
                      label='20% Target (Savings)')
            ax.legend()
        
        plt.tight_layout()
        return fig
    
    def create_bills_status_chart(self, bills_data: pd.DataFrame) -> Figure:
        """Create chart showing bills payment status"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        if bills_data.empty:
            ax1.text(0.5, 0.5, 'No bills data available', transform=ax1.transAxes,
                    ha='center', va='center', fontsize=14)
            ax2.text(0.5, 0.5, 'No bills data available', transform=ax2.transAxes,
                    ha='center', va='center', fontsize=14)
            ax1.set_title('Bills Status', fontsize=16, fontweight='bold', pad=20)
            ax2.set_title('Bills Amount by Status', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        # Status distribution (pie chart)
        status_counts = bills_data['Status'].value_counts()
        colors_status = [self.colors['positive'] if status == 'Paid' else self.colors['negative'] 
                        for status in status_counts.index]
        
        wedges1, texts1, autotexts1 = ax1.pie(
            status_counts.values,
            labels=status_counts.index,
            colors=colors_status,
            autopct='%1.1f%%',
            startangle=90
        )
        ax1.set_title('Bills Status Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Amount by status (bar chart)
        status_amounts = bills_data.groupby('Status')['Amount Due'].sum()
        bars = ax2.bar(status_amounts.index, status_amounts.values, color=colors_status, alpha=0.8)
        ax2.set_ylabel('Total Amount ($)', fontsize=12, fontweight='bold')
        ax2.set_title('Bills Amount by Status', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels
        self._add_value_labels(ax2, bars)
        
        plt.tight_layout()
        return fig
    
    def create_spending_trend_chart(self, non_essentials_data: pd.DataFrame, 
                                  days: int = 30) -> Figure:
        """Create detailed spending trend chart for last N days"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if non_essentials_data.empty:
            ax.text(0.5, 0.5, 'No spending data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title(f'Spending Trend - Last {days} Days', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        # Filter data for last N days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        data = non_essentials_data.copy()
        data['Date'] = pd.to_datetime(data['Date']).dt.date
        data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
        
        if data.empty:
            ax.text(0.5, 0.5, f'No spending data for last {days} days', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title(f'Spending Trend - Last {days} Days', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        # Group by date
        daily_spending = data.groupby('Date')['Amount'].sum().reset_index()
        
        # Create complete date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        complete_data = pd.DataFrame({'Date': date_range.date})
        complete_data = complete_data.merge(daily_spending, on='Date', how='left')
        complete_data['Amount'] = complete_data['Amount'].fillna(0)
        
        # Plot
        ax.plot(complete_data['Date'], complete_data['Amount'], 
               marker='o', linewidth=2, markersize=4, color=self.colors['non_essentials'])
        ax.fill_between(complete_data['Date'], complete_data['Amount'], 
                       alpha=0.3, color=self.colors['non_essentials'])
        
        # Add average line
        avg_spending = complete_data['Amount'].mean()
        ax.axhline(y=avg_spending, color='red', linestyle='--', alpha=0.7,
                  label=f'Average: ${avg_spending:.2f}')
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Daily Spending ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Daily Spending Trend - Last {days} Days', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def create_budget_progress_chart(self, income_total: float, 
                                   essentials_actual: float,
                                   non_essentials_actual: float,
                                   savings_actual: float) -> Figure:
        """Create budget progress chart showing 50/30/20 adherence"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if income_total <= 0:
            ax.text(0.5, 0.5, 'No income data available', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14)
            ax.set_title('Budget Progress (50/30/20 Rule)', fontsize=16, fontweight='bold', pad=20)
            return fig
        
        categories = ['Essentials\n(50%)', 'Non-Essentials\n(30%)', 'Savings\n(20%)']
        targets = [income_total * 0.5, income_total * 0.3, income_total * 0.2]
        actuals = [essentials_actual, non_essentials_actual, savings_actual]
        
        x = np.arange(len(categories))
        width = 0.35
        
        # Create bars
        bars1 = ax.bar(x - width/2, targets, width, label='Target', 
                      color=['#FF9800', '#2196F3', '#9C27B0'], alpha=0.6)
        bars2 = ax.bar(x + width/2, actuals, width, label='Actual',
                      color=['#FF9800', '#2196F3', '#9C27B0'], alpha=0.9)
        
        # Add percentage labels
        for i, (target, actual) in enumerate(zip(targets, actuals)):
            if target > 0:
                percentage = (actual / target) * 100
                color = self.colors['positive'] if percentage <= 100 else self.colors['negative']
                ax.text(i, max(target, actual) + income_total * 0.02, 
                       f'{percentage:.1f}%', ha='center', va='bottom',
                       fontweight='bold', color=color)
        
        ax.set_xlabel('Categories', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount (₱)', fontsize=12, fontweight='bold')
        ax.set_title('Budget Progress (50/30/20 Rule)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        self._add_value_labels(ax, bars1)
        self._add_value_labels(ax, bars2)
        
        plt.tight_layout()
        return fig
    
    def _add_value_labels(self, ax, bars):
        """Add value labels on top of bars"""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'${height:,.0f}', ha='center', va='bottom', fontsize=9)
    
    def set_theme(self, dark_mode: bool = True):
        """Set chart theme based on application theme"""
        if dark_mode:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
    
    def save_chart(self, figure: Figure, filename: str, dpi: int = 300):
        """Save chart to file"""
        figure.savefig(filename, dpi=dpi, bbox_inches='tight', 
                      facecolor='white', edgecolor='none')
        plt.close(figure)
