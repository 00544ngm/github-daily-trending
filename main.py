import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def translate_to_zh(text):
    """将英文简介翻译为中文，如果失败则返回原英文"""
    if not text or text == "暂无描述" or text.startswith("暂无描述"):
        return "暂无描述"
    try:
        # 使用 Google 翻译免密通道，将英文转为简中
        translated = GoogleTranslator(source='en', target='zh-CN').translate(text)
        return translated
    except Exception as e:
        print(f"⚠️ 翻译失败: {e}")
        return text

def fetch_github_trending():
    url = "https://github.com/trending?since=daily"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"无法访问 GitHub Trending, 状态码: {response.status_code}")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    repo_list = soup.find_all('article', class_='Box-row', limit=10)
    
    trending_data = []
    for index, repo in enumerate(repo_list, 1):
        title_box = repo.find('h2', class_='h3')
        repo_name = title_box.text.strip().replace('\n', '').replace(' ', '')
        
        desc_box = repo.find('p', class_='col-9')
        desc_en = desc_box.text.strip() if desc_box else "No description provided."
        
        print(f"正在翻译趋势榜 No.{index}: {repo_name}...")
        desc_zh = translate_to_zh(desc_en)
        
        lang_box = repo.find('span', itemprop='programmingLanguage')
        lang = lang_box.text.strip() if lang_box else "Markdown/Other"
        
        stars_today_box = repo.find('span', class_='d-inline-block float-sm-right')
        stars_today = stars_today_box.text.strip() if stars_today_box else "0 stars today"
        
        trending_data.append({
            "rank": index, 
            "name": repo_name, 
            "desc_zh": desc_zh, 
            "desc_en": desc_en, 
            "lang": lang, 
            "stars_today": stars_today, 
            "url": f"https://github.com/{repo_name}"
        })
    return trending_data

def fetch_most_stars():
    url = "https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc&per_page=10"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"⚠️ 总星榜获取失败，状态码: {response.status_code}")
        return []
        
    items = response.json().get('items', [])
    most_stars_data = []
    for index, item in enumerate(items, 1):
        repo_name = item.get('full_name')
        desc_en = item.get('description') or "No description provided."
        
        print(f"正在翻译总星榜 No.{index}: {repo_name}...")
        desc_zh = translate_to_zh(desc_en)
        
        stars_count = item.get('stargazers_count', 0)
        stars_formatted = f"{stars_count/1000:.1f}k" if stars_count > 1000 else str(stars_count)
        
        most_stars_data.append({
            "rank": index,
            "name": repo_name,
            "desc_zh": desc_zh,
            "desc_en": desc_en,
            "lang": item.get('language') or "Markdown/Other",
            "stars_total": stars_formatted,
            "url": item.get('html_url')
        })
    return most_stars_data

def generate_readme(trending_data, most_stars_data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    markdown_content = f"""# 🚀 GitHub 双维度技术日报

> 💡 **技术博主每日报**：全自动追踪 GitHub 全球趋势与历史巅峰，助你一眼看穿“谁当下最火”与“谁历史最强”。
> 📅 **更新时间**：{today_str} (🤖 系统全自动无人值守更新 - 包含 AI 自动翻译)

---

## 🔥 榜单一：今日热门爆发项目（过去 24 小时 Star 增长最多）
*💡 代表当前技术圈最新爆发的财富密码、新工具、新框架。*

| 排名 | 项目名称与链接 | 主要语言 | 今日增长 | 项目简介 (中/英) |
| :---: | :--- | :---: | :---: | :--- |
"""
    
    for item in trending_data:
        markdown_content += f"| **{item['rank']}** | [{item['name']}]({item['url']}) | `{item['lang']}` | 🔥 {item['stars_today']} | **{item['desc_zh']}** <br><sub style='color:gray'>{item['desc_en']}</sub> |\n"
        
    markdown_content += """
---

## 👑 榜单二：全球开源巅峰巨头（历史总 Star 最多榜 Top 10）
*💡 代表整个计算机世界里最稳固、沉淀最深、影响最广的行业基石。*

| 排名 | 项目名称与链接 | 主要语言 | 历史总星数 | 项目简介 (中/英) |
| :---: | :--- | :---: | :---: | :--- |
"""
    
    if most_stars_data:
        for item in most_stars_data:
            markdown_content += f"| **{item['rank']}** | [{item['name']}]({item['url']}) | `{item['lang']}` | ⭐ **{item['stars_total']}** | **{item['desc_zh']}** <br><sub style='color:gray'>{item['desc_en']}</sub> |\n"
    else:
        markdown_content += "| - | 暂未获取到数据，请查看 API 限制 | - | - | - |\n"

    markdown_content += """
---

### 🛠️ 关于本项目
- 本项目完全基于 **GitHub Actions** 实现每日自动爬取、翻译与双榜更新。
- 如果对你有帮助，欢迎 **Star** 本仓库获取每日持续推送！ 
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("README.md 双榜中英对照版渲染成功！")

if __name__ == "__main__":
    try:
        print("1. 开始抓取今日趋势榜...")
        trending_data = fetch_github_trending()
        
        print("2. 开始获取全球总星榜...")
        most_stars_data = fetch_most_stars()
        
        print("3. 开始合并生成双榜 README...")
        generate_readme(trending_data, most_stars_data)
    except Exception as e:
        print(f"运行出错: {e}")
