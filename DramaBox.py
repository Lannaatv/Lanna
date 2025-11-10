import requests
import re
from bs4 import BeautifulSoup
import sys
import time
import json
import os

# =============== INFORMASI PEMBUAT ==================
# Script by      : Ryuken (Modified for DramaBox)
# Version        : 1.0.0 - DramaBox Scraper
# Instagram      : Redpack.id
# Updated        : Scraping DramaBox drama series
# ====================================================

BASE_URL = "https://www.dramabox.com/"
JSON_FILENAME = "DramaBox.json"

processed_titles = set()
processed_urls = set()
success_count = 0
current_category_name = ""
current_category_id = ""
export_format = "json"
drama_data_list = []
all_categories_data = []

# ===== Generate Category ID =====
def generate_category_id(category_name):
    """Generate ID kategori dari nama kategori"""
    category_id = category_name.lower().replace(" ", "_").replace("'", "")
    category_id = re.sub(r'[^\w_]', '', category_id)
    return category_id

# ===== Generate drama ID unik =====
def generate_drama_id(index):
    """Generate ID unik untuk drama dengan format drama_XXX"""
    return f"drama_{index:03d}"

# ===== Initialize JSON =====
def initialize_json():
    """Reset JSON file saat program pertama kali dijalankan"""
    global all_categories_data
    
    print("\n📄 Initializing new session...")
    
    if os.path.exists(JSON_FILENAME):
        try:
            file_size = os.path.getsize(JSON_FILENAME) / 1024
            print(f"📄 Found existing {JSON_FILENAME} ({file_size:.2f} KB)")
            print("⚠️  File will be overwritten when you start scraping")
        except:
            pass
    
    all_categories_data = []
    print("✅ Session initialized - Ready to scrape fresh data")

# ===== Menu Format Export =====
def select_export_format():
    global export_format
    
    print("\n=== PILIH FORMAT EXPORT ===")
    print("1. JSON (Recommended)")
    print("2. M3U Playlist")
    print("3. Keduanya (JSON + M3U)")
    
    choice = input("\nPilih format export (1-3, default 1): ").strip()
    
    format_map = {
        "1": "json",
        "2": "m3u",
        "3": "both",
        "": "json"
    }
    
    export_format = format_map.get(choice, "json")
    
    if export_format == "json":
        print("✓ Format: JSON")
    elif export_format == "m3u":
        print("✓ Format: M3U Playlist")
    else:
        print("✓ Format: JSON + M3U")
    
    return export_format

# ===== Menu Kategori Drama =====
def display_drama_categories():
    global current_category_name, current_category_id
    
    while True:
        print("\n" + "="*60)
        print("🎬 PILIH KATEGORI DRAMA - DRAMABOX")
        print("="*60)
        print("\n📺 KATEGORI UTAMA:")
        print("1. Must-sees (Drama yang Wajib Ditonton)")
        print("2. Trending (Sedang Tren)")
        print("3. Hidden Gems (Drama Menarik)")
        
        print("\n🏷️ BERDASARKAN GENRE:")
        print("4. Romance (Romansa)")
        print("5. Urban (Kehidupan Kota)")
        print("6. Revenge (Balas Dendam)")
        print("7. Strong Female Lead (Wanita Tangguh)")
        print("8. Family Bonds (Ikatan Keluarga)")
        
        print("\n⚙️ ADVANCED:")
        print("9. Custom URL (Input Manual)")
        print("0. Keluar")
        print("="*60)

        choice = input("\nPilih kategori (0-9, default 1): ").strip()

        # Mapping kategori DramaBox
        category_map = {
            "1": {
                "url": "/in/more/must-sees",
                "name": "Must-sees"
            },
            "2": {
                "url": "/in/more/trending",
                "name": "Trending"
            },
            "3": {
                "url": "/in/more/hidden-gems",
                "name": "Hidden Gems"
            },
            "4": {
                "url": "/in/browse/447",
                "name": "Romance"
            },
            "5": {
                "url": "/in/browse/427",
                "name": "Urban"
            },
            "6": {
                "url": "/in/browse/458",
                "name": "Revenge"
            },
            "7": {
                "url": "/in/browse/463",
                "name": "Strong Female Lead"
            },
            "8": {
                "url": "/in/browse/464",
                "name": "Family Bonds"
            }
        }

        if choice == "0":
            print("\n💾 IMPORTANT: Jangan lupa backup file DramaBox.json!")
            print("📁 Gunakan perintah: cp DramaBox.json /sdcard/Download/")
            print("👋 Sampai jumpa lagi!...")
            sys.exit(0)
            
        elif choice == "9":
            # Custom URL
            print("\n🔧 CUSTOM URL")
            print("="*60)
            print("Contoh URL yang valid:")
            print("  • /in/more/must-sees")
            print("  • /in/browse/447")
            print("="*60)
            
            custom_url = input("\nMasukkan URL path: ").strip()
            
            if not custom_url:
                print("⚠️ URL kosong, kembali ke menu...")
                continue
                
            custom_name = input("Masukkan nama kategori: ").strip()
            
            if not custom_name:
                custom_name = "Custom Category"
                
            current_category_name = custom_name.title()
            current_category_id = generate_category_id(current_category_name)
            
            print(f"\n✅ Custom URL berhasil: {current_category_name}")
            return custom_url
            
        elif choice in category_map:
            category_data = category_map[choice]
            current_category_name = category_data["name"]
            current_category_id = generate_category_id(current_category_name)
            
            print(f"\n✅ Dipilih: {current_category_name}")
            print(f"🔗 URL: {category_data['url']}")
            
            return category_data["url"]
            
        elif choice == "":
            # Default ke Must-sees
            category_data = category_map["1"]
            current_category_name = category_data["name"]
            current_category_id = generate_category_id(current_category_name)
            
            print(f"\n✅ Default: {current_category_name}")
            return category_data["url"]
            
        else:
            print("❌ Pilihan tidak valid! Silakan pilih 0-9")
            time.sleep(1)
            continue

# ===== Display Info Kategori =====
def display_category_info(category_url):
    """Tampilkan info detail kategori yang dipilih"""
    print("\n📋 INFO KATEGORI:")
    print("="*60)
    print(f"📂 Nama      : {current_category_name}")
    print(f"🆔 ID        : {current_category_id}")
    print(f"🔗 URL       : {BASE_URL}{category_url.lstrip('/')}")
    print("="*60)

# ===== Cek duplikat =====
def is_duplicate(title, url):
    normalized_title = title.lower().strip()
    if normalized_title in processed_titles or url in processed_urls:
        return True
    processed_titles.add(normalized_title)
    processed_urls.add(url)
    return False

# ===== Extract drama info dari card =====
def extract_drama_info(drama_element):
    """Extract informasi dari drama card"""
    try:
        link_tag = drama_element.find('a', href=True)
        if not link_tag:
            return None
            
        link = link_tag['href']
        if not link.startswith('http'):
            link = BASE_URL.rstrip('/') + '/' + link.lstrip('/')

        # Extract title
        title = "No Title"
        
        # Cari di h2 class bookName
        title_tag = drama_element.find('h2', class_=re.compile('bookName'))
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # Fallback ke alt img
        if title == "No Title":
            img_tag = drama_element.find('img', alt=True)
            if img_tag:
                title = img_tag['alt']

        if is_duplicate(title, link):
            return None

        # Extract poster/cover
        poster = ""
        img_tag = drama_element.find('img')
        if img_tag:
            poster = img_tag.get('src', '')
            if not poster:
                poster = img_tag.get('data-src', '')
            
            if poster and not poster.startswith('http'):
                poster = BASE_URL.rstrip('/') + '/' + poster.lstrip('/')

        # Extract episode count
        episode_count = 0
        ep_tag = drama_element.find(text=re.compile(r'(\d+)\s*Episode', re.I))
        if ep_tag:
            ep_match = re.search(r'(\d+)', ep_tag)
            if ep_match:
                episode_count = int(ep_match.group(1))

        # Extract tags/genres
        tags = []
        tag_elements = drama_element.find_all('a', class_=re.compile('Tag|tag'))
        for tag_el in tag_elements:
            tag_text = tag_el.get_text(strip=True)
            if tag_text:
                tags.append(tag_text)

        print(f"📌 Ditemukan: {title}")
        return {
            "link": link,
            "title": title,
            "poster": poster,
            "episode_count": episode_count,
            "tags": tags
        }
        
    except Exception as e:
        print(f"❌ Error extracting drama info: {e}")
        return None

# ===== Find drama cards =====
def find_drama_cards(soup):
    """Mencari drama cards dengan multiple approach"""
    drama_elements = []
    
    print("🔍 Mencari drama cards...")
    
    # Method 1: Cari dengan class itemBox
    item_boxes = soup.find_all('div', class_=re.compile('itemBox'))
    if item_boxes:
        print(f"  ✓ Menemukan {len(item_boxes)} div dengan class 'itemBox'")
        drama_elements.extend(item_boxes)
    
    # Method 2: Cari dengan class firstListBox
    if not drama_elements:
        list_boxes = soup.find_all('div', class_=re.compile('firstListBox|listBox'))
        for box in list_boxes:
            items = box.find_all('div', class_=re.compile('itemBox'))
            if items:
                print(f"  ✓ Menemukan {len(items)} items di listBox")
                drama_elements.extend(items)
    
    # Method 3: Cari dengan pattern link drama
    if not drama_elements:
        print("  → Mencari dengan pattern link drama...")
        potential_containers = soup.find_all(['div', 'article'], class_=re.compile(r'(item|card|drama)'))
        for container in potential_containers:
            link = container.find('a', href=re.compile(r'/drama/\d+/'))
            img = container.find('img')
            if link and img:
                drama_elements.append(container)
        if drama_elements:
            print(f"  ✓ Menemukan {len(drama_elements)} containers dengan link drama")
    
    # Remove duplicates berdasarkan link
    seen_links = set()
    unique_elements = []
    for elem in drama_elements:
        link_tag = elem.find('a', href=True)
        if link_tag:
            link = link_tag['href']
            if link not in seen_links:
                seen_links.add(link)
                unique_elements.append(elem)
    
    print(f"🎯 Total drama cards unik: {len(unique_elements)}")
    
    return unique_elements

# ===== Extract drama detail dari halaman detail =====
def get_drama_detail(drama_link, title, poster, episode_count, tags, index):
    """Get detail drama dari halaman detail"""
    global success_count
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print(f"📖 Mengambil detail: {title}")
    
    try:
        response = requests.get(drama_link, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"  ❌ Gagal akses: {drama_link}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract description
        description = ""
        desc_selectors = [
            'p.intro',
            'div.introduction',
            'div.desc',
            'p[class*="intro"]'
        ]
        for selector in desc_selectors:
            desc_tag = soup.select_one(selector)
            if desc_tag:
                description = desc_tag.get_text(strip=True)
                if len(description) > 500:
                    description = description[:500] + "..."
                break
        
        if not description:
            description = f"{title} - Drama series available on DramaBox"
        
        # Extract rating
        rating = 7.5
        rating_tag = soup.find(text=re.compile(r'rating|score', re.I))
        if rating_tag:
            rating_match = re.search(r'(\d+\.?\d*)', rating_tag)
            if rating_match:
                try:
                    rating = float(rating_match.group(1))
                    if rating > 10:
                        rating = rating / 10
                except:
                    pass
        
        # Extract year
        year = 2024
        year_tag = soup.find(text=re.compile(r'20\d{2}'))
        if year_tag:
            year_match = re.search(r'(20\d{2})', year_tag)
            if year_match:
                year = int(year_match.group(1))
        
        # Extract genres (max 3)
        genres = tags[:3] if tags else ["Drama"]
        if len(genres) < 3:
            # Cari genre tambahan di halaman
            genre_links = soup.find_all('a', href=re.compile(r'/browse/\d+'))
            for link in genre_links:
                if len(genres) >= 3:
                    break
                genre_text = link.get_text(strip=True)
                if genre_text and genre_text not in genres:
                    genres.append(genre_text)
        
        # Extract episodes jika ada
        episodes = []
        if episode_count > 0:
            # Cari episode list di halaman
            episode_list = soup.find('div', class_=re.compile('episode'))
            if episode_list:
                episode_links = episode_list.find_all('a', href=True)
                for i, ep_link in enumerate(episode_links[:episode_count], 1):
                    ep_url = ep_link['href']
                    if not ep_url.startswith('http'):
                        ep_url = BASE_URL.rstrip('/') + '/' + ep_url.lstrip('/')
                    
                    episodes.append({
                        "episode": i,
                        "title": f"Episode {i}",
                        "duration": "5-10 min",
                        "streamUrl": ep_url
                    })
        
        drama_id = generate_drama_id(index)
        
        drama_data = {
            "id": drama_id,
            "title": title,
            "description": description,
            "poster": poster if poster else "https://via.placeholder.com/320x450",
            "backdrop": poster if poster else "https://via.placeholder.com/1280x720",
            "rating": round(rating, 1),
            "year": year,
            "genres": genres[:3],
            "type": "series" if episode_count > 1 else "movie",
            "episodeCount": episode_count
        }
        
        if episodes:
            drama_data["episodes"] = episodes
            print(f"  📺 {len(episodes)} episodes extracted")
        else:
            drama_data["streamUrl"] = drama_link
            print(f"  🎬 Drama link extracted")
        
        print(f"  ✅ Success")
        return drama_data
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

# ===== Save to M3U =====
def save_to_m3u_playlist(drama_data):
    global current_category_name
    try:
        with open("DramaBox.m3u", "a", encoding="utf-8") as f:
            if drama_data["type"] == "series" and "episodes" in drama_data:
                for episode in drama_data["episodes"]:
                    f.write(f'#EXTINF:-1 tvg-logo="{drama_data["poster"]}" group-title="{current_category_name}",{drama_data["title"]} - {episode["title"]}\n')
                    f.write(f"{episode['streamUrl']}\n")
            else:
                stream_url = drama_data.get('streamUrl', '')
                if stream_url:
                    f.write(f'#EXTINF:-1 tvg-logo="{drama_data["poster"]}" group-title="{current_category_name}",{drama_data["title"]}\n')
                    f.write(f"{stream_url}\n")
    except Exception as e:
        print(f"❌ Error saving to M3U: {e}")

# ===== Save to JSON =====
def save_to_json():
    global drama_data_list, current_category_name, current_category_id, all_categories_data
    
    try:
        category_exists = False
        for i, cat in enumerate(all_categories_data):
            if cat["id"] == current_category_id:
                all_categories_data[i] = {
                    "id": current_category_id,
                    "title": current_category_name,
                    "items": drama_data_list
                }
                category_exists = True
                print(f"📄 Updated existing category: {current_category_name}")
                break
        
        if not category_exists:
            all_categories_data.append({
                "id": current_category_id,
                "title": current_category_name,
                "items": drama_data_list
            })
            print(f"➕ Added new category: {current_category_name}")
        
        json_data = {
            "categories": all_categories_data
        }
        
        with open(JSON_FILENAME, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        total_dramas = sum(len(cat["items"]) for cat in all_categories_data)
        print(f"✅ Data disimpan: {len(all_categories_data)} kategori, {total_dramas} drama total")
        print(f"📄 File: {JSON_FILENAME}")
        return True
        
    except Exception as e:
        print(f"❌ Error menyimpan JSON: {str(e)}")
        return False

# ===== Progress bar =====
def progress_bar(current, total, title=""):
    percent = int((current / total) * 100)
    bar = "█" * (percent // 5) + "-" * (20 - (percent // 5))
    print(f"\r[{bar}] {percent}% ({current}/{total}) {title}", end="", flush=True)

# ===== Scrape drama page =====
def scrape_drama_page(url):
    global success_count
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'id,en-US;q=0.9,en;q=0.8',
        'Referer': BASE_URL
    }
    
    print(f"\n🌐 Scraping: {url}")
    
    try:
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"  ❌ Failed (Status: {res.status_code})")
            return False
            
        soup = BeautifulSoup(res.text, "html.parser")
        drama_elements = find_drama_cards(soup)
        
        if not drama_elements:
            print("  ❌ No drama cards found")
            return False

        total_dramas = len(drama_elements)
        saved_count = 0

        print(f"  📊 Found {total_dramas} dramas")

        for idx, drama_element in enumerate(drama_elements, start=1):
            drama_info = extract_drama_info(drama_element)
            if drama_info:
                print(f"\n  🎯 [{idx}/{total_dramas}] {drama_info['title']}")
                
                drama_detail = get_drama_detail(
                    drama_info['link'],
                    drama_info['title'],
                    drama_info['poster'],
                    drama_info['episode_count'],
                    drama_info['tags'],
                    success_count + 1
                )
                
                if drama_detail:
                    if export_format in ["m3u", "both"]:
                        save_to_m3u_playlist(drama_detail)
                    
                    if export_format in ["json", "both"]:
                        drama_data_list.append(drama_detail)
                    
                    success_count += 1
                    saved_count += 1
            
            progress_bar(idx, total_dramas, f"Processing {idx}/{total_dramas}")
            time.sleep(1)  # Delay untuk menghindari rate limit

        print(f"\n  ✅ Saved: {saved_count}/{total_dramas}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

# ===== Display Memory Status =====
def display_memory_status():
    """Tampilkan status data di memory"""
    if all_categories_data:
        print("\n" + "="*60)
        print("💾 DATA DI MEMORY (Session ini):")
        print("="*60)
        for cat in all_categories_data:
            print(f"  📂 {cat['title']}: {len(cat['items'])} dramas")
        total = sum(len(cat['items']) for cat in all_categories_data)
        print(f"  📊 Total: {len(all_categories_data)} kategori, {total} dramas")
        print("="*60)
        print("💡 Data ini akan tersimpan di DramaBox.json")
    else:
        print("\n💾 Belum ada data di memory (session baru)")

# ===== Display File Info =====
def display_file_info():
    """Tampilkan info file JSON yang ada"""
    if os.path.exists(JSON_FILENAME):
        try:
            file_size = os.path.getsize(JSON_FILENAME) / 1024
            
            with open(JSON_FILENAME, "r", encoding="utf-8") as f:
                data = json.load(f)
                categories = data.get("categories", [])
                total_dramas = sum(len(cat.get("items", [])) for cat in categories)
            
            print("\n" + "="*60)
            print(f"📄 FILE TERSIMPAN: {JSON_FILENAME}")
            print("="*60)
            print(f"  📦 Size      : {file_size:.2f} KB")
            print(f"  📂 Categories: {len(categories)}")
            print(f"  📊 Total Drama: {total_dramas}")
            print("="*60)
        except:
            pass

# ===== Main Function =====
def main():
    global success_count, drama_data_list
    
    print("=" * 60)
    print("🎬 DRAMABOX SCRAPER v1.0.0")
    print("📺 Created by : Ryuken (Modified)")
    print("🌐 Version    : 1.0.0 - DramaBox Indonesia")
    print("📢 Instagram  : Redpack.id")
    print("=" * 60)
    print("\033[1;33m⚠️ Disclaimer: Educational purposes only\033[0m")
    print("=" * 60)
    
    initialize_json()
    display_file_info()

    while True:
        display_memory_status()
        
        select_export_format()
        category_url = display_drama_categories()
        if not category_url:
            continue

        display_category_info(category_url)
        
        confirm = input("\n🤔 Continue? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', 'ya', '']:
            continue

        # Setup M3U jika diperlukan
        if export_format in ["m3u", "both"]:
            m3u_mode = "a" if os.path.exists("DramaBox.m3u") else "w"
            with open("DramaBox.m3u", m3u_mode, encoding="utf-8") as f:
                if m3u_mode == "w":
                    f.write("#EXTM3U\n")
                f.write(f"#PLAYLIST:DramaBox - {current_category_name}\n\n")
        
        # Reset data kategori saat ini
        drama_data_list = []
        success_count = 0
        processed_titles.clear()
        processed_urls.clear()

        print(f"\n🚀 Starting scrape...")
        print(f"📂 Category: {current_category_name}")
        print(f"💾 Format: {export_format.upper()}")
        print("="*60)
        
        final_confirm = input("\n⚠️ Start now? (y/n): ").strip().lower()
        if final_confirm not in ['y', 'yes', 'ya', '']:
            continue
        
        start_time = time.time()

        # Scrape URL (single page untuk kategori DramaBox)
        full_url = BASE_URL.rstrip('/') + category_url
        success = scrape_drama_page(full_url)

        end_time = time.time()
        duration = end_time - start_time

        # Simpan data ke JSON
        if export_format in ["json", "both"] and drama_data_list:
            print(f"\n💾 Saving {len(drama_data_list)} dramas to JSON...")
            save_to_json()

        print("\n" + "="*60)
        print("🎉 SCRAPING COMPLETE!")
        print("="*60)
        print(f"📂 Category : {current_category_name}")
        print(f"📊 Total    : {success_count} dramas")
        print(f"⏱️ Duration : {int(duration//60)}m {int(duration%60)}s")
        print(f"💾 Format   : {export_format.upper()}")
        
        if export_format in ["m3u", "both"] and os.path.exists("DramaBox.m3u"):
            size = os.path.getsize("DramaBox.m3u") / 1024
            print(f"📄 M3U     : DramaBox.m3u ({size:.2f} KB)")
        
        if export_format in ["json", "both"] and os.path.exists(JSON_FILENAME):
            size = os.path.getsize(JSON_FILENAME) / 1024
            total_categories = len(all_categories_data)
            total_dramas = sum(len(cat['items']) for cat in all_categories_data)
            print(f"📄 JSON    : {JSON_FILENAME} ({size:.2f} KB)")
            print(f"           {total_categories} categories, {total_dramas} total dramas")
        
        print("="*60)
        print("\n💡 TIPS BACKUP FILE:")
        print("  • Untuk Termux: cp DramaBox.json /sdcard/Download/")
        print("  • Untuk Telegram: cp DramaBox.json /sdcard/Download/Telegram/")
        print("="*60)
        
        repeat = input("\n🔄 Scrape another category? (y/n): ").strip().lower()
        if repeat not in ['y', 'yes', 'ya']:
            print("\n" + "="*60)
            print("💾 FINAL SUMMARY:")
            print("="*60)
            print(f"✅ Data tersimpan di: {JSON_FILENAME}")
            print(f"📊 Total: {len(all_categories_data)} kategori, {sum(len(cat['items']) for cat in all_categories_data)} dramas")
            print("\n💡 Backup dengan perintah:")
            print(f"   cp {JSON_FILENAME} /sdcard/Download/")
            print("="*60)
            print("\n👋 Thanks for using DramaBox Scraper!")
            print("📢 Follow @Redpack.id for updates!")
            break
        else:
            print("\n🔄 Kembali ke menu utama...")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopped by user (Ctrl+C)")
        if os.path.exists(JSON_FILENAME):
            size = os.path.getsize(JSON_FILENAME) / 1024
            print(f"💾 Data tersimpan di {JSON_FILENAME} ({size:.2f} KB)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)