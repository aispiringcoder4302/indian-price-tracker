"""
Unified Notification System for Indian Price Tracker
Handles Email, Telegram, and logging of notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import config
from integrations.telegram_bot import send_price_alert, send_deals_summary
from core.database import db

class NotificationManager:
    def __init__(self):
        self.email_enabled = config.EMAIL_ENABLED
        self.telegram_enabled = config.TELEGRAM_ENABLED
    
    def send_price_drop_alert(self, product: Dict, platform: str, 
                              old_price: float, new_price: float, url: str):
        """Send price drop alert via all enabled channels"""
        success = {}
        
        # Email notification
        if self.email_enabled:
            success['email'] = self._send_email_alert(
                product, platform, old_price, new_price, url
            )
        
        # Telegram notification
        if self.telegram_enabled:
            success['telegram'] = send_price_alert(
                product_name=product['name'],
                platform=platform,
                old_price=old_price,
                new_price=new_price,
                url=url,
                threshold=product['threshold']
            )
        
        # Log notification to database
        db.add_notification(
            product_id=product['id'],
            type='price_drop',
            platform=platform,
            old_price=old_price,
            new_price=new_price,
            status='sent' if any(success.values()) else 'failed'
        )
        
        return success
    
    def send_deals_digest(self, deals: List[Dict]):
        """Send daily digest of deals"""
        if not deals:
            return {'success': False, 'reason': 'no_deals'}
        
        success = {}
        
        # Email digest
        if self.email_enabled:
            success['email'] = self._send_email_digest(deals)
        
        # Telegram digest
        if self.telegram_enabled:
            formatted_deals = [
                {
                    'product_name': deal['name'],
                    'platform': deal['platform'],
                    'old_price': deal.get('original_price', 0),
                    'new_price': deal['price'],
                    'url': self._get_url_from_deal(deal)
                }
                for deal in deals
            ]
            success['telegram'] = send_deals_summary(formatted_deals)
        
        return success
    
    def _send_email_alert(self, product: Dict, platform: str,
                         old_price: float, new_price: float, url: str) -> bool:
        """Send price drop email"""
        try:
            discount = ((old_price - new_price) / old_price * 100) if old_price else 0
            
            subject = f"🔥 Price Drop Alert: {product['name']}"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">Price Drop Alert!</h2>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>{product['name']}</h3>
                    <p><strong>Platform:</strong> {platform}</p>
                    <p><strong>Old Price:</strong> <span style="text-decoration: line-through;">₹{old_price:,.2f}</span></p>
                    <p><strong>New Price:</strong> <span style="color: #28a745; font-size: 24px;">₹{new_price:,.2f}</span></p>
                    <p><strong>You Save:</strong> <span style="color: #28a745;">₹{old_price - new_price:,.2f} ({discount:.1f}% OFF)</span></p>
                    <p><strong>Your Threshold:</strong> ₹{product['threshold']:,.2f}</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <a href="{url}" style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Product →
                    </a>
                </div>
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    This alert was sent because the price dropped below your threshold of ₹{product['threshold']:,.2f}
                </p>
            </body>
            </html>
            """
            
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"Error sending email alert: {e}")
            return False
    
    def _send_email_digest(self, deals: List[Dict]) -> bool:
        """Send daily deals digest email"""
        try:
            subject = f"🔥 Daily Deals Digest - {len(deals)} Hot Deals!"
            
            deals_html = ""
            for deal in deals[:10]:  # Top 10 deals
                discount = deal.get('discount_percent', 0)
                deals_html += f"""
                <div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #667eea;">
                    <h4 style="margin: 0 0 10px 0;">{deal['name']}</h4>
                    <p style="margin: 5px 0;"><strong>Platform:</strong> {deal['platform']}</p>
                    <p style="margin: 5px 0;"><strong>Price:</strong> <span style="color: #28a745; font-size: 18px;">₹{deal['price']:,.2f}</span></p>
                    <p style="margin: 5px 0;"><strong>Discount:</strong> <span style="color: #dc3545;">{discount:.1f}% OFF</span></p>
                    <a href="{self._get_url_from_deal(deal)}" style="color: #667eea;">View Deal →</a>
                </div>
                """
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #667eea;">Your Daily Deals Digest</h2>
                <p>Here are the top {len(deals)} deals we found for you today!</p>
                
                {deals_html}
                
                <p style="color: #666; font-size: 12px; margin-top: 30px;">
                    Indian Price Tracker | {datetime.now().strftime('%B %d, %Y')}
                </p>
            </body>
            </html>
            """
            
            return self._send_email(subject, body)
            
        except Exception as e:
            print(f"Error sending digest email: {e}")
            return False
    
    def _send_email(self, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = config.SENDER_EMAIL
            msg['To'] = config.RECEIVER_EMAIL
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _get_url_from_deal(self, deal: Dict) -> str:
        """Get URL from deal based on platform"""
        platform = deal['platform'].lower()
        if 'amazon' in platform and deal.get('amazon_url'):
            return deal['amazon_url']
        elif 'flipkart' in platform and deal.get('flipkart_url'):
            return deal['flipkart_url']
        elif 'meesho' in platform and deal.get('meesho_url'):
            return deal['meesho_url']
        return "#"

# Singleton instance
notifier = NotificationManager()

if __name__ == '__main__':
    print(f"Email enabled: {notifier.email_enabled}")
    print(f"Telegram enabled: {notifier.telegram_enabled}")
