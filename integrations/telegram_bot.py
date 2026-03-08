"""
Telegram notification integration for Indian Price Tracker.
Lightweight send-only: uses Telegram Bot API to send messages.
No webhooks or polling - just outbound notifications.
"""

import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_IDS

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(message: str, parse_mode: str = "HTML") -> bool:
    """
    Send a message to all configured Telegram chat IDs.

    Args:
        message: The text to send.
        parse_mode: Telegram parse mode ('HTML' or 'Markdown'). Default: 'HTML'.

    Returns:
        True if sent to at least one chat, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_IDS:
        return False

    url = TELEGRAM_API_BASE.format(token=TELEGRAM_BOT_TOKEN)
    payload = {"parse_mode": parse_mode, "disable_web_page_preview": True}
    success = False

    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            resp = requests.post(
                url,
                json={"chat_id": chat_id, "text": message, **payload},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and data.get("ok"):
                    success = True
        except (requests.RequestException, ValueError):
            pass

    return success


def send_price_alert(
    product_name: str,
    platform: str,
    old_price: float,
    new_price: float,
    url: str,
    threshold: float,
) -> bool:
    """
    Send a price drop alert notification.

    Args:
        product_name: Name of the product.
        platform: Platform name (e.g. Amazon, Flipkart).
        old_price: Previous price.
        new_price: Current (lower) price.
        url: Product URL.
        threshold: Price drop threshold (e.g. percentage).

    Returns:
        True if sent successfully, False otherwise.
    """
    discount_pct = ((old_price - new_price) / old_price * 100) if old_price else 0
    message = (
        f"<b>Price drop alert</b>\n\n"
        f"<b>{product_name}</b>\n"
        f"Platform: {platform}\n"
        f"Old price: ₹{old_price:,.2f}\n"
        f"New price: ₹{new_price:,.2f}\n"
        f"Saved: {discount_pct:.1f}%\n"
        f"Threshold: {threshold}\n\n"
        f"<a href=\"{url}\">View product</a>"
    )
    return send_telegram_message(message)


def send_deals_summary(deals_list: list) -> bool:
    """
    Send a formatted summary of multiple deals.

    Args:
        deals_list: List of deal dicts with keys like:
            product_name, platform, old_price, new_price, url (optional).

    Returns:
        True if sent successfully, False otherwise.
    """
    if not deals_list:
        return False

    lines = ["<b>Deals summary</b>\n"]
    for i, deal in enumerate(deals_list, 1):
        name = deal.get("product_name", "Unknown")
        platform = deal.get("platform", "Unknown")
        old = deal.get("old_price", 0)
        new = deal.get("new_price", 0)
        url = deal.get("url", "")
        pct = ((old - new) / old * 100) if old else 0
        line = f"{i}. <b>{name}</b> ({platform}) – ₹{new:,.2f} (was ₹{old:,.2f}, -{pct:.1f}%)"
        if url:
            line += f"\n   <a href=\"{url}\">Link</a>"
        lines.append(line)

    message = "\n\n".join(lines)
    return send_telegram_message(message)
