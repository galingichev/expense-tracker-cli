import json
import os
from datetime import datetime
from collections import defaultdict

class IncomeExpenseTracker:
    def __init__(self, data_file='financial_data.json'):
        self.data_file = data_file
        self.data = self.load_data()
        self.expenses = self.data.get('expenses', [])
        self.monthly_income = self.data.get('monthly_income', 0.0)
        self.currency = self.data.get('currency', 'USD')
        self.currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 
            'CAD': 'C$', 'AUD': 'A$', 'CHF': 'Fr', 'CNY': '¥',
            'INR': '₹', 'BRL': 'R$', 'RUB': '₽', 'KRW': '₩',
            'SEK': 'kr', 'NOK': 'kr', 'DKK': 'kr', 'PLN': 'zł',
            'CZK': 'Kč', 'HUF': 'Ft', 'BGN': 'лв', 'RON': 'lei'
        }

    def get_currency_symbol(self):
        """Get currency symbol for display."""
        return self.currency_symbols.get(self.currency, self.currency + ' ')

    def load_data(self):
        """Load all financial data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                print("Warning: Could not load existing data. Starting fresh.")
                return {}
        return {}

    def save_data(self):
        """Save all financial data to JSON file."""
        try:
            self.data = {
                'expenses': self.expenses,
                'monthly_income': self.monthly_income,
                'currency': self.currency
            }
            with open(self.data_file, 'w') as file:
                json.dump(self.data, file, indent=2)
            print("✓ Financial data saved successfully!")
        except Exception as e:
            print(f"Error saving data: {e}")

    def set_currency(self):
        """Allow user to select currency."""
        print("\n💱 AVAILABLE CURRENCIES:")
        print("="*50)
        currencies = list(self.currency_symbols.keys())
        
        # Display in columns
        for i in range(0, len(currencies), 4):
            row = currencies[i:i+4]
            formatted_row = [f"{curr} ({self.currency_symbols[curr]})" for curr in row]
            print(f"{formatted_row[0]:<12} {formatted_row[1] if len(formatted_row) > 1 else '':<12} {formatted_row[2] if len(formatted_row) > 2 else '':<12} {formatted_row[3] if len(formatted_row) > 3 else '':<12}")
        
        print("="*50)
        
        while True:
            new_currency = input(f'Enter currency code (current: {self.currency}): ').strip().upper()
            if not new_currency:
                print("Currency unchanged.")
                return
            
            if new_currency in self.currency_symbols:
                self.currency = new_currency
                print(f"✓ Currency changed to {new_currency} ({self.get_currency_symbol()})")
                return
            else:
                print("Invalid currency code. Please try again.")

    def set_monthly_income(self):
        """Set or update monthly income."""
        current_symbol = self.get_currency_symbol()
        print(f"\n💰 Current monthly income: {current_symbol}{self.monthly_income:.2f}")
        
        try:
            new_income = input(f'Enter new monthly income ({current_symbol}): ').strip()
            if not new_income:
                print("Income unchanged.")
                return
            
            income_amount = float(new_income)
            if income_amount < 0:
                print("Warning: Negative income set. This will be treated as debt.")
            
            self.monthly_income = round(income_amount, 2)
            print(f"✓ Monthly income set to {current_symbol}{self.monthly_income:.2f}")
            
        except ValueError:
            print("Error: Please enter a valid amount!")

    def add_expense(self, amount, category, description=""):
        """Add a new expense with validation."""
        try:
            amount = float(amount)
            if amount <= 0:
                print("Error: Amount must be positive!")
                return False
            
            if not category.strip():
                print("Error: Category cannot be empty!")
                return False
            
            expense = {
                'amount': round(amount, 2),
                'category': category.strip().title(),
                'description': description.strip(),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.expenses.append(expense)
            symbol = self.get_currency_symbol()
            print(f"✓ Added expense: {symbol}{amount:.2f} for {category}")
            return True
            
        except ValueError:
            print("Error: Please enter a valid amount!")
            return False

    def print_expenses(self, expenses_list=None):
        """Print expenses in a formatted table."""
        expenses_to_show = expenses_list if expenses_list is not None else self.expenses
        
        if not expenses_to_show:
            print("No expenses found.")
            return
        
        symbol = self.get_currency_symbol()
        print("\n" + "="*85)
        print(f"{'Date':<20} {'Category':<15} {'Amount':<12} {'Description':<35}")
        print("="*85)
        
        for expense in expenses_to_show:
            date = expense.get('date', 'N/A')[:16]
            category = expense['category'][:14]
            amount = f"{symbol}{expense['amount']:.2f}"
            description = expense.get('description', '')[:34]
            
            print(f"{date:<20} {category:<15} {amount:<12} {description:<35}")
        
        print("="*85)

    def total_expenses(self, expenses_list=None):
        """Calculate total expenses."""
        expenses_to_calc = expenses_list if expenses_list is not None else self.expenses
        return sum(expense['amount'] for expense in expenses_to_calc)

    def filter_expenses_by_category(self, category):
        """Filter expenses by category (case-insensitive)."""
        category_lower = category.lower()
        return [expense for expense in self.expenses 
                if expense['category'].lower() == category_lower]

    def get_monthly_expenses(self):
        """Calculate current month's expenses."""
        current_month = datetime.now().strftime('%Y-%m')
        monthly_expenses = [
            expense for expense in self.expenses
            if expense.get('date', '').startswith(current_month)
        ]
        return monthly_expenses

    def calculate_financial_summary(self):
        """Calculate comprehensive financial summary."""
        total_expenses = self.total_expenses()
        monthly_expenses = self.total_expenses(self.get_monthly_expenses())
        
        # Calculate net balance
        net_balance = self.monthly_income - monthly_expenses
        
        # Calculate required monthly income to cover all expenses
        required_income = total_expenses
        
        # Calculate additional income needed to stay positive
        additional_income_needed = max(0, monthly_expenses - self.monthly_income)
        
        # Calculate savings (if positive)
        monthly_savings = max(0, net_balance)
        
        return {
            'total_expenses': total_expenses,
            'monthly_expenses': monthly_expenses,
            'net_balance': net_balance,
            'required_income': required_income,
            'additional_income_needed': additional_income_needed,
            'monthly_savings': monthly_savings
        }

    def show_financial_dashboard(self):
        """Display comprehensive financial dashboard."""
        summary = self.calculate_financial_summary()
        symbol = self.get_currency_symbol()
        current_month = datetime.now().strftime('%B %Y')
        
        print("\n" + "="*60)
        print(f"📊 FINANCIAL DASHBOARD - {current_month}")
        print("="*60)
        
        # Income Section
        print(f"💰 Monthly Income:          {symbol}{self.monthly_income:>12.2f}")
        print("-"*60)
        
        # Expenses Section
        print(f"💳 Total All Expenses:      {symbol}{summary['total_expenses']:>12.2f}")
        print(f"📅 This Month's Expenses:   {symbol}{summary['monthly_expenses']:>12.2f}")
        print("-"*60)
        
        # Balance Section
        balance_color = "🔴" if summary['net_balance'] < 0 else "🟢"
        print(f"{balance_color} Net Monthly Balance:     {symbol}{summary['net_balance']:>12.2f}")
        
        if summary['net_balance'] < 0:
            print(f"⚠️  Deficit Amount:          {symbol}{abs(summary['net_balance']):>12.2f}")
        
        print("-"*60)
        
        # Analysis Section
        print("📈 FINANCIAL ANALYSIS:")
        print("-"*60)
        
        if summary['monthly_savings'] > 0:
            print(f"💚 Monthly Savings:         {symbol}{summary['monthly_savings']:>12.2f}")
        
        if summary['additional_income_needed'] > 0:
            print(f"🔺 Additional Income Needed: {symbol}{summary['additional_income_needed']:>12.2f}")
            print(f"   (to avoid negative balance)")
        
        print(f"📊 Required Monthly Income:  {symbol}{summary['required_income']:>12.2f}")
        print(f"   (to cover all expenses)")
        
        # Recommendations
        print("-"*60)
        print("💡 RECOMMENDATIONS:")
        
        if summary['net_balance'] < 0:
            print("   • You're spending more than you earn this month")
            print(f"   • Consider reducing expenses by {symbol}{abs(summary['net_balance']):.2f}")
            print(f"   • Or increase income by {symbol}{summary['additional_income_needed']:.2f}")
        elif summary['monthly_savings'] > 0:
            savings_rate = (summary['monthly_savings'] / self.monthly_income) * 100
            print(f"   • Great job! You're saving {savings_rate:.1f}% of your income")
            if savings_rate < 20:
                print("   • Consider increasing savings rate to 20% if possible")
        
        if summary['total_expenses'] > self.monthly_income * 12:
            annual_deficit = summary['total_expenses'] - (self.monthly_income * 12)
            print(f"   • Annual expenses exceed annual income by {symbol}{annual_deficit:.2f}")
        
        print("="*60)

    def get_category_summary(self):
        """Get summary of expenses by category."""
        if not self.expenses:
            print("No expenses to summarize.")
            return
        
        category_totals = defaultdict(float)
        for expense in self.expenses:
            category_totals[expense['category']] += expense['amount']
        
        symbol = self.get_currency_symbol()
        print("\n" + "="*45)
        print("📊 CATEGORY SUMMARY")
        print("="*45)
        
        total = 0
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            percentage = (amount / self.total_expenses()) * 100 if self.total_expenses() > 0 else 0
            print(f"{category:<25} {symbol}{amount:>10.2f} ({percentage:>5.1f}%)")
            total += amount
        
        print("-"*45)
        print(f"{'TOTAL':<25} {symbol}{total:>10.2f} (100.0%)")
        print("="*45)

    def delete_expense(self, index):
        """Delete an expense by index."""
        try:
            if 0 <= index < len(self.expenses):
                deleted = self.expenses.pop(index)
                symbol = self.get_currency_symbol()
                print(f"✓ Deleted expense: {symbol}{deleted['amount']:.2f} for {deleted['category']}")
                return True
            else:
                print("Error: Invalid expense number!")
                return False
        except (ValueError, IndexError):
            print("Error: Invalid expense number!")
            return False

    def search_expenses(self, keyword):
        """Search expenses by keyword in category or description."""
        keyword_lower = keyword.lower()
        matching_expenses = [
            expense for expense in self.expenses
            if (keyword_lower in expense['category'].lower() or 
                keyword_lower in expense.get('description', '').lower())
        ]
        return matching_expenses

    def get_monthly_breakdown(self):
        """Get expenses breakdown by month."""
        if not self.expenses:
            print("No expenses to analyze.")
            return
        
        monthly_totals = defaultdict(float)
        for expense in self.expenses:
            try:
                date_str = expense.get('date', '')
                if date_str:
                    month = date_str[:7]  # YYYY-MM
                    monthly_totals[month] += expense['amount']
            except:
                continue
        
        if not monthly_totals:
            print("No dated expenses found.")
            return
        
        symbol = self.get_currency_symbol()
        print("\n" + "="*40)
        print("📅 MONTHLY BREAKDOWN")
        print("="*40)
        
        for month in sorted(monthly_totals.keys()):
            month_name = datetime.strptime(month + "-01", "%Y-%m-%d").strftime("%B %Y")
            deficit_surplus = self.monthly_income - monthly_totals[month]
            status = "💚" if deficit_surplus >= 0 else "🔴"
            
            print(f"{month_name:<20} {symbol}{monthly_totals[month]:>10.2f} {status}")
            if deficit_surplus < 0:
                print(f"{'  Deficit:':<20} {symbol}{abs(deficit_surplus):>10.2f}")
            else:
                print(f"{'  Surplus:':<20} {symbol}{deficit_surplus:>10.2f}")
            print("-"*40)
        
        print("="*40)

    def run(self):
        """Main program loop."""
        print("🏦 Welcome to Complete Income & Expense Tracker!")
        print(f"Current Currency: {self.currency} ({self.get_currency_symbol()})")
        
        while True:
            print('\n' + "="*55)
            print('💰 INCOME & EXPENSE TRACKER MENU')
            print("="*55)
            print('1.  Set monthly income')
            print('2.  Add an expense')
            print('3.  List all expenses')
            print('4.  Financial dashboard')
            print('5.  Filter expenses by category')
            print('6.  Category summary')
            print('7.  Monthly breakdown')
            print('8.  Search expenses')
            print('9.  Delete an expense')
            print('10. Change currency')
            print('11. Save & Exit')
            print('12. Exit without saving')
            print("="*55)
           
            choice = input('Enter your choice (1-12): ').strip()

            if choice == '1':
                self.set_monthly_income()

            elif choice == '2':
                symbol = self.get_currency_symbol()
                amount = input(f'Enter amount ({symbol}): ').strip()
                category = input('Enter category: ').strip()
                description = input('Enter description (optional): ').strip()
                self.add_expense(amount, category, description)

            elif choice == '3':
                print('\n📋 ALL EXPENSES:')
                self.print_expenses()
                if self.expenses:
                    symbol = self.get_currency_symbol()
                    print(f"\nTotal: {symbol}{self.total_expenses():.2f}")

            elif choice == '4':
                self.show_financial_dashboard()

            elif choice == '5':
                category = input('Enter category to filter: ').strip()
                if category:
                    filtered = self.filter_expenses_by_category(category)
                    print(f'\n📊 Expenses for "{category}":')
                    self.print_expenses(filtered)
                    if filtered:
                        symbol = self.get_currency_symbol()
                        print(f"Category Total: {symbol}{self.total_expenses(filtered):.2f}")

            elif choice == '6':
                self.get_category_summary()

            elif choice == '7':
                self.get_monthly_breakdown()

            elif choice == '8':
                keyword = input('Enter search keyword: ').strip()
                if keyword:
                    results = self.search_expenses(keyword)
                    print(f'\n🔍 Search results for "{keyword}":')
                    self.print_expenses(results)
                    if results:
                        symbol = self.get_currency_symbol()
                        print(f"Results Total: {symbol}{self.total_expenses(results):.2f}")

            elif choice == '9':
                if not self.expenses:
                    print("No expenses to delete.")
                    continue
                
                self.print_expenses()
                try:
                    index = int(input(f'Enter expense number to delete (1-{len(self.expenses)}): ')) - 1
                    self.delete_expense(index)
                except ValueError:
                    print("Please enter a valid number.")

            elif choice == '10':
                self.set_currency()

            elif choice == '11':
                self.save_data()
                print('👋 Goodbye! Your financial data has been saved.')
                break

            elif choice == '12':
                confirm = input('Are you sure you want to exit without saving? (y/N): ')
                if confirm.lower() in ['y', 'yes']:
                    print('👋 Goodbye!')
                    break

            else:
                print('❌ Invalid choice. Please enter a number between 1-12.')

            # Pause for user to read output
            input('\nPress Enter to continue...')

def main():
    """Entry point of the program."""
    tracker = IncomeExpenseTracker()
    try:
        tracker.run()
    except KeyboardInterrupt:
        print('\n\n👋 Program interrupted. Goodbye!')
    except Exception as e:
        print(f'\n❌ An unexpected error occurred: {e}')

if __name__ == "__main__":
    main()