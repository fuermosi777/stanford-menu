# Stanford Dining Menu Notifier 🍽️

A lightweight, automated Python service that queries the daily lunch menu from the Arrillaga Family Dining Commons at Stanford University and emails a beautifully formatted HTML notification of the next day's menu.

Automated completely for free via **GitHub Actions**!

---

## Features

- **Session-based Scraping**: Clean, robust scraping that handles the ASP.NET WebForms session-state lifecycle (`__VIEWSTATE`, cookie management, etc.).
- **Premium Design**: Generates responsive, gorgeous HTML email templates with custom cards for each menu item, including distinct warnings for allergens and trace allergens.
- **Timezone Aware**: Uses timezone-aware date calculations so that no matter where the runner is situated, the "tomorrow" menu is computed correctly according to California time.
- **Serverless Automation**: Deployed on a daily cron schedule using GitHub Actions.

---

## Local Setup & Quick Start

### 1. Install Dependencies
Ensure you have Python 3.9+ installed, then create a virtual environment and install the required packages:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Test Local Scraper (Dry Run)
You can run the script in **dry-run** mode, which fetches and prints tomorrow's menu to your console without attempting to send any emails.

```bash
# Fetch and print tomorrow's menu
python main.py --dry-run

# Fetch and print a specific date's menu (M/D/YYYY)
python main.py --date 5/31/2026 --dry-run
```

---

## GitHub Actions & Automation Setup

This repository is pre-configured to run automatically every day at **18:00 PDT / 17:00 PST (01:00 UTC)** using a GitHub Actions workflow.

To enable the daily email alerts, follow these simple steps to add your secrets to your GitHub repository:

### 1. Configure Repository Secrets
Go to your GitHub repository: `https://github.com/fuermosi777/stanford-menu`

1. Navigate to **Settings** -> **Secrets and variables** -> **Actions**.
2. Click **New repository secret** and add the following:

| Secret Name | Description | Example |
| :--- | :--- | :--- |
| `SENDER_EMAIL` | The email address sending the alerts | `your_gmail@gmail.com` |
| `SENDER_PASSWORD` | The SMTP password or App Password for the sender | `abcd efgh ijkl mnop` *(see below)* |
| `RECIPIENT_EMAIL` | The email address where you want to receive the alerts | `recipient_email@domain.com` |
| `SMTP_SERVER` | *(Optional)* The SMTP server domain (defaults to Gmail) | `smtp.gmail.com` |
| `SMTP_PORT` | *(Optional)* The SMTP port (defaults to 587) | `587` |

### 2. How to get a Gmail App Password
If you are using Gmail for the `SENDER_EMAIL`:
1. Go to your **Google Account Settings** (myaccount.google.com).
2. Go to **Security** -> **2-Step Verification** (must be enabled).
3. Scroll to the bottom and select **App passwords**.
4. Select App: *Other (Custom name)*, type `Stanford Menu Scraper`, and click **Generate**.
5. Copy the 16-character code (e.g., `abcd efgh ijkl mnop`) and save it as your `SENDER_PASSWORD` secret on GitHub.

---

## File Structure

- `main.py`: Entrypoint orchestrator. Determines target date, initiates scraper, and triggers delivery.
- `scraper.py`: Core logic for ASP.NET WebForms retrieval, HTTP cookies/headers, and BeautifulSoup HTML parser.
- `notifier.py`: Formulator for the responsive HTML email template and SMTP sending.
- `config.py`: Loads environment configurations with fallback values.
- `.github/workflows/menu_notifier.yml`: The automation schedule and job definition.
