#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동반성장 지수 평가 관련 뉴스 크롤링 Streamlit 애플리케이션
Google News RSS를 활용하여 동반성장 지수 평가 관련 뉴스를 수집하고 분석합니다.
"""

import streamlit as st
import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import csv
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin, urlparse
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import io

# 페이지 설정
st.set_page_config(
    page_title="동반성장 지수 평가 뉴스 크롤러",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

class NewsCrawler:
    def __init__(self):
        self.base_url = "https://news.google.com/rss"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 동반성장 지수 관련 키워드
        self.keywords = [
            "동반성장 지수",
            "동반성장위원회",
            "공정거래위원회",
            "공정거래협약",
            "실적평가",
            "이행평가",
            "동반성장 평가",
            "공정거래 평가",
            "중소기업 동반성장",
            "대기업 동반성장",
            "동반성장 지수 평가",
            "동반성장 실적",
            "공정거래 실적"
        ]
    
    def search_news(self, keyword, max_results=50):
        """Google News RSS에서 특정 키워드로 뉴스를 검색합니다."""
        try:
            search_url = f"{self.base_url}/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
            
            # RSS 피드 파싱
            feed = feedparser.parse(search_url)
            
            if not feed.entries:
                return []
            
            articles = []
            for entry in feed.entries[:max_results]:
                try:
                    article = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', ''),
                        'source': entry.get('source', {}).get('title', ''),
                        'keyword': keyword,
                        'crawled_at': datetime.now().isoformat()
                    }
                    
                    # URL 정규화
                    article['normalized_url'] = self.normalize_url(article['link'])
                    articles.append(article)
                    
                except Exception as e:
                    continue
            
            return articles
            
        except Exception as e:
            st.error(f"뉴스 검색 중 오류: {e}")
            return []
    
    def normalize_url(self, url):
        """URL을 정규화하여 중복을 방지합니다."""
        try:
            parsed = urlparse(url)
            return f"{parsed.netloc}{parsed.path}"
        except:
            return url
    
    def filter_relevant_news(self, articles):
        """동반성장 지수 평가와 관련된 뉴스만 필터링합니다."""
        relevant_keywords = [
            "동반성장", "공정거래", "실적평가", "이행평가", 
            "동반성장위원회", "공정거래위원회", "공정거래협약",
            "중소기업", "대기업", "지수", "평가"
        ]
        
        filtered_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            if any(keyword in title or keyword in summary for keyword in relevant_keywords):
                filtered_articles.append(article)
        
        return filtered_articles

def main():
    st.title("📰 동반성장 지수 평가 뉴스 크롤러")
    st.markdown("---")
    
    # 사이드바 설정
    st.sidebar.title("⚙️ 설정")
    
    # 크롤링 옵션
    st.sidebar.subheader("🔍 검색 옵션")
    max_results = st.sidebar.slider("키워드당 최대 뉴스 수", 10, 100, 30)
    selected_keywords = st.sidebar.multiselect(
        "검색할 키워드 선택",
        crawler.keywords,
        default=crawler.keywords[:5]
    )
    
    # 필터링 옵션
    st.sidebar.subheader("🔧 필터링 옵션")
    filter_relevant = st.sidebar.checkbox("관련 뉴스만 표시", value=True)
    remove_duplicates = st.sidebar.checkbox("중복 제거", value=True)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 뉴스 크롤링")
        
        if st.button("📡 뉴스 수집 시작", type="primary"):
            if not selected_keywords:
                st.warning("검색할 키워드를 선택해주세요.")
                return
            
            # 진행바
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_articles = []
            seen_urls = set()
            
            for i, keyword in enumerate(selected_keywords):
                status_text.text(f"검색 중: {keyword}")
                progress_bar.progress((i + 1) / len(selected_keywords))
                
                articles = crawler.search_news(keyword, max_results)
                
                for article in articles:
                    if remove_duplicates and article['normalized_url'] in seen_urls:
                        continue
                    if remove_duplicates:
                        seen_urls.add(article['normalized_url'])
                    all_articles.append(article)
                
                time.sleep(1)  # 요청 간격 조절
            
            # 필터링
            if filter_relevant:
                all_articles = crawler.filter_relevant_news(all_articles)
            
            # 세션 상태에 저장
            st.session_state['news_data'] = all_articles
            st.session_state['crawl_time'] = datetime.now()
            
            status_text.text("✅ 크롤링 완료!")
            progress_bar.progress(1.0)
            
            st.success(f"총 {len(all_articles)}개의 뉴스를 수집했습니다.")
    
    with col2:
        st.subheader("📊 통계")
        
        if 'news_data' in st.session_state:
            news_data = st.session_state['news_data']
            
            # 기본 통계
            st.metric("총 뉴스 수", len(news_data))
            
            # 키워드별 통계
            keyword_counts = Counter([article['keyword'] for article in news_data])
            st.write("**키워드별 뉴스 수:**")
            for keyword, count in keyword_counts.most_common(5):
                st.write(f"• {keyword}: {count}개")
            
            # 출처별 통계
            source_counts = Counter([article['source'] for article in news_data if article['source']])
            st.write("**주요 출처:**")
            for source, count in source_counts.most_common(3):
                st.write(f"• {source}: {count}개")
    
    # 뉴스 데이터 표시
    if 'news_data' in st.session_state and st.session_state['news_data']:
        st.markdown("---")
        st.subheader("📰 수집된 뉴스")
        
        # 검색 및 필터링
        search_term = st.text_input("🔍 뉴스 검색:", placeholder="제목이나 내용으로 검색...")
        
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            keyword_filter = st.selectbox("키워드 필터:", ["전체"] + list(set([article['keyword'] for article in st.session_state['news_data']])))
        
        with col_filter2:
            source_filter = st.selectbox("출처 필터:", ["전체"] + list(set([article['source'] for article in st.session_state['news_data'] if article['source']])))
        
        with col_filter3:
            sort_option = st.selectbox("정렬:", ["최신순", "제목순", "출처순"])
        
        # 데이터 필터링
        filtered_data = st.session_state['news_data'].copy()
        
        if search_term:
            filtered_data = [article for article in filtered_data 
                           if search_term.lower() in article['title'].lower() or 
                           search_term.lower() in article.get('summary', '').lower()]
        
        if keyword_filter != "전체":
            filtered_data = [article for article in filtered_data if article['keyword'] == keyword_filter]
        
        if source_filter != "전체":
            filtered_data = [article for article in filtered_data if article['source'] == source_filter]
        
        # 정렬
        if sort_option == "최신순":
            filtered_data.sort(key=lambda x: x.get('published', ''), reverse=True)
        elif sort_option == "제목순":
            filtered_data.sort(key=lambda x: x.get('title', ''))
        elif sort_option == "출처순":
            filtered_data.sort(key=lambda x: x.get('source', ''))
        
        # 페이지네이션
        items_per_page = 10
        total_pages = (len(filtered_data) + items_per_page - 1) // items_per_page
        current_page = st.selectbox("페이지:", range(1, total_pages + 1), index=0)
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered_data[start_idx:end_idx]
        
        # 뉴스 카드 표시
        for i, article in enumerate(page_data):
            with st.expander(f"📰 {article['title'][:80]}..."):
                col_info, col_link = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**출처:** {article['source']}")
                    st.write(f"**키워드:** {article['keyword']}")
                    st.write(f"**발행일:** {article['published']}")
                    
                    if article.get('summary'):
                        st.write(f"**요약:** {article['summary'][:200]}...")
                
                with col_link:
                    if st.button(f"🔗 링크", key=f"link_{i}"):
                        st.write(f"[기사 보기]({article['link']})")
        
        # 데이터 내보내기
        st.markdown("---")
        st.subheader("💾 데이터 내보내기")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            if st.button("📄 JSON 다운로드"):
                json_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="JSON 파일 다운로드",
                    data=json_data,
                    file_name=f"동반성장_뉴스_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col_export2:
            if st.button("📊 CSV 다운로드"):
                df = pd.DataFrame(filtered_data)
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=csv_data,
                    file_name=f"동반성장_뉴스_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_export3:
            if st.button("📈 Excel 다운로드"):
                df = pd.DataFrame(filtered_data)
                excel_buffer = io.BytesIO()
                df.to_excel(excel_buffer, index=False, engine='openpyxl')
                st.download_button(
                    label="Excel 파일 다운로드",
                    data=excel_buffer.getvalue(),
                    file_name=f"동반성장_뉴스_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # 시각화
    if 'news_data' in st.session_state and st.session_state['news_data']:
        st.markdown("---")
        st.subheader("📊 데이터 시각화")
        
        news_data = st.session_state['news_data']
        df = pd.DataFrame(news_data)
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            # 키워드별 뉴스 수 차트
            keyword_counts = df['keyword'].value_counts()
            fig1 = px.bar(
                x=keyword_counts.index, 
                y=keyword_counts.values,
                title="키워드별 뉴스 수",
                labels={'x': '키워드', 'y': '뉴스 수'}
            )
            fig1.update_xaxis(tickangle=45)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_viz2:
            # 출처별 뉴스 수 차트
            source_counts = df['source'].value_counts().head(10)
            fig2 = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title="주요 출처별 뉴스 비율"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # 시간별 뉴스 트렌드
        if len(news_data) > 0:
            st.subheader("📈 시간별 뉴스 트렌드")
            
            # 발행일 파싱 및 그룹화
            df['published_date'] = pd.to_datetime(df['published'], errors='coerce')
            df['date'] = df['published_date'].dt.date
            
            daily_counts = df.groupby('date').size().reset_index(name='count')
            
            if not daily_counts.empty:
                fig3 = px.line(
                    daily_counts, 
                    x='date', 
                    y='count',
                    title="일별 뉴스 수 트렌드"
                )
                st.plotly_chart(fig3, use_container_width=True)

# 전역 변수
crawler = NewsCrawler()

if __name__ == "__main__":
    main()
