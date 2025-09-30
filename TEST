#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
동반성장 지수 평가 관련 뉴스 크롤러
Google News RSS를 활용하여 동반성장 지수 평가 관련 뉴스를 수집합니다.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        
        # 결과 저장용 리스트
        self.news_data = []
    
    def search_news(self, keyword, max_results=50):
        """
        Google News RSS에서 특정 키워드로 뉴스를 검색합니다.
        """
        try:
            # Google News RSS URL 구성
            search_url = f"{self.base_url}/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
            logger.info(f"검색 중: {keyword}")
            logger.info(f"URL: {search_url}")
            
            # RSS 피드 파싱
            feed = feedparser.parse(search_url)
            
            if not feed.entries:
                logger.warning(f"'{keyword}'에 대한 뉴스가 없습니다.")
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
                    
                    # 중복 제거를 위한 URL 정규화
                    article['normalized_url'] = self.normalize_url(article['link'])
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"기사 파싱 중 오류: {e}")
                    continue
            
            logger.info(f"'{keyword}' 검색 완료: {len(articles)}개 기사")
            return articles
            
        except Exception as e:
            logger.error(f"뉴스 검색 중 오류: {e}")
            return []
    
    def normalize_url(self, url):
        """
        URL을 정규화하여 중복을 방지합니다.
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.netloc}{parsed.path}"
        except:
            return url
    
    def get_article_content(self, url):
        """
        기사 URL에서 실제 내용을 추출합니다.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 기사 내용 추출 (다양한 셀렉터 시도)
            content_selectors = [
                'article',
                '.article-content',
                '.news-content',
                '.content',
                '.post-content',
                'main',
                '.entry-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    break
            
            if not content:
                # 메타 태그에서 설명 추출
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    content = meta_desc.get('content', '')
            
            return content[:1000]  # 내용 길이 제한
            
        except Exception as e:
            logger.error(f"기사 내용 추출 중 오류: {e}")
            return ""
    
    def filter_relevant_news(self, articles):
        """
        동반성장 지수 평가와 관련된 뉴스만 필터링합니다.
        """
        relevant_keywords = [
            "동반성장", "공정거래", "실적평가", "이행평가", 
            "동반성장위원회", "공정거래위원회", "공정거래협약",
            "중소기업", "대기업", "지수", "평가"
        ]
        
        filtered_articles = []
        for article in articles:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            # 관련 키워드가 포함된 기사만 선택
            if any(keyword in title or keyword in summary for keyword in relevant_keywords):
                filtered_articles.append(article)
        
        return filtered_articles
    
    def crawl_all_news(self):
        """
        모든 키워드에 대해 뉴스를 크롤링합니다.
        """
        logger.info("동반성장 지수 평가 관련 뉴스 크롤링 시작")
        
        all_articles = []
        seen_urls = set()
        
        for keyword in self.keywords:
            try:
                articles = self.search_news(keyword, max_results=30)
                
                for article in articles:
                    # 중복 URL 제거
                    if article['normalized_url'] not in seen_urls:
                        seen_urls.add(article['normalized_url'])
                        all_articles.append(article)
                
                # 요청 간격 조절
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"키워드 '{keyword}' 처리 중 오류: {e}")
                continue
        
        # 관련 뉴스만 필터링
        relevant_articles = self.filter_relevant_news(all_articles)
        
        logger.info(f"총 {len(relevant_articles)}개의 관련 뉴스 발견")
        self.news_data = relevant_articles
        
        return relevant_articles
    
    def save_to_json(self, filename='news_data.json'):
        """
        뉴스 데이터를 JSON 파일로 저장합니다.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.news_data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON 파일 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"JSON 저장 중 오류: {e}")
    
    def save_to_csv(self, filename='news_data.csv'):
        """
        뉴스 데이터를 CSV 파일로 저장합니다.
        """
        try:
            if not self.news_data:
                logger.warning("저장할 데이터가 없습니다.")
                return
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'title', 'link', 'published', 'summary', 'source', 
                    'keyword', 'crawled_at'
                ])
                writer.writeheader()
                writer.writerows(self.news_data)
            logger.info(f"CSV 파일 저장 완료: {filename}")
        except Exception as e:
            logger.error(f"CSV 저장 중 오류: {e}")
    
    def print_summary(self):
        """
        크롤링 결과 요약을 출력합니다.
        """
        if not self.news_data:
            print("크롤링된 뉴스가 없습니다.")
            return
        
        print(f"\n=== 동반성장 지수 평가 관련 뉴스 크롤링 결과 ===")
        print(f"총 뉴스 개수: {len(self.news_data)}")
        
        # 키워드별 통계
        keyword_stats = {}
        for article in self.news_data:
            keyword = article['keyword']
            keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
        
        print(f"\n키워드별 뉴스 개수:")
        for keyword, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {keyword}: {count}개")
        
        # 최신 뉴스 5개 출력
        print(f"\n최신 뉴스 5개:")
        for i, article in enumerate(self.news_data[:5], 1):
            print(f"{i}. {article['title']}")
            print(f"   출처: {article['source']}")
            print(f"   링크: {article['link']}")
            print(f"   발행일: {article['published']}")
            print()

def main():
    """
    메인 실행 함수
    """
    crawler = NewsCrawler()
    
    try:
        # 뉴스 크롤링 실행
        articles = crawler.crawl_all_news()
        
        if articles:
            # 결과 저장
            crawler.save_to_json()
            crawler.save_to_csv()
            
            # 요약 출력
            crawler.print_summary()
        else:
            print("관련 뉴스를 찾을 수 없습니다.")
    
    except Exception as e:
        logger.error(f"크롤링 실행 중 오류: {e}")

if __name__ == "__main__":
    main()
