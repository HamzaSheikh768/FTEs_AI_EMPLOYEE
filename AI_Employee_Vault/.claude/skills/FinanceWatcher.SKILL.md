---
name: finance_watcher
description: |
  Monitors financial transactions in real-time, integrates with bank APIs and financial services,
  monitors for unusual transaction patterns, generates alerts for significant financial events,
  tracks and categorizes expenses and revenue, supports multiple currencies and accounts,
  generates financial summary reports.
---

# Finance Watcher

This skill should be used when monitoring financial transactions and activities for the Personal AI Employee system. It provides real-time financial monitoring and analysis capabilities.

## Purpose

Implements comprehensive financial transaction monitoring with the following capabilities:
- Real-time monitoring of financial transactions
- Integration with bank APIs and financial services
- Detection of unusual transaction patterns
- Generation of alerts for significant financial events
- Tracking and categorization of expenses and revenue
- Support for multiple currencies and accounts
- Generation of financial summary reports

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing financial data handling patterns, API integration methods |
| **Conversation** | User's specific requirements for transaction types, alert thresholds |
| **Skill References** | Financial API integration patterns, fraud detection techniques |
| **User Guidelines** | Financial monitoring policies, security requirements |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Real-time Transaction Monitoring
- Monitor financial transactions as they occur
- Process transaction data immediately upon receipt
- Identify transaction types and categories
- Validate transaction authenticity and security

### Financial API Integration
- Connect to bank APIs and financial service providers
- Retrieve transaction history and current activities
- Handle API rate limits and connection issues
- Maintain secure connections to financial services

### Pattern Recognition
- Detect unusual or suspicious transaction patterns
- Identify potential fraudulent activities
- Recognize spending trends and anomalies
- Flag transactions requiring additional review

### Alert Generation
- Generate alerts for significant financial events
- Send notifications for unusual activities
- Create alerts based on user-defined thresholds
- Provide detailed information about flagged transactions

### Transaction Categorization
- Automatically categorize expenses and revenue
- Track spending by category and time period
- Maintain detailed transaction history
- Support for custom categorization rules

### Multi-Currency Support
- Handle transactions in multiple currencies
- Convert currencies using current exchange rates
- Maintain currency-specific financial metrics
- Support for international transaction tracking

## Data Sources Integration

### Financial Service APIs
- Bank account APIs (Chase, Bank of America, etc.)
- Payment processor APIs (PayPal, Stripe, Square)
- Investment account APIs (Robinhood, Fidelity, etc.)
- Cryptocurrency wallet APIs (if applicable)

### Transaction Data
- Account balances and limits
- Transaction history and pending transactions
- Merchant information and categorization data
- Exchange rates and currency conversion data

## Output Format

The skill generates:
- Transaction logs to `/Platinum/Financial_Monitoring/`
- Financial alerts to notification channels
- Categorization reports to `/Platinum/Advanced_Reports/`
- Pattern analysis results to `/Platinum/Advanced_Reports/`

## Error Handling

- If API unavailable: use cached data and retry with exponential backoff
- If transaction invalid: flag for manual review and continue
- If fraud detected: immediately alert and potentially block
- If currency conversion fails: log error and continue with base currency

## Configuration

The skill requires:
- Financial service API credentials and access tokens
- Alert threshold configurations
- Transaction categorization rules
- Currency conversion service access
- User notification preferences