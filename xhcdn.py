import requests
import re
from bs4 import BeautifulSoup
import sys
import time
import threading
import itertools

# =============== INFORMASI PEMBUAT ==================
#  Script by      : Pusman TV
#  Version.       : XHCDN Pro
# Instagram   : Redpack.id
# ====================================================

BASE_URL = "https://id.xhamster.com/"
processed_titles = set()
processed_urls = set()
success_count = 0  # Hitung total konten berhasil

# ===== ANSI Color Codes untuk RGB Effect =====
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    
    @staticmethod
    def rgb_colors():
        """Generator untuk warna RGB berputar"""
        colors = [Colors.RED, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.MAGENTA]
        return itertools.cycle(colors)

# ===== Spinner Class dengan RGB Effect =====
class RGBSpinner:
    def __init__(self):
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.is_spinning = False
        self.spinner_thread = None
        self.current_text = ""
        self.colors = Colors.rgb_colors()
        
    def _spin(self):
        """Thread function untuk animasi spinner"""
        spinner = itertools.cycle(self.spinner_chars)
        while self.is_spinning:
            color = next(self.colors)
            char = next(spinner)
            sys.stdout.write(f'\r{color}{char}{Colors.RESET} {self.current_text}')
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self, text):
        """Mulai spinner dengan teks"""
        self.current_text = text
        self.is_spinning = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.daemon = True
        self.spinner_thread.start()
    
    def update(self, text):
        """Update teks spinner"""
        self.current_text = text
    
    def stop(self, success=True, final_text=""):
        """Stop spinner dengan status"""
        self.is_spinning = False
        if self.spinner_thread:
            self.spinner_thread.join()
        
        if success:
            symbol = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            symbol = f"{Colors.RED}✗{Colors.RESET}"
        
        sys.stdout.write(f'\r{symbol} {final_text}\n')
        sys.stdout.flush()

# ===== Generate URL yang Benar untuk XHAMSTER =====
def generate_page_url(base_category, page_num):
    """
    Generate URL yang benar berdasarkan pola XHAMSTER:
    - Halaman 1: /search/China
    - Halaman 2: /search/China?page=2  
    - Halaman 3: /search/China?page=3
    """
    if page_num == 1:
        # Halaman pertama tanpa suffix
        return BASE_URL + base_category
    else:
        # Halaman selanjutnya dengan ?page={page_num}
        return BASE_URL + base_category + f"?page={page_num}"

# ===== Validasi URL Video =====
def is_valid_video_url(url):
    """Validasi apakah URL adalah video yang valid"""
    if not url:
        return False
    
    # URL yang harus dihindari (profil, kategori, dll)
    invalid_patterns = [
        r'/[a-zA-Z-]+\d*$',  # Pattern seperti /hiroshi-tanaka1
        r'/user/',
        r'/profile/',
        r'/category/',
        r'/tag/',
        r'/pornstar/',
        r'/model/',
        r'/channel/',
        r'^https?://[^/]+/[a-zA-Z-]+\d*/?$'  # Domain + kata + angka
    ]
    
    for pattern in invalid_patterns:
        if re.search(pattern, url):
            return False
    
    # URL yang valid biasanya punya pattern tertentu
    valid_patterns = [
        r'/video/',
        r'/watch/',
        r'/v/',
        r'/embed/',
        r'\d+',  # Ada angka di path
        r'[a-f0-9]{8,}',  # Hash panjang
    ]
    
    for pattern in valid_patterns:
        if re.search(pattern, url):
            return True
    
    return False

def is_valid_direct_video_url(url):
    """Validasi apakah URL adalah direct video link"""
    if not url:
        return False
    
    # Harus mengandung ekstensi video atau streaming
    video_extensions = ['.mp4', '.m3u8', '.avi', '.mov', '.wmv', '.flv', '.webm']
    
    for ext in video_extensions:
        if ext in url.lower():
            return True
    
    return False

# ===== Test Poster URL =====
def test_poster_url(url):
    """Test apakah poster URL valid dengan HEAD request"""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

# ===== Menu Kategori =====
def display_categories():
    while True:
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== PILIH KATEGORI ==={Colors.RESET}")
        print("1. Today's selection (Default)")
        print("2. Asian")
        print("3. Asian Teen")
        print("4. Indonesia")
        print("5. Japanase Wife")
        print("6. Japan")
        print("7. Japan Uncensored")
        print("8. Jav")
        print("9. Chinese")
        print("10. China")
        print("11. Family")
        print("12. Big Tits")
        print("13. Hardcore")
        print("14. Teen")
        print("15. Blowjob")
        print("16. Cute")
        print("17. Anal")
        print("18. Cow Girl")
        print("19. Sex Toys")
        print("20. Milf")
        print("21. Doggy Style")
        print("22. Massage")
        print("23. Cumshot")
        print("24. Step Sister")
        print("25. Squirting")
        print("26. Custom Category")
        print("27. Kembali")
        print("0. Keluar")

        choice = input(f"\n{Colors.YELLOW}Pilih kategori (0-27, default 1): {Colors.RESET}").strip()

        category_map = {
            "1": "",
            "2": "search/asian",
            "3": "search/asian+teen",
            "4": "search/indonesia",
            "5": "search/japanese+wife",
            "6": "search/japanese+%E6%97%A5%E6%9C%AC+%E7%84%A1%E4%BF%AE%E6%AD%A3+%E9%AB%98%E7%94%BB%E8%B3%AA",
            "7": "search/uncensored+japanese+porn",
            "8": "search/best+jav",
            "9": "search/Chinese%20sex",     
            "10": "search/China",     
            "11": "search/familial_relations",
            "12": "search/big_tits",
            "13": "search/hardcore",
            "14": "search/teen",
            "15": "search/blowjob",
            "16": "search/cute",
            "17": "search/anal",
            "18": "search/cowgirl",
            "19": "search/sex_toys",
            "20": "search/milf",
            "21": "search/doggystyle",
            "22": "search/massage",
            "23": "search/cumshot",
            "24": "search/Step%20sister",
            "25": "search/squirting"
        }

        if choice == "0":
            print(f"{Colors.MAGENTA}👋 Sampai jumpa lagi!...{Colors.RESET}")
            sys.exit(0)
        elif choice == "27":
            return None
        elif choice == "26":
            custom_cat = input("Masukkan nama kategori: ").strip()
            return f"search/{custom_cat}"
        elif choice in category_map:
            return category_map[choice]
        else:
            return category_map["1"]

# ===== Cek duplikat =====
def is_duplicate(title, url):
    normalized_title = title.lower().strip()
    if normalized_title in processed_titles or url in processed_urls:
        return True
    processed_titles.add(normalized_title)
    processed_urls.add(url)
    return False

# ===== Ambil info video (DIPERBAIKI) =====
def extract_video_info(video_element):
    try:
        # Cari link
        link_tag = video_element.find('a', href=True)
        if not link_tag:
            all_links = video_element.find_all('a', href=True)
            if all_links:
                link_tag = all_links[0]
        
        if not link_tag:
            return None
            
        link = link_tag['href']
        
        # Pastikan URL lengkap
        if link.startswith('/'):
            link = BASE_URL.rstrip('/') + link
        elif not link.startswith('http'):
            link = BASE_URL + link
        
        if not is_valid_video_url(link):
            return None
        
        # ===== POSTER EXTRACTION =====
        poster = ""
        
        # Method 1: Cari img dan periksa berbagai atribut
        img_tag = video_element.find('img')
        
        if img_tag:
            poster_attrs = [
                'data-src', 'data-original', 'data-lazy', 'data-thumb', 
                'data-poster', 'data-image', 'data-lazy-src', 
                'data-srcset', 'data-url', 'data-big'
            ]
            
            for attr in poster_attrs:
                if img_tag.get(attr):
                    potential_poster = img_tag.get(attr)
                    if 'lightbox-blank.gif' not in potential_poster and 'blank' not in potential_poster.lower():
                        poster = potential_poster
                        break
            
            if not poster and img_tag.get('src'):
                src = img_tag.get('src')
                if 'lightbox-blank.gif' not in src and 'blank' not in src.lower():
                    poster = src
        
        # Method 2: Generate poster URL berdasarkan pattern
        if not poster:
            video_id_patterns = [
                r'/video-(\d+)/',
                r'/video/(\d+)/',
                r'/(\d+)/',
                r'/watch/(\d+)',
                r'video-(\d+)',
                r'v=(\d+)',
                r'/v/(\d+)'
            ]
            
            video_id = None
            for pattern in video_id_patterns:
                match = re.search(pattern, link)
                if match:
                    video_id = match.group(1)
                    break
            
            if video_id:
                possible_poster_patterns = [
                    f"https://static-cdn77.xnxx-cdn.com/videos/thumbs169ll/{video_id}.jpg",
                    f"https://static-cdn77.xnxx-cdn.com/videos/thumbs169lll/{video_id}.jpg",
                    f"https://static-cdn77.xnxx-cdn.com/videos/thumbs169/{video_id}.jpg",
                    f"https://static-cdn77.xnxx-cdn.com/videos/thumbs/{video_id}.jpg",
                ]
                
                for poster_url in possible_poster_patterns:
                    if test_poster_url(poster_url):
                        poster = poster_url
                        break
        
        # Method 3: Cari dari background-image
        if not poster:
            style_elements = video_element.find_all(['div', 'span', 'a'], style=True)
            for elem in style_elements:
                style = elem.get('style', '')
                if 'background-image' in style:
                    matches = re.findall(r'background-image\s*:\s*url\(["\']?([^"\'()]+)["\']?\)', style)
                    if matches:
                        bg_image = matches[0]
                        if 'lightbox-blank.gif' not in bg_image and 'blank' not in bg_image.lower():
                            poster = bg_image
                            break
        
        # Perbaiki URL poster
        if poster:
            if poster.startswith('//'):
                poster = 'https:' + poster
            elif poster.startswith('/'):
                poster = BASE_URL.rstrip('/') + poster
            elif not poster.startswith('http') and not poster.startswith('data:'):
                poster = BASE_URL + poster
        else:
            video_id_match = re.search(r'(\d+)', link)
            if video_id_match:
                video_id = video_id_match.group(1)
                poster = f"https://static-cdn77.xnxx-cdn.com/videos/thumbs169ll/{video_id}.jpg"
            else:
                poster = "https://via.placeholder.com/320x240/333333/ffffff?text=No+Preview"
        
        # ===== TITLE EXTRACTION =====
        title = ""
        
        if img_tag and img_tag.get('alt'):
            title = img_tag['alt'].strip()
        elif link_tag.get('title'):
            title = link_tag['title'].strip()
        elif link_tag.get_text(strip=True):
            title = link_tag.get_text(strip=True)
        else:
            text_elements = video_element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'p'])
            for elem in text_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 5:
                    title = text
                    break
            
            if not title:
                title = f"Video_{link.split('/')[-1]}"
        
        # Bersihkan title
        title = re.sub(r'[^\w\s\-.,()[\]{}]', '', title).strip()
        if len(title) > 100:
            title = title[:97] + "..."
        
        if is_duplicate(title, link):
            return None

        return {"link": link, "title": title, "poster": poster}
        
    except Exception as e:
        return None

# ===== Ambil link download (DIPERBAIKI dengan Spinner) =====
def make_second_request(video_link, title, poster):
    global success_count
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': BASE_URL,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    # Batasi panjang title untuk tampilan
    display_title = title[:60] + "..." if len(title) > 60 else title
    
    # Buat spinner
    spinner = RGBSpinner()
    spinner.start(f"Scraping: {display_title}")
    
    try:
        response = requests.get(video_link, headers=headers, timeout=20)
        if response.status_code != 200:
            spinner.stop(success=False, final_text=f"Failed (Status {response.status_code}): {display_title}")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        video_url = None

        # PERBAIKAN: Pattern yang lebih spesifik untuk video penuh, bukan preview
        patterns = [
            # High quality video patterns (avoid preview/thumb)
            r'https?://[^/]+\.(?:hamster|xhamster|xnxx|pornhub)-cdn\.com/[^"\'<>\s]*(?:1080p|720p|480p|hd|full)[^"\'<>\s]*\.(?:mp4|m3u8)[^"\'<>\s]*',
            # Avoid preview/thumb patterns specifically
            r'https?://[^/]+\.(?:hamster|xhamster)-cdn\.com/(?!.*(?:thumb|preview|sample))[^"\'<>\s]+\.(?:mp4|m3u8)[^"\'<>\s]*',
            # Look for main video files (longer URLs usually = full video)
            r'https?://[^/]+\.(?:hamster|xhamster)-cdn\.com/[^"\'<>\s]{50,}\.(?:mp4|m3u8)[^"\'<>\s]*',
            # Pattern untuk video dengan token/parameter (biasanya video asli)
            r'https?://[^/]+\.(?:hamster|xhamster)-cdn\.com/[^"\'<>\s]+\?[^"\'<>\s]*\.(?:mp4|m3u8)',
            # General pattern but prioritize longer URLs
            r'https?://[^\s"\'<>]+\.(?:mp4|m3u8)(?:\?[^\s"\'<>]*)?'
        ]
        
        found_urls = []
        
        # Method 1: Cari dalam script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                for pattern in patterns:
                    matches = re.findall(pattern, script.string, re.IGNORECASE)
                    for match in matches:
                        # Filter out obvious previews/samples
                        if not re.search(r'(thumb|preview|sample|trailer|teaser)', match, re.IGNORECASE):
                            found_urls.append((match, len(match)))  # Store with length for prioritization
        
        # Sort by URL length (longer URLs often = full videos)
        found_urls.sort(key=lambda x: x[1], reverse=True)
        
        # Validate found URLs
        for url, length in found_urls:
            if is_valid_direct_video_url(url):
                # Additional check: avoid URLs that are clearly previews
                if not re.search(r'(preview|sample|thumb|trailer|_short|_clip)', url, re.IGNORECASE):
                    video_url = url
                    break
        
        # Method 2: Look for video tag with longer sources
        if not video_url:
            video_tags = soup.find_all('video')
            for video_tag in video_tags:
                sources = [video_tag.get('src')] + [s.get('src') for s in video_tag.find_all('source')]
                sources = [s for s in sources if s]
                
                # Prioritize longer source URLs
                sources.sort(key=len, reverse=True)
                for src in sources:
                    if src and is_valid_direct_video_url(src) and len(src) > 50:
                        if not re.search(r'(preview|sample|thumb)', src, re.IGNORECASE):
                            video_url = src
                            break
                if video_url:
                    break
        
        # Method 3: Look in specific JavaScript variables
        if not video_url:
            js_video_patterns = [
                r'(?:videoUrl|mainVideo|fullVideo|playerUrl)\s*[=:]\s*["\']([^"\']+)["\']',
                r'sources\s*:\s*\[[^]]*["\']([^"\']*\.(?:mp4|m3u8)[^"\']*)["\']',
                r'file\s*:\s*["\']([^"\']*\.(?:mp4|m3u8)[^"\']*)["\']'
            ]
            
            for pattern in js_video_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    if is_valid_direct_video_url(match) and len(match) > 30:
                        if not re.search(r'(preview|sample|thumb)', match, re.IGNORECASE):
                            video_url = match
                            break
                if video_url:
                    break

        if not video_url:
            spinner.stop(success=False, final_text=f"No video URL found: {display_title}")
            return False

        # Ensure complete URL
        if video_url.startswith('//'):
            video_url = 'https:' + video_url
        elif video_url.startswith('/'):
            video_url = BASE_URL.rstrip('/') + video_url

        # Final validation - check if URL length suggests it's a full video
        if len(video_url) < 40:  # Very short URLs likely previews
            spinner.stop(success=False, final_text=f"URL too short (preview): {display_title}")
            return False

        if video_url in processed_urls:
            spinner.stop(success=False, final_text=f"Duplicate: {display_title}")
            return False

        processed_urls.add(video_url)
        save_to_playlist(title, video_url, poster)
        success_count += 1
        
        spinner.stop(success=True, final_text=f"Success: {display_title}")
        return True
        
    except Exception as e:
        spinner.stop(success=False, final_text=f"Error: {display_title}")
        return False

# ===== Simpan ke playlist =====
def save_to_playlist(title, url, poster):
    try:
        with open("Redpack.m3u", "a", encoding="utf-8") as f:
            f.write(f"#EXTINF:-1 tvg-logo=\"{poster}\",{title}\n")
            f.write(f"{url}\n\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Error menyimpan: {str(e)}{Colors.RESET}")

# ===== Cari jumlah halaman otomatis (DIPERBAIKI) =====
def get_max_pages(category_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    url = BASE_URL + category_url
    
    try:
        print(f"{Colors.CYAN}🔍 Mencari jumlah halaman maksimal...{Colors.RESET}")
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"{Colors.YELLOW}⚠️ Tidak dapat mengakses halaman, gunakan default 5{Colors.RESET}")
            return 5
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        max_page = 1
        
        # Method 1: Cari link dengan pattern /kategori/angka
        pagination_links = soup.find_all('a', href=True)
        page_numbers = []
        
        for link in pagination_links:
            href = link.get('href', '')
            
            # Pattern untuk Xhamster: ?page=angka
            if category_url in href or 'page=' in href:
                pattern = r'page=(\d+)'
                match = re.search(pattern, href)
                if match:
                    page_numbers.append(int(match.group(1)))
        
        # Method 2: Cari text angka di pagination area
        pagination_area = soup.find(['div', 'ul', 'nav'], class_=re.compile(r'pag|page'))
        if pagination_area:
            page_links = pagination_area.find_all('a')
            for link in page_links:
                text = link.get_text(strip=True)
                if text.isdigit():
                    page_numbers.append(int(text))
        
        if page_numbers:
            max_page = max(page_numbers)
            print(f"{Colors.GREEN}📊 Ditemukan maksimal {max_page} halaman{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}📊 Tidak ditemukan info pagination, gunakan default 10 halaman{Colors.RESET}")
            max_page = 10
        
        return max_page
        
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️ Error get_max_pages: {e}, gunakan default 10{Colors.RESET}")
        return 10

# ===== Scraping halaman (DIPERBAIKI) =====
def scrape_page(url, page_num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Referer': BASE_URL
    }
    
    try:
        print(f"{Colors.CYAN}🔍 Mengakses: {url}{Colors.RESET}")
        res = requests.get(url, headers=headers, timeout=20)
        if res.status_code != 200:
            print(f"{Colors.RED}✗ Status code: {res.status_code}{Colors.RESET}")
            return False
            
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Coba berbagai selector untuk menemukan video elements
        video_selectors = [
            'div.video-card',
            'div[class*="video"]',
            'div[class*="item"]',
            'div[class*="thumb"]',
            'article',
            '.video-item',
            '.thumb',
            '.item',
            'div[class*="post"]',
            'div[class*="content"]'
        ]
        
        video_elements = []
        used_selector = ""
        
        for selector in video_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"{Colors.GREEN}✓ Ditemukan {len(elements)} elemen dengan selector: {selector}{Colors.RESET}")
                video_elements = elements
                used_selector = selector
                break
        
        # Jika tidak ada yang ditemukan, coba cari semua div yang punya link video
        if not video_elements:
            print(f"{Colors.YELLOW}🔄 Mencoba metode alternatif...{Colors.RESET}")
            all_divs = soup.find_all('div')
            potential_elements = []
            for div in all_divs:
                link = div.find('a', href=True)
                if link and is_valid_video_url(link.get('href', '')):
                    potential_elements.append(div)
            video_elements = potential_elements
            print(f"{Colors.GREEN}📋 Ditemukan {len(video_elements)} div dengan link video valid{Colors.RESET}")
            used_selector = "div dengan link video valid"
        
        # Filter elemen yang benar-benar relevan
        if video_elements:
            filtered_elements = []
            for elem in video_elements:
                link = elem.find('a', href=True)
                if link and (elem.find('img') or is_valid_video_url(link.get('href', ''))):
                    filtered_elements.append(elem)
            video_elements = filtered_elements
            print(f"{Colors.GREEN}🎯 Setelah filter: {len(video_elements)} elemen relevan{Colors.RESET}")
        
        if not video_elements:
            print(f"{Colors.RED}✗ Tidak ditemukan elemen video di halaman ini{Colors.RESET}")
            return False

        total_videos = len(video_elements)
        saved_count = 0

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}📄 Halaman {page_num} | Ditemukan {total_videos} elemen dengan '{used_selector}'{Colors.RESET}\n")

        for idx, video_element in enumerate(video_elements, start=1):
            try:
                video_info = extract_video_info(video_element)
                if video_info:
                    ok = make_second_request(video_info['link'], video_info['title'], video_info['poster'])
                    if ok:
                        saved_count += 1
                    time.sleep(1)
                    
            except Exception as e:
                print(f"{Colors.RED}✗ Error processing elemen {idx}: {e}{Colors.RESET}")
                continue

        print(f"\n{Colors.BOLD}{Colors.CYAN}✓ Halaman {page_num} selesai | Total tersimpan: {saved_count}/{total_videos}{Colors.RESET}\n")
        return saved_count > 0
        
    except Exception as e:
        print(f"{Colors.RED}✗ Error scrape_page: {e}{Colors.RESET}")
        return False

# ===== Main (DIPERBAIKI) =====
def main():
    global success_count
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}🎬 PUSMAN SCRAPER - BUAT PLAYLIST M3U OTOMATIS{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}Created by.   : PUSMAN{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}Version       : 2.2 | Premium Edition (RGB Spinner){Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}Instagram  : Redpack.id{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")

    # Copyright & Disclaimer Info
    print(f"{Colors.MAGENTA}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}🎯 Script Scrape Xnxx{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}📜 Hak Cipta: Redpack - 2025{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'=' * 60}{Colors.RESET}")

    while True:
        category_url = display_categories()
        if not category_url:
            continue

        max_pages = get_max_pages(category_url)

        # Buat file baru
        with open("Redpack.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write("#PLAYLIST:Redpack - Xnxx Enhanced\n")
            f.write("#CREATED BY:Pusman\n\n")

        print(f"\n{Colors.CYAN}{Colors.BOLD}=== PILIH METODE SCRAPING ==={Colors.RESET}")
        print("1. Otomatis (semua halaman)")
        print("2. Tanyakan lanjut tiap halaman")
        print("3. Input manual jumlah halaman")
        method = input(f"{Colors.YELLOW}Pilih metode (1-3, default 1): {Colors.RESET}").strip() or "1"

        if method == "3":
            try:
                manual_pages = int(input(f"{Colors.YELLOW}Masukkan jumlah halaman (maks {max_pages}): {Colors.RESET}").strip())
                max_pages = min(manual_pages, max_pages)
            except:
                print(f"{Colors.YELLOW}Input tidak valid, gunakan otomatis.{Colors.RESET}")
                method = "1"

        print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 Mulai scraping... Total halaman: {max_pages}{Colors.RESET}")
        print(f"{Colors.GREEN}{Colors.BOLD}📂 Kategori: {category_url}{Colors.RESET}\n")
        
        # Reset counters
        success_count = 0
        processed_titles.clear()
        processed_urls.clear()

        # PERBAIKAN UTAMA: Loop dengan URL generation yang benar
        for page_num in range(1, max_pages + 1):
            print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*50}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}📄 MEMPROSES HALAMAN {page_num}/{max_pages}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*50}{Colors.RESET}")
            
            # PERBAIKAN: Generate URL yang benar sesuai pattern XNXX
            url = generate_page_url(category_url, page_num)
            
            print(f"{Colors.YELLOW}🔗 URL Halaman {page_num}: {url}{Colors.RESET}")
            
            # Scrape halaman ini
            success = scrape_page(url, page_num)
            
            # Tampilkan hasil halaman ini
            if success:
                print(f"{Colors.GREEN}✓ Halaman {page_num} berhasil di-scrape{Colors.RESET}")
            else:
                print(f"{Colors.RED}✗ Halaman {page_num} tidak berhasil di-scrape atau kosong{Colors.RESET}")
                
            print(f"{Colors.CYAN}📊 Progress keseluruhan: {success_count} video berhasil{Colors.RESET}")

            # Handle untuk metode 2 (tanyakan lanjut)
            if method == "2":
                if page_num < max_pages:
                    print(f"\n{Colors.GREEN}✓ Halaman {page_num} selesai diproses{Colors.RESET}")
                    while True:
                        lanjut = input(f"{Colors.YELLOW}Lanjut ke halaman {page_num + 1}? (y/n): {Colors.RESET}").strip().lower()
                        if lanjut in ['y', 'yes', 'ya']:
                            print(f"{Colors.GREEN}🚀 Melanjutkan ke halaman {page_num + 1}...{Colors.RESET}")
                            break
                        elif lanjut in ['n', 'no', 'tidak']:
                            print(f"{Colors.YELLOW}⏹️ Scraping dihentikan oleh pengguna{Colors.RESET}")
                            print(f"{Colors.CYAN}📊 Total halaman yang diproses: {page_num}{Colors.RESET}")
                            break
                        else:
                            print(f"{Colors.RED}❌ Input tidak valid. Gunakan 'y' atau 'n'{Colors.RESET}")
                    
                    if lanjut in ['n', 'no', 'tidak']:
                        break
            
            # Untuk metode 1 dan 3, lanjutkan otomatis dengan delay
            elif method in ["1", "3"]:
                if page_num < max_pages:
                    print(f"{Colors.YELLOW}⏳ Menunggu 2 detik sebelum melanjutkan ke halaman {page_num + 1}...{Colors.RESET}")
                    time.sleep(2)

        # Tampilkan summary akhir
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}🎉 SCRAPING SELESAI!{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}📊 Total konten berhasil di-scrape: {success_count}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}📄 Total halaman yang diproses: {page_num if 'page_num' in locals() else max_pages}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}💾 Nama File Playlist tersimpan: Redpack.m3u{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}👨‍💻 Script by: Pusman{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}📸 Instagram : Redpack.id{Colors.RESET}")   
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}\n")
        
        # Tanyakan apakah ingin scraping kategori lain
        repeat = input(f"{Colors.YELLOW}Scraping kategori lain? (y/n): {Colors.RESET}").strip().lower()
        if repeat not in ['y', 'yes', 'ya']:
            print(f"{Colors.MAGENTA}👋 Sampai jumpa lagi!{Colors.RESET}")
            break

if __name__ == "__main__":
    main()