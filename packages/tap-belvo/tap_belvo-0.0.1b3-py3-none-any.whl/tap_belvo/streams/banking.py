"""Stream type classes for tap-belvo."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tap_belvo.client import BelvoStream
from tap_belvo.streams.links import Links

if TYPE_CHECKING:
    from urllib.parse import ParseResult


class Accounts(BelvoStream):
    """Accounts stream."""

    name = "banking_accounts"
    path = "/api/accounts"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "Account"


class Transactions(BelvoStream):
    """Transactions stream."""

    name = "banking_transactions"
    path = "/api/transactions"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "Account"
    parent_stream_type = Links

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next page URL, if available.

        Returns:
            Mapping of URL query parameters.
        """
        params = super().get_url_params(context, next_page_token)

        if context is not None:
            params["link"] = context["link_id"]

        return params


class Balances(BelvoStream):
    """Balances stream."""

    name = "banking_balances"
    path = "/api/balances"
    primary_keys = ["id"]
    replication_key = "value_date"
    openapi_ref = "Balance"


class Owners(BelvoStream):
    """Owners stream."""

    name = "banking_owners"
    path = "/api/owners"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "Owner"


class InvestmentPortfolios(BelvoStream):
    """Portfolios stream."""

    name = "investment_portfolios"
    path = "/investments/portfolios"
    primary_keys = ["id"]
    replication_key = None
    openapi_ref = "InvestmentsPortfolio"


class InvestmentTransactions(BelvoStream):
    """Investment transactions stream."""

    name = "investment_transactions"
    path = "/investments/transactions"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "InvestmentsInstrumentTransaction"


class ReceivableTransactions(BelvoStream):
    """Receivable transactions stream."""

    name = "receivable_transactions"
    path = "/receivables/transactions"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "ReceivablesTransaction"
