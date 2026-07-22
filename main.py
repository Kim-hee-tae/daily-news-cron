import urllib.request
import urllib.parse
import json
import os

# GitHub Secrets에서 네이버 API 키 가져오기
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

KEYWORD = "부동산"  # 검색할 기본 키워드
DISPLAY_COUNT = 15     # 가져올 기사 개수

def fetch_naver_news(keyword, count=10):
    query = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={count}&sort=date"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)

    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            articles = []
            
            for item in data['items']:
                clean_title = item['title'].replace('<b>', '').replace('</b>', '')\
                                          .replace('&quot;', '"').replace('&amp;', '&')\
                                          .replace('&lt;', '<').replace('&gt;', '>')
                
                clean_desc = item['description'].replace('<b>', '').replace('</b>', '')\
                                                .replace('&quot;', '"').replace('&amp;', '&')\
                                                .replace('&lt;', '<').replace('&gt;', '>')

                articles.append({
                    'title': clean_title,
                    'summary': clean_desc,
                    'link': item['link'],
                    'originallink': item['originallink'],
                    'pubDate': item['pubDate']
                })
            return articles
        else:
            print(f"API 호출 실패 코드: {response.getcode()}")
            return []
    except Exception as e:
        print(f"오류 발생: {e}")
        return []

def generate_html(articles, keyword):
    cards_html = ""
    for idx, item in enumerate(articles, 1):
        target_link = item['originallink'] if item['originallink'] else item['link']
        
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <span class="badge">{idx}</span>
                <span class="pub-date">{item['pubDate']}</span>
            </div>
            <h2 class="title">
                <a href="{target_link}" target="_blank" rel="noopener noreferrer">{item['title']}</a>
            </h2>
            <div class="summary-box">
                <p class="summary-text">{item['summary']}</p>
            </div>
            <div class="card-footer">
                <a href="{target_link}" target="_blank" class="link-btn">원문 기사 읽기 &rarr;</a>
            </div>
        </div>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>네이버 뉴스 브리핑 - {keyword}</title>
    <style>
        :root {{
            --naver-green: #03C75A;
            --bg-color: #f5f6f8;
            --card-bg: #ffffff;
            --text-main: #1e1e23;
            --text-sub: #606060;
            --border-color: #e4e8eb;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 30px 15px;
            display: flex;
            justify-content: center;
        }}
        .container {{ width: 100%; max-width: 800px; }}
        .header-title {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 3px solid var(--naver-green);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .keyword-tag {{ color: var(--naver-green); font-weight: bold; }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
        }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
        .badge {{
            background-color: var(--naver-green);
            color: white; font-size: 12px; font-weight: 700; padding: 3px 9px; border-radius: 12px;
        }}
        .pub-date {{ font-size: 12px; color: var(--text-sub); }}
        .title {{ font-size: 17px; margin: 0 0 12px 0; line-height: 1.4; }}
        .title a {{ color: var(--text-main); text-decoration: none; }}
        .title a:hover {{ color: var(--naver-green); }}
        .summary-box {{
            background-color: #f8f9fa;
            border-left: 4px solid var(--naver-green);
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 14px;
        }}
        .summary-text {{ margin: 0; font-size: 14px; color: var(--text-sub); line-height: 1.6; }}
        .card-footer {{ text-align: right; }}
        .link-btn {{ font-size: 13px; color: var(--naver-green); font-weight: 600; text-decoration: none; }}
        .link-btn:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-title">
            <span>네이버 뉴스 브리핑</span>
            <span class="keyword-tag">#{keyword}</span>
        </div>
        {cards_html}
    </div>
</body>
</html>
"""
    return full_html

if __name__ == "__main__":
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ API 키 설정이 완료되지 않았습니다.")
    else:
        articles = fetch_naver_news(KEYWORD, DISPLAY_COUNT)
        if articles:
            html_content = generate_html(articles, KEYWORD)
            # GitHub Pages의 기본 메인 페이지 파일명인 index.html로 저장
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("✅ index.html 생성 완료!")
