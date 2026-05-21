import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def fetch_github_trending():
    url = "https://github.com/trending?since=daily"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"无法访问 GitHub Trending, 状态码: {response.status_code}")
        
    soup = BeautifulSoup(response.text, 'html.parser')
    repo_list = soup.find_all('article', class_='Box-row', limit=10) # 严格限制前10名
    
    trending_data = []
    for index, repo in enumerate(repo_list, 1):
        # 提取项目名 (格式通常是: 作者 / 项目名)
        title_box = repo.find('h2', class_='h3')
        repo_name = title_box.text.strip().replace('\n', '').replace(' ', '')
        
        # 提取项目描述
        desc_box = repo.find('p', class_='col-9')
        desc = desc_box.text.strip() if desc_box else "暂无描述 (No description provided)."
        
        # 提取主要开发语言
        lang_box = repo.find('span', itemprop='programmingLanguage')
        lang = lang_box.text.strip() if lang_box else "Markdown/Other"
        
        # 提取今日增长的 Star 数
        stars_today_box = repo.find('span', class_='d-inline-block float-sm-right')
        stars_today = stars_today_box.text.strip() if stars_today_box else "0 stars today"
        
        trending_data.append({
            "rank": index,
            "name": repo_name,
            "desc": desc,
            "lang": lang,
            "stars_today": stars_today,
            "url": f"https://github.com/{repo_name}"
        })
    return trending_data

def generate_readme(data):
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 构建 Markdown 内容
    markdown_content = f"""# 🚀 GitHub Daily Trending Top 10

> 💡 **技术博主每日报**：自动追踪 GitHub 全球每日最热门的 10 个开源项目。
> 📅 **更新时间**：{today_str} (🤖 系统自动更新)

---

### 🔥 今日热门项目排行榜

| 排名 | 项目名称与链接 | 主要语言 | 今日增长 | 项目简介 |
| :---: | :--- | :---: | :---: | :--- |
"""
    
    for item in data:
        markdown_content += f"| **{item['rank']}** | [{item['name']}]({item['url']}) | `{item['lang']}` | 🔥 {item['stars_today']} | {item['desc']} |\n"
        
    markdown_content += """
---

### 🛠️ 关于本项目
- 本项目完全基于 **GitHub Actions** 实现无人值守的每日自动爬取与更新。
- 如果对你有帮助，欢迎 **Star** 本仓库获取每日推送！ 
"""
    
    # 写入文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("README.md 渲染成功！")

if __name__ == "__main__":
    try:
        print("开始抓取 GitHub Trending...")
        data = fetch_github_trending()
        print(f"抓取成功，共获取 {len(data)} 个项目。")
        generate_readme(data)
    except Exception as e:
        print(f"运行出错: {e}")
