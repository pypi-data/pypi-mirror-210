"""Stream classes for tap-belvo."""

from __future__ import annotations

from tap_belvo.streams.banking import (
    Accounts,
    Balances,
    InvestmentPortfolios,
    InvestmentTransactions,
    Owners,
    ReceivableTransactions,
    Transactions,
)
from tap_belvo.streams.enrichment import Incomes, RecurringExpenses, RiskInsights
from tap_belvo.streams.fiscal import (
    Invoices,
    TaxComplianceStatuses,
    TaxDeclarations,
    TaxRetentions,
    TaxReturns,
    TaxStatuses,
)
from tap_belvo.streams.links import Institutions, Links

__all__ = [
    "Links",
    "Institutions",
    "Accounts",
    "Transactions",
    "Balances",
    "Owners",
    "InvestmentPortfolios",
    "InvestmentTransactions",
    "ReceivableTransactions",
    "Incomes",
    "RecurringExpenses",
    "RiskInsights",
    "Invoices",
    "TaxComplianceStatuses",
    "TaxDeclarations",
    "TaxRetentions",
    "TaxReturns",
    "TaxStatuses",
]
