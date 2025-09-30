#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 Streamlit 테스트 앱
이 파일을 실행하여 Streamlit이 정상 작동하는지 확인합니다.
"""

import streamlit as st
import sys
import os

def main():
    # 페이지 설정
    st.set_page_config(
        page_title="Streamlit 테스트",
        page_icon="🔧",
        layout="centered"
    )
    
    # 제목
    st.title("🔧 Streamlit 화면 테스트")
    st.markdown("---")
    
    # 시스템 정보 표시
    st.subheader("📊 시스템 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Python 버전**: {sys.version}")
        st.write(f"**Streamlit 버전**: {st.__version__}")
    
    with col2:
        st.write(f"**현재 디렉토리**: {os.getcwd()}")
        st.write(f"**운영체제**: {os.name}")
    
    # 기본 기능 테스트
    st.subheader("🧪 기능 테스트")
    
    # 텍스트 입력
    name = st.text_input("이름을 입력하세요:", "테스트 사용자")
    
    # 슬라이더
    age = st.slider("나이를 선택하세요:", 0, 100, 25)
    
    # 버튼
    if st.button("인사하기"):
        st.success(f"안녕하세요, {name}님! {age}세이시군요!")
    
    # 체크박스
    if st.checkbox("추가 정보 표시"):
        st.info("이것은 추가 정보입니다!")
    
    # 선택박스
    option = st.selectbox("선호하는 색상을 선택하세요:", ["빨강", "파랑", "초록", "노랑"])
    st.write(f"선택한 색상: {option}")
    
    # 진행바
    progress = st.progress(0)
    if st.button("진행바 테스트"):
        for i in range(100):
            progress.progress(i + 1)
    
    # 성공 메시지
    st.markdown("---")
    st.success("✅ Streamlit이 정상적으로 작동하고 있습니다!")
    st.info("💡 이 화면이 보인다면 모든 기능이 정상입니다.")
    
    # 경고 메시지
    st.warning("⚠️ 만약 화면이 보이지 않는다면 브라우저를 새로고침하거나 다른 브라우저를 시도해보세요.")

if __name__ == "__main__":
    main()
