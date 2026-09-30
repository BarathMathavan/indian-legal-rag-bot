import os
import json
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Key India Code URLs for core criminal acts
ACT_URLS = {
    "IPC": "https://www.indiacode.nic.in/handle/123456789/2263",
    "BNS": "https://www.indiacode.nic.in/handle/123456789/20059" # Bharatiya Nyaya Sanhita, 2023
}

def fetch_act_sections(act_name: str, base_handle_url: str):
    print(f"[*] Fetching index for {act_name}...")
    response = requests.get(base_handle_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"[!] Failed to fetch {act_name}. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Locate all section links from the table of contents
    sections_data = []
    links = soup.find_all("a", href=True)
    
    # Filter for section URLs (India Code formats them with section-details or handle parameters)
    section_links = [
        link for link in links 
        if "section" in link["href"].lower() or "handle" in link["href"].lower()
    ]

    print(f"[*] Found links to process for {act_name}...")
    
    # Fallback/Direct Scraping: If India Code provides an entire one-page view or individual sections
    # Extract clean text sections
    content_divs = soup.find_all("div", class_="section-content") or soup.find_all("td")
    
    # (Optional) Direct PDF Auto-Downloader if you prefer full PDFs
    pdf_link = None
    for a in soup.find_all("a", href=True):
        if a["href"].endswith(".pdf"):
            pdf_link = a["href"]
            break
            
    if pdf_link:
        if not pdf_link.startswith("http"):
            pdf_link = "https://www.indiacode.nic.in" + pdf_link
        download_pdf(act_name, pdf_link)

    return sections_data

def download_pdf(act_name: str, pdf_url: str):
    os.makedirs("data", exist_ok=True)
    file_path = f"data/{act_name}.pdf"
    print(f"[*] Downloading official Bare Act PDF: {pdf_url}")
    
    res = requests.get(pdf_url, headers=HEADERS, stream=True)
    with open(file_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"[✓] Saved to {file_path}")

if __name__ == "__main__":
    for act, url in ACT_URLS.items():
        fetch_act_sections(act, url)
        time.sleep(2)  # Respect server rate limits