#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Price Tracker for Indian E-Commerce
Tracks prices from Amazon.in, Flipkart, and Meesho
With retry logic, rate limiting, and SQLite integration
"""

import logging
import re
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from config import (
    MAX_RETRIES,
    RATE_LIMIT_DELAY,
    TIMEOUT,
    USER_AGENT,
)
from core.database import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries: int = 3):
    """Decorator for retry logic with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Optional[Dict]:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except requests.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * RATE_LIMIT_DELAY
                        logger.warning(
                            "%s failed (attempt %d/%d): %s. Retrying in %.1fs",
                            func.__name__, attempt + 1, max_retries, e, wait_time
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            "%s failed after %d attempts: %s",
                            func.__name__, max_retries, e
                        )
                except Exception as e:
                    logger.exception("Unexpected error in %s: %s", func.__name__, e)
                    return None
            return None
        return wrapper
    return decorator


class PriceTracker:
    """Enhanced price tracker with retry, rate limiting, and database integration."""

    def __init__(self, database: Optional[Database] = None):
        self.db = database or Database()
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.results: List[Dict] = []
        self._last_request_time: float = 0

    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            sleep_time = RATE_LIMIT_DELAY - elapsed
            logger.debug("Rate limiting: sleeping %.1fs", sleep_time)
            time.sleep(sleep_time)
        self._last_request_time = time.time()

    def clean_price(self, price_text: Optional[str]) -> Optional[float]:
        """Extract numeric price from text."""
        if not price_text:
            return None
        price = re.sub(r'[^\d.]', '', price_text)
        try:
            return float(price) if price else None
        except (ValueError, TypeError):
            return None

    @retry_with_backoff(max_retries=MAX_RETRIES)
    def scrape_amazon(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Amazon.in."""
        self._rate_limit()
        response = self.session.get(url, timeout=TIMEOUT)
        logger.debug("Amazon response status: %d", response.status_code)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        price = None
        selectors = [
            'span.a-price-whole',
            'span#priceblock_dealprice',
            'span#priceblock_ourprice',
            'span.a-price span.a-offscreen',
            'span#price_inside_buybox',
            'span.a-price.aok-align-center span.a-offscreen'
        ]

        for selector in selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price = self.clean_price(price_elem.text)
                if price:
                    break

        if not price:
            all_prices = soup.find_all('span', class_=re.compile('a-price'))
            for price_elem in all_prices[:3]:
                price = self.clean_price(price_elem.text)
                if price and price > 100:
                    break

        return {
            'product': product_name,
            'platform': 'Amazon',
            'price': price,
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'currency': '₹'
        }

    @retry_with_backoff(max_retries=MAX_RETRIES)
    def scrape_flipkart(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Flipkart."""
        self._rate_limit()
        response = self.session.get(url, timeout=TIMEOUT)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        price = None
        selectors = [
            'div._30jeq3._16Jk6d',
            'div._30jeq3',
            'div._25b18c div._30jeq3',
            'div._16Jk6d',
            'div.Nx9bqj.CxhGGd',
            'div._30jeq3._1_WHN1'
        ]

        for selector in selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price = self.clean_price(price_elem.text)
                if price:
                    break

        if not price:
            all_text = soup.get_text()
            price_match = re.search(r'₹\s*([\d,]+)', all_text)
            if price_match:
                price = self.clean_price(price_match.group(1))

        return {
            'product': product_name,
            'platform': 'Flipkart',
            'price': price,
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'currency': '₹'
        }

    @retry_with_backoff(max_retries=MAX_RETRIES)
    def scrape_meesho(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Meesho."""
        self._rate_limit()
        response = self.session.get(url, timeout=TIMEOUT)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        price = None
        selectors = [
            'span.sc-eDvSVe',
            'h4.sc-eDvSVe',
            'span[class*="price"]'
        ]

        for selector in selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price = self.clean_price(price_elem.text)
                if price:
                    break

        return {
            'product': product_name,
            'platform': 'Meesho',
            'price': price,
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'currency': '₹'
        }

    def _scrape_platform(self, platform: str, url: str, product_name: str) -> Optional[Dict]:
        """Route to the appropriate scraper based on platform."""
        platform_lower = platform.lower()
        if 'amazon' in platform_lower:
            return self.scrape_amazon(url, product_name)
        if 'flipkart' in platform_lower:
            return self.scrape_flipkart(url, product_name)
        if 'meesho' in platform_lower:
            return self.scrape_meesho(url, product_name)
        logger.warning("Unknown platform: %s", platform)
        return None

    def track_product(
        self,
        product_config: Dict,
        product_id: Optional[int] = None,
        save_to_db: bool = True
    ) -> List[Dict]:
        """Track a single product across platforms."""
        product_name = product_config['name']
        threshold = product_config.get('threshold', 0)
        urls = product_config.get('urls', {})

        logger.info("Tracking: %s (threshold: ₹%s)", product_name, threshold)
        product_results = []

        for platform, url in urls.items():
            if not url:
                continue

            logger.info("Checking %s...", platform)
            result = self._scrape_platform(platform, url, product_name)

            if result and result.get('price') is not None:
                price = result['price']
                result['below_threshold'] = price <= threshold if threshold > 0 else False
                result['product_id'] = product_id
                self.results.append(result)
                product_results.append(result)

                if save_to_db and product_id:
                    self.db.add_price_record(
                        product_id=product_id,
                        platform=result['platform'],
                        price=price,
                        available=True
                    )

                status = "DEAL!" if result['below_threshold'] else "OK"
                logger.info("%s ₹%.2f [%s]", status, price, platform)
            else:
                logger.warning("Could not fetch price from %s", platform)
                if save_to_db and product_id:
                    self.db.add_price_record(
                        product_id=product_id,
                        platform=platform,
                        price=None,
                        available=False
                    )

        return product_results

    def track_all_products(self, active_only: bool = True) -> Dict[str, Any]:
        """
        Track all products from the database.
        Returns summary statistics.
        """
        products = self.db.get_all_products(active_only=active_only)
        self.results = []

        if not products:
            logger.warning("No products to track")
            return self._get_summary_stats()

        logger.info("Tracking %d product(s) from database", len(products))

        for product in products:
            product_config = {
                'name': product['name'],
                'threshold': product['threshold'],
                'urls': {
                    'amazon': product.get('amazon_url') or '',
                    'flipkart': product.get('flipkart_url') or '',
                    'meesho': product.get('meesho_url') or ''
                }
            }
            self.track_product(product_config, product_id=product['id'], save_to_db=True)

        return self._get_summary_stats()

    def _get_summary_stats(self) -> Dict[str, Any]:
        """Compute and return summary statistics."""
        total = len(self.results)
        successful = len([r for r in self.results if r.get('price') is not None])
        failed = total - successful
        deals = len([r for r in self.results if r.get('below_threshold', False)])

        platforms: Dict[str, List[Dict]] = {}
        for r in self.results:
            if r.get('price') is not None:
                platform = r['platform']
                platforms.setdefault(platform, []).append(r)

        platform_summary = {}
        for platform, items in platforms.items():
            prices = [item['price'] for item in items]
            platform_summary[platform] = {
                'count': len(items),
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
            }

        return {
            'total_checks': total,
            'successful': successful,
            'failed': failed,
            'deals_found': deals,
            'platform_summary': platform_summary,
            'results': self.results,
        }

    def run(self) -> Dict[str, Any]:
        """Main execution: track all products from database and return summary."""
        logger.info("Starting Price Tracker at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        stats = self.track_all_products()
        logger.info("Price tracking completed. Stats: %s", stats)
        return stats


if __name__ == "__main__":
    tracker = PriceTracker()
    stats = tracker.run()
    print("\n📊 Summary:", stats)
