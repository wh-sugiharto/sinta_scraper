# sinta_scraper.py
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Kredensial login
USERNAME = "[EMAIL_ADDRESS]"
PASSWORD = "[PASSWORD]"

# Daftar tab view yang ingin di-scrape
TABS = [
    "scopus",        # Scopus
    #"garuda",        # Garuda
    #"googlescholar", # Google Scholar
    #"rama",          # Ristekdikti
    #"researches",    # Researches
    #"services",      # Services
    #"iprs",          # IPRs
    #"books",         # Books
    #"metrics"        # Metrics
]

# Baca file Excel untuk mendapatkan AuthorID unik
now = datetime.now()
this_year = now.year

df = pd.read_excel("author_ids.xlsx")
df = df.drop_duplicates(subset=['AuthorID'])
AUTHOR_IDS = df['AuthorID'].astype(str).tolist()

# Setup browser
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

def login_sinta(driver):
    print("🔐 Membuka halaman login SINTA...")
    driver.get("https://sinta.kemdikbud.go.id/logins")
    time.sleep(2)

    try:
        print("📥 Memasukkan kredensial...")
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, '//button[contains(text(), "Login")]').click()
        
        print("⏳ Menunggu login selesai...")
        time.sleep(5)  # Tunggu login selesai
        return True
    except Exception as e:
        print(f"❌ Gagal login: {e}")
        return False

def scrape_author_name(driver, author_id):
    driver.get(f"https://sinta.kemdikbud.go.id/authors/profile/{author_id}")
    time.sleep(2)
    try:
        name = driver.find_element(By.TAG_NAME, "h3").text.strip()
        return name.split('\n')[0]
    except:
        return "Unknown"

def scrape_tab(driver, author_id, view, author_name):
    base_url = f"https://sinta.kemdikbud.go.id/authors/profile/{author_id}"
    if view:
        base_url += f"/?view={view}"
    else:
        base_url += "/"  # Untuk tab articles tanpa parameter view
    
    tab_name = view.upper() if view else "ARTICLES"
    print(f"\n📄 Tab {tab_name} untuk Author: {author_name} (ID: {author_id}): {base_url}")

    page = 1
    total_pages = 1
    total_records = 0
    all_items = []
    
    while True:
        # Construct URL with pagination
        url = f"{base_url}&page={page}" if view else f"{base_url}?page={page}" if page > 1 else base_url
        driver.get(url)
        time.sleep(3)
        
        # Get pagination info
        try:
            pagination_element = driver.find_element(By.CSS_SELECTOR, ".pagination-text small")
            pagination_text = pagination_element.text
            
            # Parse pagination text
            if "Page" in pagination_text and "Total Records" in pagination_text:
                # Format: "Page 1 of 2 | Total Records 15"
                page_info = pagination_text.split("|")[0].strip()
                total_records = int(pagination_text.split("Total Records")[1].strip())
                
                current_page = int(page_info.split("Page")[1].split("of")[0].strip())
                total_pages = int(page_info.split("of")[1].strip())
            
            print(f"ℹ️ Pagination Info: {pagination_text}")
        except Exception:
            # Handle error without showing stacktrace
            print("ℹ️ Tidak ditemukan informasi pagination, asumsikan hanya 1 halaman")
            total_pages = 1  # Jika tidak ada pagination, asumsikan hanya 1 halaman
        
        # Get current page items
        items = driver.find_elements(By.CLASS_NAME, "ar-list-item")
        print(f"🔎 Ditemukan {len(items)} item di tab {tab_name} halaman {page} (Total: {total_records} records)")
        
        # Process items
        for idx, item in enumerate(items, 1):
            try:
                title_element = item.find_element(By.CLASS_NAME, "ar-title")
                title = title_element.text.strip()
                link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                meta = item.find_element(By.CLASS_NAME, "ar-meta").text.strip()
                try:
                    year = item.find_element(By.CLASS_NAME, "ar-year").text.strip()
                except:
                    year = "Unknown"

                # Ekstrak informasi ar-cited dan ar-quartile
                try:
                    cited = item.find_element(By.CLASS_NAME, "ar-cited").text.strip()
                except:
                    cited = "Unknown"

                try:
                    quartile = item.find_element(By.CLASS_NAME, "ar-quartile").text.strip()
                except:
                    quartile = "Unknown"

                # Tampilkan informasi di log
                print(f"{idx}. 📘 {title}")
                print(f"    🔗 Link: {link}")
                print(f"    📄 {meta}")
                print(f"    📅 Tahun: {year}")
                print(f"    📊 Cited: {cited}")
                print(f"    🏅 Quartile: {quartile}")

                all_items.append({
                    "AuthorID": author_id,
                    "AuthorName": author_name,
                    "Tab": tab_name,
                    "Title": title,
                    "Link": link,
                    "Meta": meta,
                    "Year": year,
                    "Cited": cited,  # Kolom baru untuk cited
                    "Quartile": quartile,  # Kolom baru untuk quartile
                    "Page": page,
                    "TotalPages": total_pages,
                    "TotalRecords": total_records,
                    "ItemNumber": idx
                })
            except Exception as e:
                print(f"⚠️ Gagal membaca item ke-{idx}: {e}")
        
        # Check if we've reached the last page
        if page >= total_pages:
            print(f"ℹ️ Sudah mencapai halaman terakhir ({total_pages})")
            break
            
        page += 1

    return all_items

def main():
    # Setup browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Login
    if not login_sinta(driver):
        print("❌ Proses scraping dibatalkan karena gagal login")
        driver.quit()
        return

    # Loop untuk setiap author dan setiap tab
    all_data = []
    for author_id in AUTHOR_IDS:
        author_name = scrape_author_name(driver, author_id)
        print("\n============================")
        print(f"📌 Profil Author: {author_name} (ID: {author_id}, Tahun: {this_year})")
        print("============================")
        for tab in TABS:
            print(f"\n🔄 Memulai scraping untuk tab: {tab.upper()}")
            try:
                items = scrape_tab(driver, author_id, tab, author_name)
                all_data.extend(items)
                print(f"ℹ️ Scraping tab {tab.upper()} selesai")
            except Exception as e:
                print(f"⚠️ Gagal scraping tab {tab.upper()}: {e}")
                continue

    # Simpan ke CSV dan Excel
    output_df = pd.DataFrame(all_data)
    
    # Urutkan kolom sesuai kebutuhan
    columns_order = [
        'AuthorID', 'AuthorName', 'Tab', 'Title', 'Link', 'Meta', 'Year', 
        'Cited', 'Quartile', 'Page', 'TotalPages', 'TotalRecords', 'ItemNumber'
    ]
    output_df = output_df[columns_order]
    
    # Simpan ke file CSV
    csv_filename = "sinta_authors_full.csv"
    output_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    # Simpan ke file Excel
    xlsx_filename = "sinta_authors_full.xlsx"
    output_df.to_excel(xlsx_filename, index=False)
    
    print(f"\n✅ Selesai scraping semua data author.")
    print(f"    - Data CSV disimpan di {csv_filename}")
    print(f"    - Data Excel disimpan di {xlsx_filename}")
    driver.quit()

if __name__ == "__main__":
    main()
