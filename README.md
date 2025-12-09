# 쿠팡 판매 보고서 비교 프로그램

쿠팡 월별 판매량 및 매출 보고서와 DB에 저장된 일별 판매 데이터를 비교하여 차이를 분석하는 프로그램입니다.

## 주요 기능

- 쿠팡 월별 판매 보고서 파일(.xlsx) 자동 읽기
- DB에서 해당 월의 일별 판매 데이터 조회
- 옵션명별 매출 및 판매량 비교
- 차이 분석 결과를 Excel 파일로 출력
- 차이가 있는 항목 강조 표시

## 프로젝트 구조

```
cp_d_to_m/
├── main.py                    # 메인 프로그램
├── monthly_report_reader.py   # 월별 보고서 읽기 모듈
├── db_reader.py               # DB 데이터 조회 모듈
├── data_comparator.py         # 데이터 비교 모듈
├── report_generator.py        # 결과 보고서 생성 모듈
├── requirements.txt           # 필요한 패키지 목록
├── config/
│   └── config.ini            # DB 연결 설정
├── data/                     # 월별 보고서 파일을 넣는 디렉토리
└── output/                   # 결과 파일이 저장되는 디렉토리
```

## 설치 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. DB 설정

`config/config.ini` 파일을 편집하여 DB 연결 정보를 입력합니다.

```ini
[DATABASE]
db_type = mysql              # DB 종류: mysql, postgresql, sqlite
host = localhost             # DB 호스트
port = 3306                  # DB 포트
database = sales_db          # DB 이름
username = your_username     # DB 사용자명
password = your_password     # DB 비밀번호
table_name = daily_sales_report  # 일별 판매 데이터 테이블명
```

## 사용 방법

### 1. 월별 보고서 파일 준비

쿠팡에서 다운로드한 월별 판매량 및 매출 보고서 파일(.xlsx)을 `data/` 디렉토리에 넣습니다.

### 2. 프로그램 실행

```bash
python main.py
```

### 3. 연도와 월 입력

프로그램 실행 후 비교하려는 연도와 월을 입력합니다.

```
비교할 연도를 입력하세요 (예: 2024): 2024
비교할 월을 입력하세요 (1-12): 3
```

### 4. 결과 확인

`output/` 디렉토리에 생성된 Excel 파일을 확인합니다.

파일명 형식: `판매보고서_비교결과_2024년_3월_20240309_143052.xlsx`

## 결과 파일 구성

생성된 Excel 파일은 다음과 같은 시트로 구성됩니다:

### 1. 요약 시트

- 총 옵션 수
- 차이가 있는 옵션 수
- 총 매출 차이
- 총 판매량 차이
- 평균/최대/최소 차이 등 통계

### 2. 상세 비교 시트

모든 옵션에 대한 상세 비교 결과:
- 옵션명
- 월별보고서_매출 / DB_매출 / 매출_차이 / 매출_차이율(%)
- 월별보고서_판매량 / DB_판매량 / 판매량_차이 / 판매량_차이율(%)

### 3. 차이 있는 항목 시트

차이가 있는 옵션만 필터링한 결과

**강조 표시:**
- 🔴 빨간색: 월별 보고서가 DB보다 큰 경우 (양수 차이)
- 🟢 초록색: 월별 보고서가 DB보다 작은 경우 (음수 차이)

## 데이터 매핑

### 월별 보고서 (쿠팡)

- 옵션명
- 매출(원) - 총 매출 (취소 포함)
- 판매량 - 총 판매량 (취소 포함)

### DB 일별 데이터

- Name_option_coupang_at_sales_report_coupang_2p (옵션명)
- Sales_total_amount_at_sales_report_coupang_2p (총 매출, 취소 포함)
- Qty_sales_total_at_sales_report_coupang_2p (총 판매량, 취소 포함)

폴백 옵션:
- Sales_net_amount_at_sales_report_coupang_2p (순 매출, 취소 제외)
- Qty_sales_net_at_sales_report_coupang_2p (순 판매량, 취소 제외)

### 비교 방식

프로그램은 **취소를 포함한 총 매출/판매량**을 기준으로 비교합니다:
- 월별 보고서의 '매출(원)' ↔ DB의 'Sales_total_amount' (취소 포함)
- 월별 보고서의 '판매량' ↔ DB의 'Qty_sales_total' (취소 포함)

이를 통해 양쪽 데이터의 일관성을 확인할 수 있습니다.

## 문제 해결

### 1. DB 연결 오류

- `config/config.ini` 파일의 DB 연결 정보를 확인하세요.
- DB 서버가 실행 중인지 확인하세요.
- 방화벽 설정을 확인하세요.

### 2. 파일을 찾을 수 없음

- `data/` 디렉토리에 .xlsx 파일이 있는지 확인하세요.
- 파일 권한을 확인하세요.

### 3. 컬럼명 불일치

- 파일의 헤더가 다를 수 있습니다.
- `monthly_report_reader.py`와 `db_reader.py`의 컬럼 매핑을 확인하세요.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 개발자

- 개발 언어: Python 3.8+
- 주요 라이브러리: pandas, openpyxl, sqlalchemy

## 업데이트 이력

- v1.0.0 (2024-12-09): 초기 버전 릴리스
