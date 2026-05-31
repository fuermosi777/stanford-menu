import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import config

logger = logging.getLogger(__name__)

URL = "https://rdeapps.stanford.edu/dininghallmenu/"

def generate_html_email(menu_data: dict, date_str: str) -> str:
    """
    Generates a beautifully styled, premium-looking HTML email body for the menu.
    Uses responsive card elements, Stanford Cardinal Red branding accents,
    and elegant typography/spacing.
    """
    header = menu_data.get("header", f"Arrillaga Dining Hall Menu - {date_str}")
    items = menu_data.get("items", [])
    
    # Generate cards for each food item
    cards_html = ""
    if not items:
        cards_html = """
        <div style="background-color: #f9f9f9; border-radius: 8px; padding: 24px; text-align: center; border: 1px solid #e0e0e0; margin-top: 16px;">
            <p style="margin: 0; color: #5f6368; font-size: 16px;">No menu items listed for today.</p>
        </div>
        """
    else:
        for item in items:
            name = item.get("name", "Unknown Dish")
            desc = item.get("description", "")
            ingredients = item.get("ingredients", "")
            allergens = item.get("allergens", [])
            shared_equip = item.get("shared_equip", [])
            
            # Format allergens
            allergens_html = ""
            if allergens:
                allergens_list = ", ".join(allergens)
                allergens_html = f"""
                <div style="margin-top: 10px; font-size: 12px; color: #b00020; font-weight: 600;">
                    ⚠️ Contains: {allergens_list}
                </div>
                """
                
            # Format shared equipment allergens
            shared_html = ""
            if shared_equip:
                shared_list = ", ".join(shared_equip)
                shared_html = f"""
                <div style="margin-top: 4px; font-size: 11px; color: #e65100; font-style: italic;">
                    ⚠️ Shared Equipment: {shared_list}
                </div>
                """
                
            # Format ingredients
            ing_html = ""
            if ingredients:
                ing_html = f"""
                <p style="margin: 8px 0 0 0; font-size: 13px; color: #5f6368; line-height: 1.5;">
                    <strong style="color: #202124;">Ingredients:</strong> {ingredients}
                </p>
                """
                
            # Format description
            desc_html = ""
            if desc:
                desc_html = f"""
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #3c4043; line-height: 1.5; font-style: italic;">
                    {desc}
                </p>
                """
                
            # Build the card
            cards_html += f"""
            <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; margin-bottom: 16px; border: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <h3 style="margin: 0; color: #8C1515; font-size: 18px; font-weight: 700; border-bottom: 2px solid #f4f4f4; padding-bottom: 8px;">
                    {name}
                </h3>
                {desc_html}
                {ing_html}
                {allergens_html}
                {shared_html}
            </div>
            """

    # Full Email template
    email_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{header}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7f9fa; color: #202124; margin: 0; padding: 0;">
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #f7f9fa;">
            <tr>
                <td style="padding: 24px 16px 8px 16px;">
                    <!-- Header Bar -->
                    <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background-color: #8C1515; border-radius: 8px 8px 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="padding: 28px 24px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">
                                    Stanford Dining
                                </h1>
                                <p style="margin: 6px 0 0 0; color: #fcebeb; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">
                                    Arrillaga Family Dining Commons
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            
            <tr>
                <td style="padding: 0 16px;">
                    <!-- Menu Date Banner -->
                    <div style="background-color: #ffffff; border-radius: 0 0 8px 8px; padding: 18px 24px; border-left: 1px solid #e0e0e0; border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0; margin-bottom: 24px; text-align: center;">
                        <h2 style="margin: 0; color: #202124; font-size: 18px; font-weight: 700;">
                            🍴 {date_str} Menu (Lunch Only)
                        </h2>
                    </div>
                </td>
            </tr>
            
            <tr>
                <td style="padding: 0 16px;">
                    <!-- Food Cards Container -->
                    {cards_html}
                </td>
            </tr>
            
            <tr>
                <td style="padding: 32px 16px 24px 16px; text-align: center;">
                    <!-- Footer -->
                    <p style="margin: 0; font-size: 12px; color: #5f6368; line-height: 1.5;">
                        This is an automated menu alert from the Stanford Menu Scraper.<br>
                        Powered by GitHub Actions & Python.
                    </p>
                    <p style="margin: 12px 0 0 0; font-size: 11px; color: #9aa0a6;">
                        Stanford Dining Hall Menu Web app: <a href="{URL}" style="color: #8C1515; text-decoration: underline;">rdeapps.stanford.edu/dininghallmenu/</a>
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return email_template

def send_email_notification(menu_data: dict, date_str: str):
    """
    Sends the menu notification via SMTP email based on config settings.
    """
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD or not config.RECIPIENT_EMAIL:
        logger.warning("Missing email configuration (SENDER_EMAIL, SENDER_PASSWORD, or RECIPIENT_EMAIL). Skipping email delivery.")
        logger.info("Local configuration debug check:")
        logger.info(f"  SENDER_EMAIL: {'Set' if config.SENDER_EMAIL else 'MISSING'}")
        logger.info(f"  SENDER_PASSWORD: {'Set' if config.SENDER_PASSWORD else 'MISSING'}")
        logger.info(f"  RECIPIENT_EMAIL: {'Set' if config.RECIPIENT_EMAIL else 'MISSING'}")
        return False
        
    subject = f"🍽️ Arrillaga Lunch Menu - {date_str}"
    html_content = generate_html_email(menu_data, date_str)
    
    # Create MIMEMultipart message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SENDER_EMAIL
    msg["To"] = config.RECIPIENT_EMAIL
    
    # Attach HTML body
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        logger.info(f"Connecting to SMTP server {config.SMTP_SERVER}:{config.SMTP_PORT}...")
        
        # Connect using the standard port 587 (STARTTLS) or 465 (SSL)
        if config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
        else:
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
        logger.info("SMTP Connection secure. Logging in...")
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        
        logger.info(f"Sending email from {config.SENDER_EMAIL} to {config.RECIPIENT_EMAIL}...")
        server.sendmail(config.SENDER_EMAIL, config.RECIPIENT_EMAIL, msg.as_string())
        
        server.quit()
        logger.info("Email notification sent successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        return False
