import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

URL = "https://rdeapps.stanford.edu/dininghallmenu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": URL,
    "Origin": "https://rdeapps.stanford.edu"
}

def fetch_menu_html(dining_hall: str, date_str: str, meal_type: str) -> str:
    """
    Fetches the raw HTML of the Stanford Dining Hall menu for a specific date,
    location, and meal type, handling ASP.NET WebForms session and state.
    """
    logger.info(f"Initiating GET request to {URL} to retrieve ASP.NET state...")
    session = requests.Session()
    
    # 1. First GET request to initialize session cookies and retrieve dynamic WebForms state
    get_response = session.get(URL, headers=HEADERS)
    if get_response.status_code != 200:
        raise Exception(f"Failed to initialize session. GET status code: {get_response.status_code}")
        
    soup = BeautifulSoup(get_response.text, "html.parser")
    
    def get_hidden_field(soup_obj, name):
        field = soup_obj.find("input", {"name": name})
        return field.get("value", "") if field else ""

    viewstate = get_hidden_field(soup, "__VIEWSTATE")
    generator = get_hidden_field(soup, "__VIEWSTATEGENERATOR")
    validation = get_hidden_field(soup, "__EVENTVALIDATION")
    
    logger.info(f"Successfully retrieved ASP.NET state (ViewState len={len(viewstate)})")
    
    # 2. Formulate the POST parameters.
    # In ASP.NET WebForms, selecting a day/location/meal type triggers a postback.
    # We use 'GetMenulstDay' or standard postback targets to submit the form request.
    payload = {
        "__EVENTTARGET": "GetMenulstDay",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": generator,
        "__EVENTVALIDATION": validation,
        "ctl00$MainContent$lstLocations": dining_hall,
        "ctl00$MainContent$lstDay": date_str,
        "ctl00$MainContent$lstMealType": meal_type
    }
    
    logger.info(f"Sending POST request for Location={dining_hall}, Date={date_str}, Meal={meal_type}...")
    post_response = session.post(URL, headers=HEADERS, data=payload)
    
    if post_response.status_code != 200:
        raise Exception(f"Failed to fetch menu. POST status code: {post_response.status_code}")
        
    logger.info("Successfully fetched menu HTML!")
    return post_response.text

def parse_menu(html: str) -> dict:
    """
    Parses the dynamic HTML returned by the POST request.
    Extracts the menu header and lists of parsed items with ingredients and allergens.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract menu header details
    header_h2 = soup.find("h2", class_="clsMenuHeader")
    header_text = header_h2.text.strip().replace("\r", "").replace("\n", " ").strip() if header_h2 else "Stanford Dining Menu"
    
    # Iterate through rows in the page to extract dishes
    rows = soup.find_all("div", class_="row")
    items = []
    current_item = None
    
    for row in rows:
        h3_name = row.find("h3", class_="clsLabel_Name")
        if h3_name:
            if current_item:
                items.append(current_item)
            current_item = {
                "name": h3_name.text.strip(),
                "description": "",
                "ingredients": "",
                "allergens": [],
                "shared_equip": []
            }
            continue
            
        if current_item:
            # Check for optional details in the subsequent sibling rows
            desc_span = row.find("span", class_="clsLabel_Description")
            if desc_span:
                current_item["description"] = desc_span.text.strip()
                continue
                
            ing_span = row.find("span", class_="clsLabel_Ingredients")
            if ing_span:
                text = ing_span.text.strip()
                if text.startswith("Ingredients:"):
                    text = text[len("Ingredients:"):].strip()
                current_item["ingredients"] = text
                continue
                
            all_span = row.find("span", class_="clsLabel_Allergens")
            if all_span:
                text = all_span.text.strip()
                if text.startswith("Allergens:"):
                    text = text[len("Allergens:"):].strip()
                # Split allergens by comma and strip
                current_item["allergens"] = [a.strip() for a in text.split(",") if a.strip()]
                continue
                
            trace_span = row.find("span", class_="clsLabel_TraceAllergens")
            if trace_span:
                text = trace_span.text.strip()
                if text.startswith("Made on shared equipment with"):
                    text = text[len("Made on shared equipment with"):].strip()
                # Split trace allergens by comma and strip
                current_item["shared_equip"] = [a.strip() for a in text.split(",") if a.strip()]
                continue

    if current_item:
        items.append(current_item)
        
    return {
        "header": header_text,
        "items": items
    }
