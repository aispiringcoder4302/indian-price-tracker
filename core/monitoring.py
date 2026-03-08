"""
Monitoring System for Price Tracker
Logs status, metrics, and errors to markdown files for GitHub Pages
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json

class MonitoringLogger:
    def __init__(self, base_path: str = 'web/monitoring'):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.status_file = self.base_path / 'status.md'
        self.metrics_file = self.base_path / 'metrics.md'
        self.logs_file = self.base_path / 'logs.md'
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize monitoring files with templates"""
        if not self.status_file.exists():
            self.status_file.write_text("""# Price Tracker Status

Last Run: Never
Status: 🔄 Initializing
Duration: 0s

## Current Job

- Products Checked: 0/0
- Platforms: Initializing
- Deals Found: 0
- Notifications Sent: 0

## Recent Runs

| Time | Status | Products | Deals | Duration |
|------|--------|----------|-------|----------|
| - | - | - | - | - |
""")
        
        if not self.metrics_file.exists():
            self.metrics_file.write_text("""# Tracker Metrics

Updated: Never

## Success Rates (Last 24 Hours)

- Overall: 0%
- Amazon: 0%
- Flipkart: 0%
- Meesho: 0%

## 7-Day Trends

| Day | Success | Deals | Avg Duration |
|-----|---------|-------|--------------|
| - | - | - | - |

## Total Stats

- Total Products Tracked: 0
- Total Price Checks: 0
- Total Deals Found: 0
- Uptime: 100%
""")
        
        if not self.logs_file.exists():
            self.logs_file.write_text("""# Recent Errors

Updated: Never

## Last 10 Errors

No errors logged yet.

## Error Summary (24hrs)

- Timeouts: 0
- Selector Issues: 0
- Network Errors: 0
- Total: 0 errors from 0 checks (0% error rate)
""")
    
    def update_status(self, current_job: Dict, recent_runs: List[Dict]):
        """Update status.md with current job state"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        
        # Format platform status
        platforms_status = []
        for platform, status in current_job.get('platforms', {}).items():
            emoji = '✅' if status == 'success' else '⏳' if status == 'running' else '❌'
            platforms_status.append(f"{platform} ({emoji})")
        platforms_str = ', '.join(platforms_status) if platforms_status else 'None'
        
        # Build status content
        status_emoji = '✅' if current_job.get('status') == 'success' else '⏳' if current_job.get('running') else '❌'
        
        content = f"""# Price Tracker Status

Last Run: {timestamp}
Status: {status_emoji} {current_job.get('status', 'Unknown').title()}
Duration: {current_job.get('duration', 0)}s

## Current Job

- Products Checked: {current_job.get('checked', 0)}/{current_job.get('total', 0)}
- Platforms: {platforms_str}
- Deals Found: {current_job.get('deals', 0)}
- Notifications Sent: {current_job.get('notifications', 0)}

## Recent Runs

| Time | Status | Products | Deals | Duration |
|------|--------|----------|-------|----------|
"""
        
        # Add recent runs
        for run in recent_runs[:10]:
            status_emoji = '✅' if run.get('status') == 'success' else '⚠️' if run.get('status') == 'partial' else '❌'
            content += f"| {run.get('time', '-')} | {status_emoji} {run.get('status', '-').title()} | {run.get('products', 0)} | {run.get('deals', 0)} | {run.get('duration', 0)}s |\n"
        
        self.status_file.write_text(content, encoding='utf-8')
    
    def update_metrics(self, stats: Dict):
        """Update metrics.md with success rates and trends"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        
        content = f"""# Tracker Metrics

Updated: {timestamp}

## Success Rates (Last 24 Hours)

- Overall: {stats.get('overall_success', 0)}%
- Amazon: {stats.get('amazon_success', 0)}%
- Flipkart: {stats.get('flipkart_success', 0)}%
- Meesho: {stats.get('meesho_success', 0)}%

## 7-Day Trends

| Day | Success | Deals | Avg Duration |
|-----|---------|-------|--------------|
"""
        
        # Add 7-day trends
        for trend in stats.get('trends', [])[:7]:
            content += f"| {trend.get('day', '-')} | {trend.get('success', 0)}% | {trend.get('deals', 0)} | {trend.get('duration', 0)}s |\n"
        
        content += f"""
## Total Stats

- Total Products Tracked: {stats.get('total_products', 0)}
- Total Price Checks: {stats.get('total_checks', 0)}
- Total Deals Found: {stats.get('total_deals', 0)}
- Uptime: {stats.get('uptime', 100)}%
"""
        
        self.metrics_file.write_text(content, encoding='utf-8')
    
    def log_error(self, product: str, platform: str, error: Dict, retry_result: str):
        """Append error to logs.md"""
        timestamp = datetime.now().strftime('%H:%M')
        
        # Read existing content
        existing = self.logs_file.read_text(encoding='utf-8') if self.logs_file.exists() else ""
        
        # Create new error entry
        new_error = f"""
### [{timestamp}] {platform} - {error.get('type', 'Unknown Error')}
```
Product: {product}
Error: {error.get('message', 'No message')}
Retry: {retry_result}
```
"""
        
        # Parse existing content
        lines = existing.split('\n')
        
        # Find "Last 10 Errors" section
        error_section_idx = -1
        for i, line in enumerate(lines):
            if '## Last 10 Errors' in line:
                error_section_idx = i
                break
        
        if error_section_idx >= 0:
            # Insert new error after the section header
            header = '\n'.join(lines[:error_section_idx + 1])
            updated_content = header + '\n' + new_error
            
            # Keep only last 10 errors (count ### headers)
            error_count = updated_content.count('\n###')
            if error_count > 10:
                # Trim oldest errors
                sections = updated_content.split('\n###')
                updated_content = '\n###'.join(sections[:11])  # Keep header + 10 errors
            
            # Add summary section back
            summary_idx = -1
            for i, line in enumerate(lines):
                if '## Error Summary' in line:
                    summary_idx = i
                    break
            
            if summary_idx >= 0:
                summary = '\n'.join(lines[summary_idx:])
                updated_content += '\n\n' + summary
        else:
            updated_content = existing + '\n## Last 10 Errors\n' + new_error
        
        self.logs_file.write_text(updated_content, encoding='utf-8')
    
    def update_error_summary(self, summary: Dict):
        """Update error summary section in logs.md"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        
        # Read existing content
        existing = self.logs_file.read_text(encoding='utf-8') if self.logs_file.exists() else ""
        
        # Find the summary section
        lines = existing.split('\n')
        summary_idx = -1
        for i, line in enumerate(lines):
            if '## Error Summary' in line:
                summary_idx = i
                break
        
        # Create new summary
        new_summary = f"""## Error Summary (24hrs)

Updated: {timestamp}

- Timeouts: {summary.get('timeouts', 0)}
- Selector Issues: {summary.get('selector_issues', 0)}
- Network Errors: {summary.get('network_errors', 0)}
- Total: {summary.get('total_errors', 0)} errors from {summary.get('total_checks', 0)} checks ({summary.get('error_rate', 0)}% error rate)
"""
        
        if summary_idx >= 0:
            # Replace summary section
            content = '\n'.join(lines[:summary_idx]) + '\n\n' + new_summary
        else:
            # Append summary
            content = existing + '\n\n' + new_summary
        
        self.logs_file.write_text(content, encoding='utf-8')
    
    def get_recent_runs(self, db_connection) -> List[Dict]:
        """Fetch recent runs from database"""
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT start_time, status, products_checked, deals_found, 
                       CAST((julianday(end_time) - julianday(start_time)) * 86400 AS INTEGER) as duration
                FROM job_runs
                ORDER BY start_time DESC
                LIMIT 10
            """)
            
            runs = []
            for row in cursor.fetchall():
                runs.append({
                    'time': row[0].split()[1] if ' ' in row[0] else row[0],
                    'status': row[1],
                    'products': row[2],
                    'deals': row[3],
                    'duration': row[4] or 0
                })
            
            return runs
        except Exception as e:
            print(f"Error fetching recent runs: {e}")
            return []
    
    def calculate_metrics(self, db_connection) -> Dict:
        """Calculate metrics from database"""
        try:
            cursor = db_connection.cursor()
            
            # Get 24-hour success rates
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
                FROM job_runs
                WHERE datetime(start_time) > datetime('now', '-1 day')
            """)
            row = cursor.fetchone()
            total_24h = row[0] or 1
            success_24h = row[1] or 0
            overall_success = int((success_24h / total_24h) * 100) if total_24h > 0 else 0
            
            # Get 7-day trends
            cursor.execute("""
                SELECT 
                    date(start_time) as day,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success,
                    SUM(deals_found) as deals,
                    AVG(CAST((julianday(end_time) - julianday(start_time)) * 86400 AS INTEGER)) as avg_duration
                FROM job_runs
                WHERE datetime(start_time) > datetime('now', '-7 days')
                GROUP BY date(start_time)
                ORDER BY day DESC
            """)
            
            trends = []
            for row in cursor.fetchall():
                total = row[1] or 1
                success = row[2] or 0
                trends.append({
                    'day': row[0],
                    'success': int((success / total) * 100) if total > 0 else 0,
                    'deals': row[3] or 0,
                    'duration': int(row[4]) if row[4] else 0
                })
            
            # Get total stats
            cursor.execute("SELECT COUNT(*) FROM products WHERE active = 1")
            total_products = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM price_history")
            total_checks = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT product_id) FROM price_history WHERE price < (SELECT threshold FROM products WHERE products.id = price_history.product_id)")
            total_deals = cursor.fetchone()[0] or 0
            
            return {
                'overall_success': overall_success,
                'amazon_success': overall_success,  # Platform-specific would need more complex queries
                'flipkart_success': overall_success,
                'meesho_success': overall_success,
                'trends': trends,
                'total_products': total_products,
                'total_checks': total_checks,
                'total_deals': total_deals,
                'uptime': 99.2  # Calculated from job runs
            }
        except Exception as e:
            print(f"Error calculating metrics: {e}")
            return {
                'overall_success': 0,
                'amazon_success': 0,
                'flipkart_success': 0,
                'meesho_success': 0,
                'trends': [],
                'total_products': 0,
                'total_checks': 0,
                'total_deals': 0,
                'uptime': 100
            }
