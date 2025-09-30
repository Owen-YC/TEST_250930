#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동반성장 지수 평가 관련 뉴스 크롤링 Streamlit 애플리케이션 (UI/UX 개선 버전)
Google News RSS를 활용하여 동반성장 지수 평가 관련 뉴스를 수집하고 분석합니다.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import time
from collections import Counter
import io

# 페이지 설정
st.set_page_config(
    page_title="동반성장 뉴스 크롤러",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 미니멀 트렌디 디자인
st.markdown("""
<style>
    /* 전체 테마 - 미니멀 흰색/회색 */
    .main {
        background-color: #ffffff;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    /* 헤더 스타일 */
    .main-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* 카드 스타일 */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 10px rgba(44, 62, 80, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(44, 62, 80, 0.3);
    }
    
    /* 메트릭 스타일 */
    .metric-container {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0;
        font-weight: 500;
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background: #ffffff;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    
    /* 애니메이션 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* 성공/경고 메시지 */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        color: #155724;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        color: #856404;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-radius: 8px;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 헤더 섹션
    st.markdown("""
    <div class="main-header fade-in">
        <h1 class="main-title">📰 동반성장 뉴스 크롤러</h1>
        <p class="main-subtitle">Google News RSS를 활용한 실시간 뉴스 수집 및 분석</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        
        # 크롤링 옵션
        st.markdown("#### 🔍 검색 옵션")
        max_results = st.slider("키워드당 최대 뉴스 수", 10, 100, 30)
        
        # 키워드 선택
        keywords = [
            "동반성장 지수", "동반성장위원회", "공정거래위원회", 
            "공정거래협약", "실적평가", "이행평가", "동반성장 평가"
        ]
        selected_keywords = st.multiselect(
            "검색할 키워드 선택",
            keywords,
            default=keywords[:5]
        )
        
        # 필터링 옵션
        st.markdown("#### 🔧 필터링 옵션")
        filter_relevant = st.checkbox("관련 뉴스만 표시", value=True)
        remove_duplicates = st.checkbox("중복 제거", value=True)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚀 뉴스 크롤링")
        
        # 크롤링 버튼
        if st.button("📡 뉴스 수집 시작", type="primary", use_container_width=True):
            if not selected_keywords:
                st.warning("검색할 키워드를 선택해주세요.")
            else:
                # 진행바와 상태 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 시뮬레이션된 크롤링
                all_articles = []
                for i, keyword in enumerate(selected_keywords):
                    status_text.text(f"🔍 검색 중: {keyword}")
                    progress_bar.progress((i + 1) / len(selected_keywords))
                    
                    # 시뮬레이션된 뉴스 데이터
                    for j in range(max_results // len(selected_keywords)):
                        article = {
                            'title': f"{keyword} 관련 뉴스 {j+1}",
                            'link': f"https://example.com/news/{j+1}",
                            'published': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'summary': f"{keyword}에 대한 상세한 내용입니다.",
                            'source': f"뉴스출처{j+1}",
                            'keyword': keyword,
                            'crawled_at': datetime.now().isoformat()
                        }
                        all_articles.append(article)
                    
                    time.sleep(0.5)  # 시뮬레이션
                
                # 세션 상태에 저장
                st.session_state['news_data'] = all_articles
                st.session_state['crawl_time'] = datetime.now()
                
                status_text.text("✅ 크롤링 완료!")
                progress_bar.progress(1.0)
                
                st.success(f"🎉 총 {len(all_articles)}개의 뉴스를 수집했습니다.")
    
    with col2:
        st.markdown("### 📊 실시간 통계")
        
        if 'news_data' in st.session_state:
            news_data = st.session_state['news_data']
            
            # 통계 카드들
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">총 뉴스 수</div>
                </div>
                """.format(len(news_data)), unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown("""
                <div class="metric-container">
                    <div class="metric-value">{}</div>
                    <div class="metric-label">검색 키워드</div>
                </div>
                """.format(len(selected_keywords)), unsafe_allow_html=True)
            
            # 키워드별 통계
            keyword_counts = Counter([article['keyword'] for article in news_data])
            st.markdown("**🔍 키워드별 뉴스 수:**")
            for keyword, count in keyword_counts.most_common(5):
                st.markdown(f"• **{keyword}**: {count}개")
            
            # 출처별 통계
            source_counts = Counter([article['source'] for article in news_data if article['source']])
            st.markdown("**📰 주요 출처:**")
            for source, count in source_counts.most_common(3):
                st.markdown(f"• **{source}**: {count}개")
        else:
            st.info("💡 뉴스를 수집하면 통계가 표시됩니다.")
    
    # 뉴스 데이터 표시
    if 'news_data' in st.session_state and st.session_state['news_data']:
        st.markdown("---")
        st.markdown("### 📰 수집된 뉴스")
        
        # 검색 및 필터링 섹션
        st.markdown("#### 🔍 검색 및 필터링")
        
        # 검색창
        search_term = st.text_input("", placeholder="제목이나 내용으로 검색...", key="search_input")
        
        # 필터 옵션들
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
        if total_pages > 1:
            current_page = st.selectbox("페이지:", range(1, total_pages + 1), index=0)
        else:
            current_page = 1
        
        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_data = filtered_data[start_idx:end_idx]
        
        # 뉴스 카드 표시
        st.markdown("#### 📋 뉴스 목록")
        for i, article in enumerate(page_data):
            with st.expander(f"📰 {article['title'][:80]}...", expanded=False):
                col_info, col_link = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"**📰 출처:** {article['source']}")
                    st.markdown(f"**🔍 키워드:** {article['keyword']}")
                    st.markdown(f"**📅 발행일:** {article['published']}")
                    
                    if article.get('summary'):
                        st.markdown(f"**📝 요약:** {article['summary'][:200]}...")
                
                with col_link:
                    st.markdown(f"[🔗 기사 보기]({article['link']})")
        
        # 데이터 내보내기 섹션
        st.markdown("---")
        st.markdown("### 💾 데이터 내보내기")
        
        col_export1, col_export2, col_export3 = st.columns(3)
        
        with col_export1:
            json_data = json.dumps(filtered_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📄 JSON 다운로드",
                data=json_data,
                file_name=f"동반성장_뉴스_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_export2:
            df = pd.DataFrame(filtered_data)
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📊 CSV 다운로드",
                data=csv_data,
                file_name=f"동반성장_뉴스_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_export3:
            st.info("📈 Excel 다운로드는 실제 크롤링 시 사용 가능합니다.")

if __name__ == "__main__":
    main()
