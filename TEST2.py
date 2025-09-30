import streamlit as st
import feedparser
import datetime
import json
import pandas as pd
from urllib.parse import quote

# Google News RSS URL 생성 함수
def get_google_news_rss_url(query, hl='ko', gl='KR', num_results=100):
    """
    Google News RSS URL을 생성합니다.
    - query: 검색 쿼리
    - hl: 언어 (ko: 한국어)
    - gl: 국가 (KR: 한국)
    - num_results: 결과 수
    """
    encoded_query = quote(query)
    base_url = "https://news.google.com/rss/search"
    params = f"?q={encoded_query}&hl={hl}&gl={gl}&ceid={gl}:{hl}&num={num_results}"
    return base_url + params

# RSS 피드 크롤링 및 기사 추출 함수
def crawl_news_articles(rss_url, max_articles=20):
    """
    Google News RSS 피드를 파싱하여 기사 목록을 반환합니다.
    - rss_url: RSS 피드 URL
    - max_articles: 최대 기사 수
    """
    feed = feedparser.parse(rss_url)
    
    if feed.bozo_exception:
        st.error(f"RSS 파싱 오류: {feed.bozo_exception}")
        return []
    
    articles = []
    for entry in feed.entries[:max_articles]:
        article = {
            'title': entry.get('title', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'summary': entry.get('summary', ''),
            'source': entry.get('source', {}).get('title', '') if 'source' in entry else '',
            'media_url': entry.get('media_content', [{}])[0].get('url', '') if 'media_content' in entry else ''
        }
        try:
            article['published_date'] = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            article['published_date'] = entry.published
        
        articles.append(article)
    
    return articles

# Streamlit 앱 메인 함수
def main():
    st.title("동반성장 지수 뉴스 크롤링 앱")
    st.markdown("""
    이 앱은 Google News RSS를 통해 동반성장 지수 평가 관련 기업 활동 뉴스를 크롤링합니다.  
    **동반성장 지수 평가**: 동반성장위원회의 실적평가와 공정거래위원회의 공정거래협약 이행평가 관련 뉴스를 검색합니다.
    """)

    # 기본 키워드 목록
    default_queries = [
        "동반성장 지수 기업 활동",
        "동반성장위원회 실적평가 기업",
        "공정거래협약 이행평가 기업",
        "중소기업 지원 대기업 뉴스",
        "공정거래 준수 기업 사례"
    ]

    # 사용자 입력
    st.subheader("검색 설정")
    query_input = st.text_input("검색 키워드 (쉼표로 구분하여 여러 키워드 입력 가능)", value=", ".join(default_queries))
    max_articles = st.slider("쿼리당 최대 기사 수", min_value=5, max_value=50, value=20)
    
    if st.button("뉴스 크롤링 시작"):
        queries = [q.strip() for q in query_input.split(",")]
        all_articles = []
        
        with st.spinner("뉴스 데이터를 크롤링 중입니다..."):
            for query in queries:
                st.write(f"크롤링 중: {query}")
                rss_url = get_google_news_rss_url(query)
                articles = crawl_news_articles(rss_url, max_articles)
                all_articles.extend(articles)
                st.write(f"  - {len(articles)}개 기사 수집")
        
        # 중복 제거
        seen_links = set()
        unique_articles = []
        for article in all_articles:
            if article['link'] not in seen_links:
                seen_links.add(article['link'])
                unique_articles.append(article)
        
        st.success(f"총 {len(unique_articles)}개 고유 기사 수집 완료")
        
        # 데이터프레임으로 변환
        if unique_articles:
            df = pd.DataFrame(unique_articles)
            df = df[['title', 'source', 'published_date', 'summary', 'link']]
            df.columns = ['제목', '출처', '게시일', '요약', '링크']
            
            # 테이블 출력
            st.subheader("크롤링 결과")
            st.dataframe(df, use_container_width=True)
            
            # JSON 파일 다운로드 버튼
            output_file = f"dongban_news_articles_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(unique_articles, f, ensure_ascii=False, indent=2)
            
            with open(output_file, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="JSON 파일 다운로드",
                    data=f,
                    file_name=output_file,
                    mime="application/json"
                )
        else:
            st.warning("수집된 기사가 없습니다. 키워드를 변경하거나 나중에 다시 시도하세요.")

if __name__ == "__main__":
    main()

# 실행 방법:
# 1. 필요한 라이브러리 설치:
#    pip install streamlit feedparser pandas
# 2. 이 파일을 저장 (예: app.py)
# 3. 터미널에서 실행: streamlit run app.py
# 4. 브라우저에서 표시되는 Streamlit 앱에서 키워드 입력 및 크롤링 실행
#
# 주의:
# - Google News RSS는 실시간 데이터로, 결과는 실행 시점에 따라 다를 수 있습니다.
# - Streamlit 앱은 로컬 환경 또는 배포된 서버에서 실행 가능.
# - 추가 필터링(예: 날짜 범위)은 RSS URL에 &as_qdr=d7 (최근 7일) 등을 추가하여 구현 가능.
