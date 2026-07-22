import os
import html
import requests
from datetime import datetime

# 네이버 API 인증 정보 (GitHub Secrets / 환경변수에서 로드)
CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

# 수집할 키워드 목록
KEYWORDS = ["부동산", "인공지능", "반도체", "축구"]

def fetch_news(keyword):
    """네이버 뉴스 API를 통해 최신 뉴스 10건 수집"""
    if not CLIENT_ID or not CLIENT_SECRET:
        print(f"⚠️ 네이버 API Key가 설정되지 않았습니다. ({keyword})")
        return []
        
    url = f"https://openapi.naver.com/v1/search/news.json?query={keyword}&display=10&sort=date"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get('items', [])
            # HTML 태그 및 특수문자 정화 처리
            for item in items:
                item['title'] = html.unescape(item['title'].replace('<b>', '').replace('</b>', ''))
                item['description'] = html.unescape(item['description'].replace('<b>', '').replace('</b>', ''))
            return items
        else:
            print(f"❌ API 요청 실패 [{keyword}]: Status Code {res.status_code}")
            return []
    except Exception as e:
        print(f"❌ 예외 발생 [{keyword}]: {e}")
        return []

def generate_html(news_dict):
    """3개 키워드 뉴스 데이터를 기반으로 반응형 탭 구조의 HTML 생성"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 탭 버튼 HTML
    tab_buttons_html = ""
    # 탭 콘텐츠 HTML
    tab_contents_html = ""
    
    for idx, key in enumerate(KEYWORDS):
        active_class = "active" if idx == 0 else ""
        display_style = "block" if idx == 0 else "none"
        
        # 탭 버튼 생성
        tab_buttons_html += f"""
        <button class="tab-btn {active_class}" onclick="openTab(event, 'tab-{idx}')">{key}</button>
        """
        
        # 뉴스 리스트 HTML 생성
        items = news_dict.get(key, [])
        news_items_html = ""
        
        if items:
            for item in items:
                pub_date = item.get('pubDate', '')[:25] # 날짜 포맷 정리
                news_items_html += f"""
                <li class="news-item">
                    <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="news-title">{item['title']}</a>
                    <p class="news-desc">{item['description']}</p>
                    <span class="news-date">{pub_date}</span>
                </li>
                """
        else:
            news_items_html = "<li class='empty-msg'>수집된 뉴스가 없습니다.</li>"
            
        # 탭 콘텐츠 생성
        tab_contents_html += f"""
        <div id="tab-{idx}" class="tab-content" style="display: {display_style};">
            <ul class="news-list">
                {news_items_html}
            </ul>
        </div>
        """

    # 전체 HTML 템플릿 (1분 메타 리프레시 포함)
    html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- 60초(1분)마다 브라우저 자동 새로고침 -->
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
            margin-bottom: 20px;
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

        /* 📱 가로 스크롤 지원 탭 스타일 수정 영역 */
        .tab-container {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            overflow-x: auto;            /* 탭이 영역을 넘어가면 가로 스크롤 생성 */
            white-space: nowrap;         /* 탭 버튼 줄바꿈 방지 */
            -webkit-overflow-scrolling: touch; /* 모바일 부드러운 스크롤 */
            scrollbar-width: thin;       /* 파이어폭스 스크롤바 얇게 */
        }
        /* 스크롤바 감추기 원할 경우 사용 (선택 사항) */
        .tab-container::-webkit-scrollbar {
            height: 4px;                /* 가로 스크롤바 두께 */
        }
        .tab-container::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }
        .tab-btn {
            padding: 10px 16px;
            border: none;
            background: none;
            font-size: 15px;
            font-weight: bold;
            color: #666;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            flex-shrink: 0;             /* 탭 버튼 폭이 줄어들지 않고 유지되도록 설정 */
            white-space: nowrap;        /* 버튼 안의 글자 줄바꿈 강제 방지 */
        }
        .tab-btn:hover {
            color: var(--primary-color);
        }
        .tab-btn.active {
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
        }

        /* 뉴스 목록 스타일 */
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
            <div class="last-update">최종 업데이트: {now_str} (1분마다 자동 새로고침)</div>
        </header>

        <!-- 탭 버튼 영역 -->
        <div class="tab-container">
            {tab_buttons_html}
        </div>

        <!-- 탭 콘텐츠 영역 -->
        {tab_contents_html}
    </div>

    <script>
        function openTab(evt, tabId) {{
            // 모든 탭 내용 숨기기
            const tabContents = document.getElementsByClassName("tab-content");
            for (let i = 0; i < tabContents.length; i++) {{
                tabContents[i].style.display = "none";
            }}

            // 모든 탭 버튼 active 클래스 제거
            const tabBtns = document.getElementsByClassName("tab-btn");
            for (let i = 0; i < tabBtns.length; i++) {{
                tabBtns[i].className = tabBtns[i].className.replace(" active", "");
            }}

            // 선택된 탭 표시 및 버튼 활성화
            document.getElementById(tabId).style.display = "block";
            evt.currentTarget.className += " active";
        }}
    </script>
</body>
</html>
"""
    return html_template

def main():
    news_data = {}
    print("🚀 뉴스 데이터 수집을 시작합니다...")
    
    for key in KEYWORDS:
        print(f"🔍 '{key}' 키워드 수집 중...")
        news_data[key] = fetch_news(key)
        
    print("📝 index.html 파일을 생성합니다...")
    html_content = generate_html(news_data)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("✅ 성공적으로 index.html이 작성되었습니다!")

if __name__ == "__main__":
    main()
