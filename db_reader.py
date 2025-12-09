"""
DB에서 일별 판매 데이터를 조회하는 모듈
"""
import pandas as pd
import configparser
from typing import Tuple
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


class DBReader:
    """DB에서 일별 판매 데이터를 조회하는 클래스"""

    def __init__(self, config_path: str = 'config/config.ini'):
        """
        Args:
            config_path: 설정 파일 경로
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        self.engine = self._create_engine()

    def _create_engine(self) -> Engine:
        """
        DB 연결 엔진 생성

        Returns:
            sqlalchemy.engine.Engine: DB 연결 엔진
        """
        db_type = self.config.get('DATABASE', 'db_type')
        host = self.config.get('DATABASE', 'host')
        port = self.config.get('DATABASE', 'port')
        database = self.config.get('DATABASE', 'database')
        username = self.config.get('DATABASE', 'username')
        password = self.config.get('DATABASE', 'password')

        if db_type == 'mysql':
            connection_string = f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
        elif db_type == 'postgresql':
            connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
        elif db_type == 'sqlite':
            connection_string = f'sqlite:///{database}'
        else:
            raise ValueError(f"지원하지 않는 DB 타입: {db_type}")

        return create_engine(connection_string)

    def get_daily_data_by_month(self, year: int, month: int) -> pd.DataFrame:
        """
        특정 월의 일별 판매 데이터를 DB에서 조회

        Args:
            year: 연도
            month: 월

        Returns:
            pd.DataFrame: 일별 판매 데이터
        """
        table_name = self.config.get('DATABASE', 'table_name')

        # 날짜 범위 계산
        start_date = f'{year}-{month:02d}-01'
        if month == 12:
            end_date = f'{year + 1}-01-01'
        else:
            end_date = f'{year}-{month + 1:02d}-01'

        # SQL 쿼리
        query = f"""
        SELECT *
        FROM {table_name}
        WHERE Date >= '{start_date}' AND Date < '{end_date}'
        """

        print(f"SQL 실행: {query}")

        # 데이터 조회
        df = pd.read_sql(query, self.engine)

        print(f"조회된 데이터: {len(df)} 행")

        return df

    def extract_option_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        옵션명별로 매출과 판매량을 집계

        DB 헤더 기준:
        - Name_option_coupang_at_sales_report_coupang_2p: 옵션명
        - Sales_net_amount_at_sales_report_coupang_2p: 순 매출 (취소 제외)
        - Qty_sales_net_at_sales_report_coupang_2p: 순 판매량 (취소 제외)

        Args:
            df: 일별 데이터 DataFrame

        Returns:
            pd.DataFrame: 옵션명별 집계 데이터
        """
        # 필요한 컬럼 확인
        print(f"DB 컬럼: {df.columns.tolist()}")

        # 컬럼 매핑 - 실제 쿠팡 DB 컬럼명
        option_col = None
        sales_amount_col = None
        sales_qty_col = None

        # 옵션명 컬럼 찾기
        if 'Name_option_coupang_at_sales_report_coupang_2p' in df.columns:
            option_col = 'Name_option_coupang_at_sales_report_coupang_2p'
        elif 'ID_option_coupang_2p_at_sales_report_coupang_2p' in df.columns:
            option_col = 'ID_option_coupang_2p_at_sales_report_coupang_2p'
        else:
            raise ValueError("옵션명 컬럼을 찾을 수 없습니다.")

        # 매출 컬럼 찾기 (순 매출 우선, 없으면 총 매출)
        if 'Sales_net_amount_at_sales_report_coupang_2p' in df.columns:
            sales_amount_col = 'Sales_net_amount_at_sales_report_coupang_2p'
        elif 'Sales_total_amount_at_sales_report_coupang_2p' in df.columns:
            sales_amount_col = 'Sales_total_amount_at_sales_report_coupang_2p'
        else:
            raise ValueError("매출 컬럼을 찾을 수 없습니다.")

        # 판매량 컬럼 찾기 (순 판매량 우선, 없으면 총 판매량)
        if 'Qty_sales_net_at_sales_report_coupang_2p' in df.columns:
            sales_qty_col = 'Qty_sales_net_at_sales_report_coupang_2p'
        elif 'Qty_sales_total_at_sales_report_coupang_2p' in df.columns:
            sales_qty_col = 'Qty_sales_total_at_sales_report_coupang_2p'
        else:
            raise ValueError("판매량 컬럼을 찾을 수 없습니다.")

        print(f"사용 컬럼 매핑:")
        print(f"  - 옵션명: {option_col}")
        print(f"  - 매출: {sales_amount_col}")
        print(f"  - 판매량: {sales_qty_col}")

        # 숫자형 변환
        df[sales_amount_col] = pd.to_numeric(df[sales_amount_col], errors='coerce').fillna(0)
        df[sales_qty_col] = pd.to_numeric(df[sales_qty_col], errors='coerce').fillna(0)

        # 옵션명별 집계
        grouped = df.groupby(option_col).agg({
            sales_amount_col: 'sum',
            sales_qty_col: 'sum'
        }).reset_index()

        # 컬럼명 통일
        grouped.columns = ['option_name', 'sales_amount', 'sales_qty']

        print(f"집계된 옵션 수: {len(grouped)}")

        return grouped

    def close(self):
        """DB 연결 종료"""
        if self.engine:
            self.engine.dispose()
