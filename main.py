import os
import html
import requests
from datetime import datetime, timezone, timedelta

# 네이버 API 인증 정보
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

# 수집할 키워드 목록
KEYWORDS = ["부동산", "인공지능", "반도체", "축구"]

def fetch_news(keyword):
    """네이버 뉴스 API 수집"""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("⚠️ 네이버 API Key가 설정되지 않았습니다.")
        return []
        
    url = "https://openapi.naver.com/v1/search/news.json?query=" + keyword + "&display=10&sort=date"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get('items', [])
            for item in items:
                item['title'] = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
                item['description'] = html.unescape(item['description'].replace('<b>', '').replace('</b>', ''))
            return items
        return []
    except Exception as e:
        print("❌ 예외 발생:", e)
        return []

def generate_html(news_dict):
    # 한국 표준시(KST = UTC + 9시간) 계산
    kst = timezone(timedelta(hours=9))
    now_str = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    
    tab_buttons = ""
    tab_contents = ""
    
    # 쿠팡 배너 HTML 템플릿 (목록 중간 및 공정위 문구 포함)
    coupang_banner_html = """
    <li class="news-item coupang-banner-item">
        <script src="https://ads-partners.coupang.com/g.js"></script>
        <script>
            new PartnersCoupang.G({"id":1009386,"template":"carousel","trackingCode":"AF8714635","width":"680","height":"140","tsource":""});
        </script>
        
    </li>
    """
    
    for idx, key in enumerate(KEYWORDS):
        active_class = "active" if idx == 0 else ""
        display_style = "block" if idx == 0 else "none"
        
        # 탭 버튼 생성
        tab_buttons += '<button class="tab-btn ' + active_class + '" onclick="openTab(event, \'tab-' + str(idx) + '\')">' + key + '</button>\n'
        
        # 뉴스 리스트 생성
        items = news_dict.get(key, [])
        news_items = ""
        
        if items:
            for item_idx, item in enumerate(items):
                pub_date = item.get('pubDate', '')[:25]
                news_items += '<li class="news-item">'
                news_items += '  <a href="' + item['link'] + '" target="_blank" rel="noopener noreferrer" class="news-title">' + item['title'] + '</a>'
                news_items += '  <p class="news-desc">' + item['description'] + '</p>'
                news_items += '  <span class="news-date">' + pub_date + '</span>'
                news_items += '</li>\n'
                
                # 5번째 뉴스(인덱스 4) 바로 뒤에 쿠팡 배너 삽입
                if item_idx == 4:
                    news_items += coupang_banner_html
        else:
            news_items = '<li class="empty-msg">수집된 뉴스가 없습니다.</li>'
            
        tab_contents += '<div id="tab-' + str(idx) + '" class="tab-content" style="display: ' + display_style + ';">'
        tab_contents += '  <ul class="news-list">' + news_items + '</ul>'
        tab_contents += '</div>\n'

    html_template = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>Daily Naver News Briefing</title>
    <style>
        :root {
            --primary-color: #03c75a;
            --bg-color: #f5f6f7;
            --card-bg: #ffffff;
            --text-color: #202020;
            --border-color: #e4e8eb;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        header {
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 15px;
            margin-bottom: 15px;
        }
        h1 {
            margin: 0 0 8px 0;
            font-size: 24px;
            color: var(--primary-color);
        }
        .last-update {
            font-size: 13px;
            color: #888;
        }
        /* [수정] 탭 메뉴를 상단에 고정 (Sticky) */
        .tab-container {
            position: sticky;
            top: 0;
            background-color: var(--card-bg);
            z-index: 100;
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            padding-top: 5px;
            margin-bottom: 10px;
            overflow-x: auto;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: thin;
        }
        .tab-container::-webkit-scrollbar {
            height: 4px;
        }
        .tab-container::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }
        .tab-btn {
            padding: 12px 16px;
            border: none;
            background: none;
            font-size: 15px;
            font-weight: bold;
            color: #666;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            flex-shrink: 0;
            white-space: nowrap;
        }
        .tab-btn:hover {
            color: var(--primary-color);
        }
        .tab-btn.active {
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
        }
        .news-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .news-item {
            padding: 16px 0;
            border-bottom: 1px solid var(--border-color);
        }
        .news-item:last-child {
            border-bottom: none;
        }
        .news-title {
            font-size: 17px;
            font-weight: 600;
            color: #1e1e1e;
            text-decoration: none;
            display: block;
            margin-bottom: 6px;
            line-height: 1.4;
        }
        .news-title:hover {
            color: var(--primary-color);
            text-decoration: underline;
        }
        .news-desc {
            font-size: 14px;
            color: #555;
            margin: 0 0 8px 0;
            line-height: 1.5;
        }
        .news-date {
            font-size: 12px;
            color: #999;
        }
        /* [추가] 쿠팡 배너 아이템 스타일링 */
        .coupang-banner-item {
            text-align: center;
            background-color: #f9f9f9;
            padding: 15px 10px;
            margin: 10px 0;
            border-radius: 8px;
            overflow: hidden;
        }
        .coupang-notice {
            font-size: 11px;
            color: #888888;
            margin: 6px 0 0 0;
        }
        .empty-msg {
            padding: 30px 0;
            text-align: center;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 뉴스 브리핑</h1>
            <div class="last-update">최종 업데이트: __NOW_STR__ (KST) (1분마다 자동 새로고침)</div>
        </header>

        <div class="tab-container">
            __TAB_BUTTONS__
        </div>

        __TAB_CONTENTS__
    </div>

    <script>
        function openTab(evt, tabId) {
            var tabContents = document.getElementsByClassName("tab-content");
            for (var i = 0; i < tabContents.length; i++) {
                tabContents[i].style.display = "none";
            }

            var tabBtns = document.getElementsByClassName("tab-btn");
            for (var i = 0; i < tabBtns.length; i++) {
                tabBtns[i].className = tabBtns[i].className.replace(" active", "");
            }

            document.getElementById(tabId).style.display = "block";
            evt.currentTarget.className += " active";
        }
    </script>
</body>
</html>
"""

    html_content = html_template.replace("__NOW_STR__", now_str)
    html_content = html_content.replace("__TAB_BUTTONS__", tab_buttons)
    html_content = html_content.replace("__TAB_CONTENTS__", tab_contents)

    return html_content

def main():
    news_data = {}
    print("🚀 뉴스 데이터 수집을 시작합니다...")
    
    for key in KEYWORDS:
        print("🔍 '" + key + "' 키워드 수집 중...")
        news_data[key] = fetch_news(key)
        
    print("📝 index.html 파일을 생성합니다...")
    html_content = generate_html(news_data)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("✅ 성공적으로 index.html이 작성되었습니다!")

if __name__ == "__main__":
    main()
