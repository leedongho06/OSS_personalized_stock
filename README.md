# 📈 맞춤형 주식 추천 시스템 (Personalized Stock)

> 사용자의 **투자 성향**을 분석하고, **코사인 유사도 기반 추천**과 **강화학습(Q-Learning)** 을 결합하여
> 개인에게 맞는 국내 주식 종목을 추천하는 프로젝트입니다.

CLI와 웹(Flask) 두 가지 인터페이스를 제공하며, 매일 변하는 시장 데이터를 반영해
"고정된 추천"이 아니라 **동적으로 변화하는 추천 결과**를 보여주는 것을 목표로 합니다.

---

## 목차

- [주요 기능](#주요-기능)
- [동작 원리](#동작-원리)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시스템 요구사항](#시스템-요구사항)
- [설치법](#설치법)
- [의존성](#의존성)
- [환경 변수 설정](#환경-변수-설정-선택)
- [사용 실행 방법](#사용-실행-방법)
- [테스트](#테스트)
- [라이선스](#라이선스)

---

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 🎯 **투자 성향 분석** | 관심 기업 입력 / 성향 직접 선택 / 뉴스 관심도 평가의 3가지 방식으로 `안정형 · 중립형 · 공격형` 성향을 추론합니다. |
| 🤖 **맞춤 종목 추천** | PER · PBR · 20일 이동평균 · 거래량 특성을 바탕으로 **코사인 유사도**를 계산해 성향에 가장 가까운 Top 5 종목을 추천합니다. |
| 🧠 **강화학습 피드백** | 사용자의 만족도 평가를 보상 신호로 변환하여 **Q-Learning** Q-테이블을 학습, 추천을 점차 개인화합니다. |
| 📰 **AI 뉴스 분류** | Google News RSS에서 실시간 뉴스를 수집하고, Gemini AI로 섹터를 자동 분류합니다. |
| 📒 **매매일지** | 매수/매도 기록을 저장하고 종목별 비중을 차트로 시각화합니다. |
| 📊 **코스피 TOP 10** | 시가총액 상위 10종목의 최신 종가·등락률을 조회합니다. |
| 💾 **자동 데이터 최신화** | 실행 시 DB의 마지막 날짜를 확인하고 누락된 주가 데이터를 자동으로 증분 수집합니다. |

---

## 동작 원리

```

1. 성향 입력  →   2. 성향 추론    →  3. 코사인 유사도 추천  →  4. Q-Learning
 (기업/뉴스)     (안정/중립/공격)      (PER·PBR·MA·거래량)       피드백 학습  

```

1. **성향 추론** — 관심 기업의 섹터·변동성 점수를 합산하거나, 뉴스 별점 평가 결과를 분석해 투자 성향을 결정합니다.
2. **이상적 프로파일 매칭** — 성향별 이상 지표(예: 안정형 `PER 10 / PBR 0.8`, 공격형 `PER 35 / PBR 3.0`)를 정의하고,
   `scikit-learn`의 `MinMaxScaler` + `cosine_similarity`로 각 종목과의 유사도를 계산합니다.
3. **동적 추천** — 정적 `stocks.csv`(KOSPI 100종목 메타데이터)와 SQLite DB의 최신 주가를 병합하여 매일 달라지는 결과를 산출합니다.
4. **강화학습** — `(성향 × 섹터)` 상태에서 추천 Action을 고르고, 사용자 피드백(1~5점)을 보상으로 변환해 Q-테이블을 갱신합니다.

---

## 기술 스택

- **Language**: Python 3.8+
- **Web**: Flask, Jinja2, HTML/CSS/JavaScript
- **Data / ML**: pandas, numpy, scikit-learn
- **Stock Data**: FinanceDataReader, pykrx
- **AI**: Google Generative AI (Gemini 1.5 Flash)
- **Database**: SQLite3
- **Test**: pytest, unittest

---

## 프로젝트 구조

```
OSS_personalized_stock/
├── main.py                  # CLI 진입점 (대화형 추천 실행)
├── app.py                   # Flask 웹 애플리케이션 (포트 5000)
├── web_server.py            # DB 조회용 별도 API 서버 (포트 8080)
├── check_db.py              # SQLite 테이블 구조 확인 유틸리티
│
├── recommendation/          # 추천 엔진
│   ├── profile.py           #  - 성향별 이상 지표 정의
│   ├── scorer.py            #  - 관심 기업 → 성향 추론
│   ├── filter.py            #  - 성향별 종목 필터링
│   └── recommender.py       #  - 코사인 유사도 Top-N 추천
│
├── q_learning/              # 강화학습 모듈
│   ├── q_table.py           #  - Q-테이블 초기화/저장/로드
│   ├── agent.py             #  - Action 선택 및 Q값 업데이트
│   ├── state_encoder.py     #  - (성향, 섹터) → 상태 인코딩
│   ├── reward.py            #  - 피드백 점수 → 보상 변환
│   └── train.py             #  - 학습 에피소드 실행
│
├── news/                    # 뉴스 수집 및 분류
│   ├── fetcher.py           #  - Google News RSS 수집
│   ├── classifier.py        #  - Gemini AI 섹터 분류
│   ├── interest_scorer.py   #  - 뉴스 관심도 점수 계산
│   ├── style_inferrer.py    #  - 관심도 → 성향 추론
│   └── db_manager.py        #  - 뉴스/매매일지 테이블 관리
│
├── data/                    # 주가 데이터 수집 파이프라인
│   ├── build_stocks.py      #  - KOSPI 100종목 stocks.csv 생성
│   ├── updater.py           #  - 일일 증분 주가 데이터 수집
│   ├── stocks.csv           #  - 종목 메타데이터 (커밋됨)
│   └── stock_data.db        #  - 주가 SQLite DB (실행 시 생성)
│
├── database/                # DB 매니저 및 스키마
│   ├── db_manager.py        #  - 주가/사용자 데이터 CRUD
│   ├── schema.sql           #  - 테이블 스키마 정의
│   └── init_db.py           #  - DB 초기화
│
├── cli/                     # 프로파일 관리용 Click CLI
│   └── main.py
│
├── templates/               # Flask HTML 템플릿
├── static/                  # CSS / JavaScript
├── tests/                   # pytest 테스트 (31개 파일)
│
├── requirements.txt         # 의존성 목록
├── LICENSE                  # MIT 라이선스
└── README.md
```

---
