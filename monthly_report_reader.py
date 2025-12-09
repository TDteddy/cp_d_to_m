"""
월별 판매량 및 매출 보고서 읽기 모듈
"""
import pandas as pd
import os
from typing import Optional


class MonthlyReportReader:
    """쿠팡 월별 판매량 및 매출 보고서를 읽는 클래스"""

    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: 데이터 파일이 있는 디렉토리 경로
        """
        self.data_dir = data_dir

    def read_report(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        월별 보고서 파일을 읽어서 DataFrame으로 반환

        Args:
            file_path: 보고서 파일 경로 (None이면 data_dir에서 .xlsx 파일 자동 검색)

        Returns:
            pd.DataFrame: 월별 보고서 데이터
        """
        if file_path is None:
            # data 디렉토리에서 첫 번째 .xlsx 파일 찾기
            xlsx_files = [f for f in os.listdir(self.data_dir) if f.endswith('.xlsx')]
            if not xlsx_files:
                raise FileNotFoundError(f"{self.data_dir} 디렉토리에 .xlsx 파일이 없습니다.")
            file_path = os.path.join(self.data_dir, xlsx_files[0])
            print(f"파일 읽기: {file_path}")

        # 엑셀 파일 읽기
        df = pd.read_excel(file_path)

        # 필요한 컬럼만 선택 (옵션명, 매출, 판매량)
        # 헤더: 옵션 ID, 옵션명, 상품명, 등록상품ID, 카테고리, 판매방식, 매출(원), 주문, 판매량...
        # 실제 컬럼명은 파일에 따라 다를 수 있으므로 유연하게 처리

        print(f"읽은 데이터: {len(df)} 행")
        print(f"컬럼: {df.columns.tolist()}")

        return df

    def extract_option_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        옵션명별로 매출과 판매량 데이터 추출

        쿠팡 월별 보고서 기준:
        - 옵션명: 옵션 이름
        - 매출(원): 총 매출 (취소 포함)
        - 판매량: 총 판매량 (취소 포함)

        Args:
            df: 원본 DataFrame

        Returns:
            pd.DataFrame: 옵션명, 매출, 판매량을 포함한 DataFrame
        """
        # 컬럼명 매핑 (실제 파일의 컬럼명에 맞게 조정)
        # 매출(원)은 취소를 포함한 총 매출 금액입니다
        column_mapping = {
            '옵션명': 'option_name',
            '옵션 ID': 'option_id',
            '매출(원)': 'sales_amount',  # 취소 포함
            '판매량': 'sales_qty',        # 취소 포함
            '주문': 'orders'
        }

        # 필요한 컬럼만 추출
        result_df = pd.DataFrame()

        for original_col, new_col in column_mapping.items():
            if original_col in df.columns:
                result_df[new_col] = df[original_col]

        # 옵션명이 없으면 옵션 ID 사용
        if 'option_name' not in result_df.columns and 'option_id' in result_df.columns:
            result_df['option_name'] = result_df['option_id']

        # 매출과 판매량이 숫자형인지 확인
        if 'sales_amount' in result_df.columns:
            result_df['sales_amount'] = pd.to_numeric(result_df['sales_amount'], errors='coerce').fillna(0)

        if 'sales_qty' in result_df.columns:
            result_df['sales_qty'] = pd.to_numeric(result_df['sales_qty'], errors='coerce').fillna(0)

        # 옵션명별로 그룹화 (중복이 있을 수 있으므로)
        if 'option_name' in result_df.columns:
            grouped = result_df.groupby('option_name').agg({
                'sales_amount': 'sum',
                'sales_qty': 'sum'
            }).reset_index()

            return grouped

        return result_df
