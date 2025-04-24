import time
import re
import os
import html
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def download_pdf(pdf_url, file_name):
    if os.path.exists(file_name):
        print(f"文件已存在，跳过下载：{file_name}")
        return
    try:
        resp = requests.get(pdf_url, timeout=15)
        resp.raise_for_status()
        with open(file_name, "wb") as f:
            f.write(resp.content)
        print(f"下载并重命名完成：{file_name}")
    except Exception as e:
        print(f"下载 {pdf_url} 时出错：{e}")

def parse_page_source(driver):
    page_source = driver.page_source
    decoded_html = html.unescape(page_source)
    return BeautifulSoup(decoded_html, "html.parser")

def process_detail_page(driver, detail_url):
    try:
        driver.get(detail_url)
        time.sleep(3)
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '.pdf')]"))
            )
        except Exception as e:
            print(f"等待 PDF 链接加载超时：{e}")
        soup = parse_page_source(driver)
        page_title = soup.title.get_text().strip() if soup.title else "untitled"
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "_", page_title)
        pdf_links = soup.find_all("a", href=re.compile(r"\.pdf"))
        if pdf_links:
            print(f"在详情页 {detail_url} 中找到 {len(pdf_links)} 个 PDF 链接。")
            if len(pdf_links) == 1:
                pdf_href = pdf_links[0].get("href")
                pdf_url = urljoin(detail_url, pdf_href)
                file_name = os.path.join("pdfs", f"{sanitized_title}.pdf")
                download_pdf(pdf_url, file_name)
            else:
                for idx, link in enumerate(pdf_links, 1):
                    pdf_href = link.get("href")
                    pdf_url = urljoin(detail_url, pdf_href)
                    file_name = os.path.join("pdfs", f"{sanitized_title}_{idx}.pdf")
                    download_pdf(pdf_url, file_name)
        else:
            print(f"详情页 {detail_url} 中未找到 PDF 链接。")
    except Exception as e:
        print(f"处理详情页 {detail_url} 时出错：{e}")

def main():
    os.makedirs("pdfs", exist_ok=True)
    base_url = "http://www.hbnavip.com/category?id=62"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    try:
        driver.get(base_url)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'动画片')]"))
            )
        except Exception as e:
            print("等待主页面动态内容加载超时或出错：", e)
        soup = parse_page_source(driver)
        anime_links = soup.find_all("a", string=re.compile("动画片"))
        if not anime_links:
            anime_links = [a for a in soup.find_all("a") if "动画片" in a.get_text()]
        if not anime_links:
            print("主页面中未找到包含 '动画片' 的链接。")
            return
        print(f"在主页面找到 {len(anime_links)} 个包含 '动画片' 的链接。")
        for link in anime_links:
            href = link.get("href")
            detail_url = urljoin(base_url, href)
            print(f"\n打开详情页：{detail_url}")
            process_detail_page(driver, detail_url)
    except Exception as e:
        print("处理主页面时出错：", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
