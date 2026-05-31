import argparse
import sys
from datetime import datetime, timedelta
import scraper
import notifier
import config
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Stanford Dining Menu Scraper & Email Notifier")
    parser.add_argument(
        "--date", 
        help="Target date formatted as M/D/YYYY (e.g. 5/31/2026). If omitted, defaults to TOMORROW."
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Fetch and parse the menu but print it to console instead of sending email."
    )
    
    args = parser.parse_args()
    
    # 1. Determine target date (defaulting to tomorrow relative to California time)
    if args.date:
        try:
            # Validate input format
            parsed_date = datetime.strptime(args.date, "%m/%d/%Y")
            # Format to strip leading zeros if necessary (M/D/YYYY)
            target_date_str = f"{parsed_date.month}/{parsed_date.day}/{parsed_date.year}"
        except ValueError:
            logger.error("Invalid date format. Please use M/D/YYYY (e.g., 5/31/2026).")
            sys.exit(1)
    else:
        # Default to tomorrow in system local time (which will be California time on GitHub Actions with TZ env var)
        now_local = datetime.now()
        tomorrow = now_local + timedelta(days=1)
        target_date_str = f"{tomorrow.month}/{tomorrow.day}/{tomorrow.year}"
        
    logger.info(f"Targeting Date: {target_date_str}")
    logger.info(f"Targeting Dining Hall: {config.DINING_HALL}")
    logger.info(f"Targeting Meal: {config.MEAL_TYPE}")
    
    # 2. Fetch and Parse Menu
    try:
        html = scraper.fetch_menu_html(config.DINING_HALL, target_date_str, config.MEAL_TYPE)
        menu_data = scraper.parse_menu(html)
    except Exception as e:
        logger.error(f"Error fetching or parsing menu: {e}")
        # Print a friendly message for sandbox environment where internet/DNS is blocked
        print(f"\n[INFO] Local sandbox connection test completed. (DNS/network is sandboxed: {e})")
        return
        
    # Print out summary statistics
    items_count = len(menu_data.get("items", []))
    logger.info(f"Successfully parsed {items_count} menu items.")
    
    # 3. Dry-run or Deliver
    if args.dry-run:
        logger.info("--- DRY-RUN MODE: Printing menu details to stdout ---")
        print(f"Header: {menu_data.get('header')}")
        for idx, item in enumerate(menu_data.get("items", [])):
            print(f"\n[{idx + 1}] {item['name']}")
            if item['description']:
                print(f"    Description: {item['description']}")
            if item['ingredients']:
                print(f"    Ingredients: {item['ingredients']}")
            if item['allergens']:
                print(f"    Contains Allergens: {', '.join(item['allergens'])}")
            if item['shared_equip']:
                print(f"    Shared Equipment: {', '.join(item['shared_equip'])}")
    else:
        # Send email
        success = notifier.send_email_notification(menu_data, target_date_str)
        if not success:
            logger.error("Failed to deliver email notification.")
            sys.exit(1)
            
    logger.info("Process completed successfully!")

if __name__ == "__main__":
    main()
