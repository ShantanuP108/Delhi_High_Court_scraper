# backend/scraper.py
import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

BASE_URL = "https://delhihighcourt.nic.in"
SEARCH_URL = f"{BASE_URL}/web/cause-lists/cause-list"

def fetch_cause_lists_for_date(date_str: str, download_folder: str = "downloads"):
    """
    Fetches and downloads all cause list PDFs for a given date from Delhi High Court.
    date_str: DD-MM-YYYY (e.g., "17-10-2025")
    """
    os.makedirs(download_folder, exist_ok=True)

    try:
        # Convert DD-MM-YYYY to YYYY-MM-DD for the form
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        formatted_date = dt.strftime("%Y-%m-%d")  # e.g., 2025-10-17
    except ValueError:
        raise ValueError("Date must be in DD-MM-YYYY format")

    # Step 1: Send POST request to get the cause list page
    payload = {
        "date": formatted_date,
        "search": ""  # You can add keyword search if needed
    }

    print(f"Searching for cause lists on {date_str}...")
    resp = requests.post(SEARCH_URL, data=payload)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Step 2: Find all PDF links in the table
    pdf_links = []
    table = soup.find("table", class_="table")  # Adjust class name based on actual HTML
    if table:
        rows = table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:  # Ensure we have enough columns
                cause_list_name = cells[1].get_text(strip=True)
                date_cell = cells[2].get_text(strip=True)
                download_cell = cells[3]
                link_tag = download_cell.find("a", href=True)
                if link_tag:
                    pdf_url = link_tag["href"]
                    if not pdf_url.startswith("http"):
                        pdf_url = BASE_URL + pdf_url
                    pdf_links.append((pdf_url, cause_list_name, date_cell))
    else:
        print("⚠️ No cause list table found on the page.")
        return []

    # Step 3: Download each PDF
    downloaded_files = []
    for url, name, date_val in pdf_links:
        # Sanitize filename
        safe_name = re.sub(r'[^\w\-_\. ]', '_', name).strip()[:50]
        filename = f"{safe_name}_{date_str}.pdf"
        filepath = os.path.join(download_folder, filename)

        print(f"Downloading: {name} → {filename}")
        try:
            pdf_resp = requests.get(url, stream=True, timeout=10)
            if pdf_resp.status_code == 200:
                with open(filepath, "wb") as f:
                    for chunk in pdf_resp.iter_content(8192):
                        f.write(chunk)
                downloaded_files.append(filepath)
            else:
                print(f"❌ Failed to download: {url} (status {pdf_resp.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")

    return downloaded_files