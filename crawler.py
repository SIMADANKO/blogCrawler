import requests
import time
import json
import logging
from bs4 import BeautifulSoup
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_all_note_urls(username):
    """通过 API 获取所有 noteUrl 和标题"""
    page = 1
    all_articles = {}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    while True:
        # 构建 API 请求的 URL
        api_url = f"https://note.com/api/v2/creators/{username}/contents?kind=note&page={page}"

        # 发起 GET 请求
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"❌ 请求失败，错误: {e}")
            break

        # 解析 JSON 数据
        json_data = response.json()

        # 检查是否是最后一页
        is_last_page = json_data.get("data", {}).get("isLastPage", True)
        if is_last_page:
            print("✅ 已获取全部文章。")
            break

        # 获取页面中的所有文章数据
        notes = json_data.get("data", {}).get("contents", [])

        # 如果没有文章，跳出循环
        if not notes:
            print("✅ 没有更多文章，已获取全部数据。")
            break

        # 提取每篇文章的 noteUrl 和标题
        for item in notes:
            if isinstance(item, dict):
                note_url = item.get('noteUrl')
                title = item.get('name')
                publish_at = item.get('publishAt')
                if note_url and title:
                    print(f"Note URL: {note_url}, Title: {title}, Time: {publish_at}")
                    all_articles[note_url] = {
                        "title": title,
                        "url": note_url,
                        "timestamp": publish_at  # 加入时间戳
                    }
        # 下一页
        page += 1
        time.sleep(1)  # 防止请求过快被限制

    # 打印所有获取的文章链接和标题
    print(f"\n✅ 共找到 {len(all_articles)} 篇文章链接：\n")
    for i, (url, article) in enumerate(all_articles.items(), 1):
        print(f"{i:02d}: {article['url']} ({article['title']})")

    return all_articles


def get_article_content(url, timestamp):
    """访问文章 URL，提取正文内容并返回，保留原文格式"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"\n📥 正在访问文章: {url}")
    print(timestamp)

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ 请求失败，错误: {e}")
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    content_div = soup.find('div', {'data-name': 'body', 'class': 'note-common-styles__textnote-body'}) or \
                  soup.find('div', class_='o-noteContent__body')

    if content_div:
        content = content_div.get_text(separator='\n', strip=True)
        if timestamp:
            content = f"{timestamp}\n\n{content}"  # 将时间戳插入正文开头
        return content
    else:
        print("❌ 未找到正文内容\n")
        return None


def save_to_json(all_articles):
    """将文章的标题、正文内容和 URL 保存到 JSON 文件中"""
    results = {}

    for url, article in all_articles.items():
        title = article["title"]
        timestamp = article["timestamp"]
        content = get_article_content(url, timestamp)

        if content:
            results[f"{timestamp[:10]}-{title}"] = {
                "title": title,
                "text": content,
                "url": url
            }

    try:
        with open('note_articles.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("✅ 文章数据已保存到 note_articles.json")
    except Exception as e:
        print(f"❌ 保存 JSON 文件失败: {e}")


def main():
    # 指定用户名
    username = "saratoga623"

    # 获取所有 noteUrl 和标题
    articles = get_all_note_urls(username)

    # 保存到 JSON 文件
    save_to_json(articles)


if __name__ == "__main__":
    main()
