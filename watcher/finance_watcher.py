"""
Platinum Tier FinanceWatcher - Financial Transaction Monitoring

Monitors financial transactions in real-time, integrates with bank APIs and financial services,
monitors for unusual transaction patterns, generates alerts for significant financial events,
tracks and categorizes expenses and revenue, supports multiple currencies and accounts,
generates financial summary reports.
"""
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import random
import uuid
from decimal import Decimal, InvalidOperation
from dataclasses import asdict


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    INVESTMENT = "investment"
    LOAN = "loan"


class TransactionCategory(Enum):
    SALARY = "salary"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    FOOD = "food"
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    UTILITIES = "utilities"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    INVESTMENT = "investment"
    TAX = "tax"
    OTHER = "other"


class AlertType(Enum):
    UNUSUAL_SPENDING = "unusual_spending"
    LARGE_TRANSACTION = "large_transaction"
    FRAUD_SUSPICION = "fraud_suspicion"
    BUDGET_EXCEEDED = "budget_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"


class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    INR = "INR"
    BRL = "BRL"


@dataclass
class FinancialTransaction:
    id: str
    account_id: str
    amount: Decimal
    currency: Currency
    transaction_type: TransactionType
    category: TransactionCategory
    description: str
    merchant: str
    timestamp: datetime
    location: Optional[str] = None
    tags: Optional[List[str]] = None
    original_amount: Optional[Decimal] = None
    original_currency: Optional[Currency] = None
    exchange_rate: Optional[Decimal] = None
    status: str = "completed"  # pending, completed, failed, cancelled
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinancialAlert:
    id: str
    type: AlertType
    severity: str  # info, warning, critical
    message: str
    timestamp: datetime
    transaction_id: Optional[str] = None
    account_id: Optional[str] = None
    amount: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FinancialSummary:
    period_start: datetime
    period_end: datetime
    total_income: Decimal
    total_expenses: Decimal
    net_flow: Decimal
    income_by_category: Dict[TransactionCategory, Decimal]
    expenses_by_category: Dict[TransactionCategory, Decimal]
    income_by_account: Dict[str, Decimal]
    expenses_by_account: Dict[str, Decimal]
    transaction_count: int
    alerts_generated: int


class FinanceWatcher:
    """
    Platinum Tier FinanceWatcher - Financial Transaction Monitoring
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Finance Watcher system"""
        self.config = self._load_config(config_path)
        self.financial_logs_dir = Path(self.config.get('financial_logs_dir', 'AI_Employee_Vault/Platinum/Financial_Monitoring'))
        self.reports_dir = Path(self.config.get('reports_dir', 'AI_Employee_Vault/Platinum/Advanced_Reports'))

        # Initialize financial data stores
        self.transactions: Dict[str, FinancialTransaction] = {}
        self.accounts: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[FinancialAlert] = []
        self.patterns: Dict[str, Any] = {}
        self.budgets: Dict[str, Decimal] = {}
        self.currency_rates: Dict[str, Decimal] = {}

        # Initialize thresholds and patterns
        self._init_default_thresholds()
        self._init_default_patterns()

        # Setup logging
        self._setup_logging()
        self.financial_logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'financial_logs_dir': 'AI_Employee_Vault/Platinum/Financial_Monitoring',
            'reports_dir': 'AI_Employee_Vault/Platinum/Advanced_Reports',
            'data_retention_days': 365,  # 1 year
            'alert_thresholds': {
                'large_transaction_usd': 1000,
                'unusual_spending_multiplier': 2.0,
                'fraud_suspicion_amount_usd': 500
            },
            'api_integrations': {
                'bank_apis': [],
                'payment_processors': []
            }
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                return config
            except Exception as e:
                print(f"Error loading config, using defaults: {e}")
                return default_config
        return default_config

    def _init_default_thresholds(self):
        """Initialize default alert thresholds"""
        self.thresholds = self.config.get('alert_thresholds', {
            'large_transaction_usd': 1000,
            'unusual_spending_multiplier': 2.0,
            'fraud_suspicion_amount_usd': 500
        })

    def _init_default_patterns(self):
        """Initialize default transaction patterns for anomaly detection"""
        self.patterns = {
            'daily_spending_limits': {},  # account_id -> limit
            'weekly_spending_limits': {},
            'monthly_spending_limits': {},
            'usual_merchants': {},  # account_id -> set of usual merchants
            'usual_categories': {},  # account_id -> set of usual categories
            'usual_amount_ranges': {},  # account_id -> (min, max)
            'usual_time_windows': {},  # account_id -> [(start_hour, end_hour)]
        }

    def _setup_logging(self):
        """Setup logging for the Finance Watcher"""
        log_file = self.financial_logs_dir / f"finance_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def add_account(self, account_id: str, account_name: str, initial_balance: Decimal = Decimal('0'), currency: Currency = Currency.USD):
        """Add a new financial account to monitor"""
        self.accounts[account_id] = {
            'id': account_id,
            'name': account_name,
            'currency': currency.value,
            'balance': str(initial_balance),
            'created_at': datetime.now().isoformat(),
            'transactions': []
        }

        # Initialize account-specific patterns
        self.patterns['usual_merchants'][account_id] = set()
        self.patterns['usual_categories'][account_id] = set()
        self.patterns['usual_amount_ranges'][account_id] = (Decimal('0'), Decimal('10000'))
        self.patterns['usual_time_windows'][account_id] = [(9, 17)]  # Business hours default

        self.logger.info(f"Account {account_id} ({account_name}) added")

    def record_transaction(self, transaction: FinancialTransaction) -> bool:
        """Record a new financial transaction and check for anomalies"""
        # Validate transaction
        if not self._validate_transaction(transaction):
            return False

        # Add to transaction store
        self.transactions[transaction.id] = transaction

        # Update account transaction history
        if transaction.account_id in self.accounts:
            self.accounts[transaction.account_id]['transactions'].append(transaction.id)

        # Update patterns based on new transaction
        self._update_account_patterns(transaction)

        # Check for anomalies and generate alerts
        alerts = self._analyze_transaction(transaction)
        for alert in alerts:
            self.alerts.append(alert)
            self._log_alert(alert)

        # Log transaction
        self._log_transaction(transaction)

        self.logger.info(f"Transaction {transaction.id} recorded: {transaction.amount} {transaction.currency.value} - {transaction.description}")
        return True

    def _validate_transaction(self, transaction: FinancialTransaction) -> bool:
        """Validate a transaction before recording"""
        try:
            # Check if amount is valid
            if transaction.amount <= 0:
                self.logger.error(f"Invalid transaction amount: {transaction.amount}")
                return False

            # Check if required fields are present
            if not transaction.id or not transaction.account_id or not transaction.description:
                self.logger.error("Missing required transaction fields")
                return False

            # Check if account exists
            if transaction.account_id not in self.accounts:
                self.logger.error(f"Unknown account {transaction.account_id}")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Transaction validation error: {str(e)}")
            return False

    def _update_account_patterns(self, transaction: FinancialTransaction):
        """Update account-specific patterns based on transaction"""
        account_id = transaction.account_id

        # Add merchant to usual merchants
        if account_id not in self.patterns['usual_merchants']:
            self.patterns['usual_merchants'][account_id] = set()
        self.patterns['usual_merchants'][account_id].add(transaction.merchant)

        # Add category to usual categories
        if account_id not in self.patterns['usual_categories']:
            self.patterns['usual_categories'][account_id] = set()
        self.patterns['usual_categories'][account_id].add(transaction.category)

        # Update amount range
        if account_id not in self.patterns['usual_amount_ranges']:
            self.patterns['usual_amount_ranges'][account_id] = (transaction.amount, transaction.amount)
        else:
            min_val, max_val = self.patterns['usual_amount_ranges'][account_id]
            min_val = min(min_val, transaction.amount)
            max_val = max(max_val, transaction.amount)
            self.patterns['usual_amount_ranges'][account_id] = (min_val, max_val)

    def _analyze_transaction(self, transaction: FinancialTransaction) -> List[FinancialAlert]:
        """Analyze a transaction for potential anomalies"""
        alerts = []

        # Check for large transactions
        if self._is_large_transaction(transaction):
            alert = FinancialAlert(
                id=f"alert_large_{transaction.id}",
                type=AlertType.LARGE_TRANSACTION,
                severity="warning",
                message=f"Large transaction detected: {transaction.amount} {transaction.currency.value}",
                timestamp=datetime.now(),
                transaction_id=transaction.id,
                account_id=transaction.account_id,
                amount=transaction.amount,
                metadata={'multiplier': float(transaction.amount) / float(self.thresholds['large_transaction_usd'])}
            )
            alerts.append(alert)

        # Check for unusual spending patterns
        if self._is_unusual_spending(transaction):
            alert = FinancialAlert(
                id=f"alert_unusual_{transaction.id}",
                type=AlertType.UNUSUAL_SPENDING,
                severity="warning",
                message=f"Unusual spending pattern detected for account {transaction.account_id}",
                timestamp=datetime.now(),
                transaction_id=transaction.id,
                account_id=transaction.account_id,
                amount=transaction.amount,
                metadata={'category': transaction.category.value, 'merchant': transaction.merchant}
            )
            alerts.append(alert)

        # Check for fraud suspicion (simplified pattern)
        if self._is_fraud_suspicion(transaction):
            alert = FinancialAlert(
                id=f"alert_fraud_{transaction.id}",
                type=AlertType.FRAUD_SUSPICION,
                severity="critical",
                message=f"Potential fraud detected: {transaction.amount} {transaction.currency.value}",
                timestamp=datetime.now(),
                transaction_id=transaction.id,
                account_id=transaction.account_id,
                amount=transaction.amount,
                metadata={'description': transaction.description, 'merchant': transaction.merchant}
            )
            alerts.append(alert)

        # Check for budget exceeded
        if self._is_budget_exceeded(transaction):
            alert = FinancialAlert(
                id=f"alert_budget_{transaction.id}",
                type=AlertType.BUDGET_EXCEEDED,
                severity="info",
                message=f"Budget may be exceeded for category {transaction.category.value}",
                timestamp=datetime.now(),
                transaction_id=transaction.id,
                account_id=transaction.account_id,
                amount=transaction.amount,
                metadata={'category': transaction.category.value}
            )
            alerts.append(alert)

        return alerts

    def _is_large_transaction(self, transaction: FinancialTransaction) -> bool:
        """Check if transaction is considered large"""
        # Convert to USD for comparison if needed
        usd_amount = self._convert_to_usd(transaction.amount, transaction.currency)
        return usd_amount >= self.thresholds['large_transaction_usd']

    def _is_unusual_spending(self, transaction: FinancialTransaction) -> bool:
        """Check if transaction represents unusual spending"""
        account_id = transaction.account_id
        if account_id not in self.patterns['usual_merchants']:
            return False

        # Check if merchant is unusual
        usual_merchants = self.patterns['usual_merchants'][account_id]
        if transaction.merchant not in usual_merchants:
            return True

        # Check if category is unusual
        usual_categories = self.patterns['usual_categories'][account_id]
        if transaction.category not in usual_categories:
            return True

        # Check if amount is unusual
        min_amount, max_amount = self.patterns['usual_amount_ranges'][account_id]
        multiplier_decimal = Decimal(str(self.thresholds['unusual_spending_multiplier']))
        if transaction.amount < min_amount or transaction.amount > max_amount * multiplier_decimal:
            return True

        return False

    def _is_fraud_suspicion(self, transaction: FinancialTransaction) -> bool:
        """Check if transaction might be fraudulent"""
        # Simplified fraud detection - check for very large amounts
        usd_amount = self._convert_to_usd(transaction.amount, transaction.currency)
        if usd_amount >= self.thresholds['fraud_suspicion_amount_usd']:
            # Additional checks could be added here
            if transaction.merchant == "UNKNOWN" or not transaction.merchant.strip():
                return True
        return False

    def _is_budget_exceeded(self, transaction: FinancialTransaction) -> bool:
        """Check if transaction exceeds budget"""
        category_budget_key = f"{transaction.account_id}:{transaction.category.value}"
        if category_budget_key in self.budgets:
            # This would require tracking category spending
            # For now, just return False - would need more complex budget tracking
            return False
        return False

    def _convert_to_usd(self, amount: Decimal, currency: Currency) -> Decimal:
        """Convert amount to USD using exchange rates"""
        if currency == Currency.USD:
            return amount

        # Simplified conversion - in real implementation, would fetch real rates
        conversion_rates = {
            Currency.EUR: Decimal('1.1'),  # Example rates
            Currency.GBP: Decimal('1.25'),
            Currency.JPY: Decimal('0.009'),
            Currency.CAD: Decimal('0.75'),
            Currency.AUD: Decimal('0.65'),
            Currency.CHF: Decimal('1.15'),
            Currency.CNY: Decimal('0.15'),
            Currency.INR: Decimal('0.012'),
            Currency.BRL: Decimal('0.18')
        }

        rate = conversion_rates.get(currency, Decimal('1.0'))
        return amount * rate

    def set_budget(self, account_id: str, category: TransactionCategory, limit: Decimal):
        """Set a budget limit for a category in an account"""
        budget_key = f"{account_id}:{category.value}"
        self.budgets[budget_key] = limit
        self.logger.info(f"Budget set for {account_id}:{category.value} = {limit}")

    def get_account_summary(self, account_id: str, period_days: int = 30) -> Optional[Dict[str, Any]]:
        """Get summary of transactions for an account over a period"""
        if account_id not in self.accounts:
            return None

        period_start = datetime.now() - timedelta(days=period_days)
        account_transactions = [
            t for t in self.transactions.values()
            if t.account_id == account_id and t.timestamp >= period_start
        ]

        total_income = Decimal('0')
        total_expenses = Decimal('0')
        income_by_category = {}
        expenses_by_category = {}

        for transaction in account_transactions:
            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount
                cat = transaction.category.value
                income_by_category[cat] = income_by_category.get(cat, Decimal('0')) + transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                total_expenses += transaction.amount
                cat = transaction.category.value
                expenses_by_category[cat] = expenses_by_category.get(cat, Decimal('0')) + transaction.amount

        summary = {
            'account_id': account_id,
            'period_start': period_start.isoformat(),
            'period_end': datetime.now().isoformat(),
            'total_income': str(total_income),
            'total_expenses': str(total_expenses),
            'net_flow': str(total_income - total_expenses),
            'transaction_count': len(account_transactions),
            'income_by_category': {k: str(v) for k, v in income_by_category.items()},
            'expenses_by_category': {k: str(v) for k, v in expenses_by_category.items()},
        }

        return summary

    def generate_financial_summary(self, period_days: int = 30) -> FinancialSummary:
        """Generate a comprehensive financial summary"""
        period_start = datetime.now() - timedelta(days=period_days)
        period_end = datetime.now()

        transactions_in_period = [
            t for t in self.transactions.values()
            if t.timestamp >= period_start
        ]

        total_income = Decimal('0')
        total_expenses = Decimal('0')
        income_by_category = {}
        expenses_by_category = {}
        income_by_account = {}
        expenses_by_account = {}

        for transaction in transactions_in_period:
            if transaction.transaction_type == TransactionType.INCOME:
                total_income += transaction.amount
                # Category tracking
                cat = transaction.category.value
                income_by_category[cat] = income_by_category.get(cat, Decimal('0')) + transaction.amount
                # Account tracking
                acc = transaction.account_id
                income_by_account[acc] = income_by_account.get(acc, Decimal('0')) + transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                total_expenses += transaction.amount
                # Category tracking
                cat = transaction.category.value
                expenses_by_category[cat] = expenses_by_category.get(cat, Decimal('0')) + transaction.amount
                # Account tracking
                acc = transaction.account_id
                expenses_by_account[acc] = expenses_by_account.get(acc, Decimal('0')) + transaction.amount

        summary = FinancialSummary(
            period_start=period_start,
            period_end=period_end,
            total_income=total_income,
            total_expenses=total_expenses,
            net_flow=total_income - total_expenses,
            income_by_category={TransactionCategory(k): v for k, v in income_by_category.items()},
            expenses_by_category={TransactionCategory(k): v for k, v in expenses_by_category.items()},
            income_by_account=income_by_account,
            expenses_by_account=expenses_by_account,
            transaction_count=len(transactions_in_period),
            alerts_generated=len([a for a in self.alerts if a.timestamp >= period_start])
        )

        # Save summary to file
        self._save_financial_summary(summary)

        return summary

    def _save_financial_summary(self, summary: FinancialSummary):
        """Save financial summary to file"""
        summary_data = {
            'period_start': summary.period_start.isoformat(),
            'period_end': summary.period_end.isoformat(),
            'total_income': str(summary.total_income),
            'total_expenses': str(summary.total_expenses),
            'net_flow': str(summary.net_flow),
            'income_by_category': {k.value: str(v) for k, v in summary.income_by_category.items()},
            'expenses_by_category': {k.value: str(v) for k, v in summary.expenses_by_category.items()},
            'income_by_account': {k: str(v) for k, v in summary.income_by_account.items()},
            'expenses_by_account': {k: str(v) for k, v in summary.expenses_by_account.items()},
            'transaction_count': summary.transaction_count,
            'alerts_generated': summary.alerts_generated,
            'generated_at': datetime.now().isoformat()
        }

        filename = self.reports_dir / f"financial_summary_{summary.period_start.strftime('%Y%m%d')}_{summary.period_end.strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(summary_data, f, indent=2)

    def _log_transaction(self, transaction: FinancialTransaction):
        """Log transaction to file"""
        transaction_data = {
            'id': transaction.id,
            'account_id': transaction.account_id,
            'amount': str(transaction.amount),
            'currency': transaction.currency.value,
            'type': transaction.transaction_type.value,
            'category': transaction.category.value,
            'description': transaction.description,
            'merchant': transaction.merchant,
            'timestamp': transaction.timestamp.isoformat(),
            'location': transaction.location,
            'tags': transaction.tags,
            'status': transaction.status
        }

        log_file = self.financial_logs_dir / f"transactions_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(transaction_data) + '\n')

    def _log_alert(self, alert: FinancialAlert):
        """Log alert to file"""
        alert_data = {
            'id': alert.id,
            'type': alert.type.value,
            'severity': alert.severity,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'transaction_id': alert.transaction_id,
            'account_id': alert.account_id,
            'amount': str(alert.amount) if alert.amount else None
        }

        log_file = self.financial_logs_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(alert_data) + '\n')

    def get_alerts(self, limit: int = 100, severity: Optional[str] = None) -> List[FinancialAlert]:
        """Get recent alerts, optionally filtered by severity"""
        alerts = self.alerts
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return alerts[-limit:]

    def categorize_transaction(self, transaction_id: str, category: TransactionCategory) -> bool:
        """Manually categorize a transaction"""
        if transaction_id not in self.transactions:
            return False

        self.transactions[transaction_id].category = category
        self.logger.info(f"Transaction {transaction_id} recategorized as {category.value}")
        return True

    def get_spending_patterns(self, account_id: str, category: Optional[TransactionCategory] = None) -> Dict[str, Any]:
        """Analyze spending patterns for an account"""
        if account_id not in self.accounts:
            return {}

        account_transactions = [
            t for t in self.transactions.values()
            if t.account_id == account_id and t.transaction_type == TransactionType.EXPENSE
        ]

        if category:
            account_transactions = [t for t in account_transactions if t.category == category]

        # Group by time periods and calculate averages
        daily_spending = {}
        weekly_spending = {}

        for transaction in account_transactions:
            day_key = transaction.timestamp.strftime('%Y-%m-%d')
            week_key = transaction.timestamp.strftime('%Y-W%U')

            daily_spending[day_key] = daily_spending.get(day_key, Decimal('0')) + transaction.amount
            weekly_spending[week_key] = weekly_spending.get(week_key, Decimal('0')) + transaction.amount

        return {
            'account_id': account_id,
            'category': category.value if category else 'all',
            'daily_spending': {k: str(v) for k, v in daily_spending.items()},
            'weekly_spending': {k: str(v) for k, v in weekly_spending.items()},
            'total_transactions': len(account_transactions),
            'total_spending': str(sum(t.amount for t in account_transactions)),
            'average_daily_spending': str(sum(daily_spending.values()) / len(daily_spending)) if daily_spending else '0'
        }

    def start_monitoring(self, check_interval: int = 60):
        """Start continuous monitoring loop"""
        self.logger.info(f"Starting financial monitoring with {check_interval}s interval")

        try:
            while True:
                # In a real implementation, this would check for new transactions
                # from connected financial services and APIs
                self.logger.debug("Checking for new transactions...")

                # Generate periodic reports
                if datetime.now().hour == 23 and datetime.now().minute == 0:  # Daily at 11 PM
                    self.generate_financial_summary(period_days=1)
                    self.logger.info("Daily financial summary generated")

                # Clean up old data periodically
                if datetime.now().minute % 10 == 0:  # Every 10 minutes
                    self._cleanup_old_data()

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info("Financial monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            raise

    def _cleanup_old_data(self):
        """Clean up old financial data based on retention policy"""
        retention_days = self.config.get('data_retention_days', 365)
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        # Clean up old transactions
        self.transactions = {
            tid: t for tid, t in self.transactions.items()
            if t.timestamp >= cutoff_date
        }

        # Clean up old alerts
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff_date]

        self.logger.debug(f"Cleaned up data older than {cutoff_date}")


if __name__ == "__main__":
    # Example usage
    watcher = FinanceWatcher()

    # Add some accounts
    watcher.add_account("account_1", "Business Checking", Decimal('10000'), Currency.USD)
    watcher.add_account("account_2", "Personal Savings", Decimal('5000'), Currency.USD)

    # Set some budgets
    watcher.set_budget("account_1", TransactionCategory.BUSINESS, Decimal('5000'))
    watcher.set_budget("account_1", TransactionCategory.ENTERTAINMENT, Decimal('500'))

    # Create some sample transactions
    transactions = [
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="account_1",
            amount=Decimal('1250.75'),
            currency=Currency.USD,
            transaction_type=TransactionType.INCOME,
            category=TransactionCategory.SALARY,
            description="Monthly salary deposit",
            merchant="Company Payroll",
            timestamp=datetime.now() - timedelta(days=1)
        ),
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="account_1",
            amount=Decimal('45.30'),
            currency=Currency.USD,
            transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.FOOD,
            description="Lunch at restaurant",
            merchant="Local Diner",
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="account_1",
            amount=Decimal('2500.00'),
            currency=Currency.USD,
            transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.BUSINESS,
            description="Office equipment purchase",
            merchant="Office Supplies Inc",
            timestamp=datetime.now() - timedelta(minutes=30)
        ),
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="account_2",
            amount=Decimal('120.50'),
            currency=Currency.USD,
            transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.ENTERTAINMENT,
            description="Movie tickets",
            merchant="Cinema Complex",
            timestamp=datetime.now()
        )
    ]

    # Record transactions
    for tx in transactions:
        watcher.record_transaction(tx)

    # Get account summary
    summary = watcher.get_account_summary("account_1")
    print("Account 1 Summary:", json.dumps(summary, indent=2))

    # Generate financial summary
    fin_summary = watcher.generate_financial_summary()
    print(f"\nGenerated financial summary:")
    print(f"Total Income: ${fin_summary.total_income}")
    print(f"Total Expenses: ${fin_summary.total_expenses}")
    print(f"Net Flow: ${fin_summary.net_flow}")
    print(f"Transaction Count: {fin_summary.transaction_count}")

    # Get alerts
    alerts = watcher.get_alerts(severity="warning")
    print(f"\nWarnings found: {len(alerts)}")

    # Get spending patterns
    patterns = watcher.get_spending_patterns("account_1")
    print(f"\nSpending patterns for account 1:")
    print(f"Total transactions: {patterns['total_transactions']}")
    print(f"Total spending: ${patterns['total_spending']}")
    print(f"Average daily spending: ${patterns['average_daily_spending']}")