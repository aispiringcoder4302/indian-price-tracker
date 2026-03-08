"""
Playwright-based Web Scraper for Indian E-Commerce
Handles JavaScript rendering and bypasses basic anti-bot measures
"""

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import asyncio
import random
import re
from datetime import datetime
from typing import Optional, Dict

class PlaywrightScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    async def setup(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()
        
        # Launch Chromium with anti-detection flags
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        # Create context with random viewport and user agent
        self.context = await self.browser.new_context(
            viewport={
                'width': random.choice([1920, 1366, 1440]),
                'height': random.choice([1080, 768, 900])
            },
            user_agent=random.choice(self.user_agents),
            locale='en-IN',
            timezone_id='Asia/Kolkata'
        )
        
        # Override navigator.webdriver
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
    
    async def close(self):
        """Close browser and Playwright"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def clean_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        # Remove all non-numeric characters except decimal point
        price = re.sub(r'[^\d.]', '', price_text)
        try:
            return float(price) if price else None
        except:
            return None
    
    async def scrape_amazon(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Amazon.in using Playwright"""
        page = None
        try:
            page = await self.context.new_page()
            
            # Navigate with timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for price element with multiple selectors
            price = None
            selectors = [
                '.a-price-whole',
                '#priceblock_dealprice',
                '#priceblock_ourprice',
                '.a-price .a-offscreen',
                '#price_inside_buybox'
            ]
            
            for selector in selectors:
                try:
                    elem = await page.wait_for_selector(selector, timeout=5000)
                    if elem:
                        price_text = await elem.inner_text()
                        price = self.clean_price(price_text)
                        if price and price > 100:  # Reasonable price check
                            break
                except PlaywrightTimeout:
                    continue
            
            # Fallback: search in page content
            if not price:
                content = await page.content()
                price_match = re.search(r'₹\s*([\d,]+)', content)
                if price_match:
                    price = self.clean_price(price_match.group(1))
            
            await page.close()
            
            return {
                'product': product_name,
                'platform': 'Amazon',
                'price': price,
                'url': url,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': '₹',
                'method': 'playwright'
            }
            
        except Exception as e:
            if page:
                await page.close()
            return {
                'product': product_name,
                'platform': 'Amazon',
                'price': None,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def scrape_flipkart(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Flipkart using Playwright"""
        page = None
        try:
            page = await self.context.new_page()
            
            # Navigate with timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Try multiple selectors
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
                try:
                    elem = await page.wait_for_selector(selector, timeout=3000)
                    if elem:
                        price_text = await elem.inner_text()
                        price = self.clean_price(price_text)
                        if price and price > 100:
                            break
                except PlaywrightTimeout:
                    continue
            
            # Fallback: search in page content
            if not price:
                content = await page.content()
                price_match = re.search(r'₹\s*([\d,]+)', content)
                if price_match:
                    price = self.clean_price(price_match.group(1))
            
            await page.close()
            
            return {
                'product': product_name,
                'platform': 'Flipkart',
                'price': price,
                'url': url,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': '₹',
                'method': 'playwright'
            }
            
        except Exception as e:
            if page:
                await page.close()
            return {
                'product': product_name,
                'platform': 'Flipkart',
                'price': None,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def scrape_meesho(self, url: str, product_name: str) -> Optional[Dict]:
        """Scrape price from Meesho using Playwright"""
        page = None
        try:
            page = await self.context.new_page()
            
            # Navigate with timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for content
            await page.wait_for_timeout(2000)
            
            # Try multiple selectors
            price = None
            selectors = [
                'span.sc-eDvSVe',
                'h4.sc-eDvSVe',
                'span[class*="price"]',
                'div[class*="price"]'
            ]
            
            for selector in selectors:
                try:
                    elem = await page.wait_for_selector(selector, timeout=3000)
                    if elem:
                        price_text = await elem.inner_text()
                        price = self.clean_price(price_text)
                        if price and price > 100:
                            break
                except PlaywrightTimeout:
                    continue
            
            # Fallback: search in page content
            if not price:
                content = await page.content()
                price_match = re.search(r'₹\s*([\d,]+)', content)
                if price_match:
                    price = self.clean_price(price_match.group(1))
            
            await page.close()
            
            return {
                'product': product_name,
                'platform': 'Meesho',
                'price': price,
                'url': url,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'currency': '₹',
                'method': 'playwright'
            }
            
        except Exception as e:
            if page:
                await page.close()
            return {
                'product': product_name,
                'platform': 'Meesho',
                'price': None,
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

# Async wrapper for synchronous usage
def scrape_with_playwright(url: str, platform: str, product_name: str) -> Optional[Dict]:
    """Synchronous wrapper for async scraping"""
    async def _scrape():
        scraper = PlaywrightScraper()
        try:
            await scraper.setup()
            
            if 'amazon' in platform.lower():
                result = await scraper.scrape_amazon(url, product_name)
            elif 'flipkart' in platform.lower():
                result = await scraper.scrape_flipkart(url, product_name)
            elif 'meesho' in platform.lower():
                result = await scraper.scrape_meesho(url, product_name)
            else:
                result = None
            
            await scraper.close()
            return result
        except Exception as e:
            await scraper.close()
            return {
                'product': product_name,
                'platform': platform,
                'price': None,
                'error': str(e)
            }
    
    return asyncio.run(_scrape())
