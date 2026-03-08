"""
Google Sheets Export Integration for Indian Price Tracker
Exports products, price history, and deals to formatted Google Sheets
"""

import time
import logging
from typing import List, Dict, Any, Optional, Tuple

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import config

logger = logging.getLogger(__name__)

# API rate limit handling
MAX_RETRIES = 5
RETRY_DELAY = 60  # seconds
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class SheetsExporter:
    """Export tracker data to Google Sheets with formatting."""

    def __init__(self):
        self.client: Optional[gspread.Client] = None
        self.spreadsheet = None

    def authenticate(self) -> Tuple[bool, str]:
        """
        Authenticate using service account credentials.
        Returns (success, message).
        """
        if not config.SHEETS_CREDENTIALS:
            return False, "SHEETS_CREDENTIALS not configured"
        if not config.SHEETS_ENABLED:
            return False, "Sheets export is disabled"

        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                config.SHEETS_CREDENTIALS,
                SCOPES
            )
            self.client = gspread.authorize(credentials)
            return True, "Authentication successful"
        except Exception as e:
            logger.exception("Sheets authentication failed")
            return False, str(e)

    def _get_or_create_spreadsheet(self) -> Optional[gspread.Spreadsheet]:
        """Get existing spreadsheet or create new one."""
        if not self.client:
            return None
        try:
            spreadsheet = self.client.open(config.SHEETS_NAME)
            return spreadsheet
        except gspread.SpreadsheetNotFound:
            try:
                spreadsheet = self.client.create(config.SHEETS_NAME)
                return spreadsheet
            except Exception as e:
                logger.exception("Failed to create spreadsheet")
                raise e

    def _api_call_with_retry(self, func, *args, **kwargs) -> Any:
        """Execute API call with retry on rate limit errors."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                last_error = e
                status = getattr(getattr(e, 'response', None), 'status_code', None)
                if status == 429:
                    wait_time = RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"API rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                raise
        raise last_error

    def _format_header_row(self, worksheet: gspread.Worksheet, num_cols: int):
        """Format header row with background color and bold."""
        header_range = worksheet.range(1, 1, 1, num_cols)
        for cell in header_range:
            cell.format = {
                "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            }
        worksheet.update_cells(header_range)

    def _get_or_add_worksheet(self, spreadsheet: gspread.Spreadsheet, title: str, rows: int = 500, cols: int = 10) -> gspread.Worksheet:
        """Get worksheet by title or create if not exists."""
        try:
            return self._api_call_with_retry(lambda: spreadsheet.worksheet(title))
        except gspread.WorksheetNotFound:
            return self._api_call_with_retry(lambda: spreadsheet.add_worksheet(title, rows=rows, cols=cols))

    def export_products(self, products_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Export products to Sheet 1: Products.
        Expected keys: id, name, threshold, amazon_url, flipkart_url, meesho_url, active
        """
        if not self.client:
            auth_ok, msg = self.authenticate()
            if not auth_ok:
                return False, msg

        try:
            spreadsheet = self._get_or_create_spreadsheet()
            worksheet = self._get_or_add_worksheet(spreadsheet, "Products", rows=500, cols=10)
        except Exception as e:
            logger.exception("Failed to get Products worksheet")
            return False, str(e)

        headers = ["ID", "Name", "Threshold (₹)", "Amazon URL", "Flipkart URL", "Meesho URL", "Active"]
        rows = [headers]

        for p in products_data:
            rows.append([
                p.get("id", ""),
                p.get("name", ""),
                p.get("threshold", ""),
                p.get("amazon_url", ""),
                p.get("flipkart_url", ""),
                p.get("meesho_url", ""),
                "Yes" if p.get("active", True) else "No"
            ])

        try:
            self._api_call_with_retry(lambda: worksheet.update(rows, value_input_option="USER_ENTERED"))
            self._format_header_row(worksheet, len(headers))
            try:
                self._api_call_with_retry(lambda: worksheet.columns_auto_resize(0, len(headers) - 1))
            except (AttributeError, TypeError):
                pass  # columns_auto_resize may not exist in all gspread versions
        except Exception as e:
            logger.exception("Export products failed")
            return False, str(e)

        return True, f"Exported {len(products_data)} products"

    def export_price_history(self, history_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Export price history to Sheet 2: Price History.
        Expected keys: product_id, platform, price, original_price, discount_percent, below_threshold, timestamp
        """
        if not self.client:
            auth_ok, msg = self.authenticate()
            if not auth_ok:
                return False, msg

        try:
            spreadsheet = self._get_or_create_spreadsheet()
            worksheet = self._get_or_add_worksheet(spreadsheet, "Price History", rows=1000, cols=10)
        except Exception as e:
            logger.exception("Failed to get Price History worksheet")
            return False, str(e)

        headers = ["ID", "Product ID", "Platform", "Price (₹)", "Original (₹)", "Discount %", "Below Threshold", "Timestamp"]
        rows = [headers]

        for h in history_data:
            rows.append([
                h.get("id", ""),
                h.get("product_id", ""),
                h.get("platform", ""),
                h.get("price", ""),
                h.get("original_price", ""),
                h.get("discount_percent", ""),
                "Yes" if h.get("below_threshold") else "No",
                str(h.get("timestamp", ""))
            ])

        try:
            self._api_call_with_retry(lambda: worksheet.update(rows, value_input_option="USER_ENTERED"))
            self._format_header_row(worksheet, len(headers))
            try:
                self._api_call_with_retry(lambda: worksheet.columns_auto_resize(0, len(headers) - 1))
            except (AttributeError, TypeError):
                pass
        except Exception as e:
            logger.exception("Export price history failed")
            return False, str(e)

        return True, f"Exported {len(history_data)} price records"

    def export_deals(self, deals_data: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Export hot deals to Sheet 3: Hot Deals.
        Expected keys: name, platform, price, original_price, discount_percent, threshold, timestamp
        """
        if not self.client:
            auth_ok, msg = self.authenticate()
            if not auth_ok:
                return False, msg

        try:
            spreadsheet = self._get_or_create_spreadsheet()
            worksheet = self._get_or_add_worksheet(spreadsheet, "Hot Deals", rows=200, cols=10)
        except Exception as e:
            logger.exception("Failed to get Hot Deals worksheet")
            return False, str(e)

        headers = ["Product", "Platform", "Price (₹)", "Original (₹)", "Discount %", "Threshold (₹)", "Saved (₹)", "Timestamp"]
        rows = [headers]

        for i, d in enumerate(deals_data):
            row_num = i + 2  # 1-based, row 1 is header
            # Use formula for Saved: =D{row}-C{row} (Original - Price)
            saved_formula = f"=IF(AND(D{row_num}>0,C{row_num}>0),D{row_num}-C{row_num},\"\")"
            rows.append([
                d.get("name", ""),
                d.get("platform", ""),
                d.get("price", ""),
                d.get("original_price", ""),
                d.get("discount_percent", ""),
                d.get("threshold", ""),
                saved_formula,
                str(d.get("timestamp", ""))
            ])

        try:
            self._api_call_with_retry(lambda: worksheet.update(rows, value_input_option="USER_ENTERED"))
            self._format_header_row(worksheet, len(headers))
            try:
                self._api_call_with_retry(lambda: worksheet.columns_auto_resize(0, len(headers) - 1))
            except (AttributeError, TypeError):
                pass
        except Exception as e:
            logger.exception("Export deals failed")
            return False, str(e)

        # Add conditional formatting for discount column (highlight high discounts)
        if len(rows) > 1:
            discount_col = 5  # E column (1-indexed in gspread)
            try:
                worksheet.format(f"E2:E{len(rows)}", {
                    "backgroundColor": {"red": 0.9, "green": 1, "blue": 0.9}
                })
            except Exception:
                pass  # Formatting is best-effort

        return True, f"Exported {len(deals_data)} deals"
