"""
월별 보고서와 DB 데이터를 비교하는 모듈
"""
import pandas as pd
from typing import Tuple


class DataComparator:
    """데이터 비교 및 차이 계산 클래스"""

    @staticmethod
    def compare_data(monthly_df: pd.DataFrame, db_df: pd.DataFrame) -> pd.DataFrame:
        """
        월별 보고서와 DB 데이터를 비교하여 차이를 계산

        Args:
            monthly_df: 월별 보고서 데이터 (컬럼: option_name, sales_amount, sales_qty)
            db_df: DB 데이터 (컬럼: option_name, sales_amount, sales_qty)

        Returns:
            pd.DataFrame: 비교 결과 (옵션명, 월별 매출, DB 매출, 매출 차이, 월별 판매량, DB 판매량, 판매량 차이)
        """
        # 두 데이터를 옵션명 기준으로 병합
        merged = pd.merge(
            monthly_df,
            db_df,
            on='option_name',
            how='outer',
            suffixes=('_monthly', '_db')
        )

        # NaN 값을 0으로 채우기
        merged['sales_amount_monthly'] = merged['sales_amount_monthly'].fillna(0)
        merged['sales_amount_db'] = merged['sales_amount_db'].fillna(0)
        merged['sales_qty_monthly'] = merged['sales_qty_monthly'].fillna(0)
        merged['sales_qty_db'] = merged['sales_qty_db'].fillna(0)

        # 차이 계산
        merged['sales_amount_diff'] = merged['sales_amount_monthly'] - merged['sales_amount_db']
        merged['sales_qty_diff'] = merged['sales_qty_monthly'] - merged['sales_qty_db']

        # 차이율 계산 (%)
        merged['sales_amount_diff_rate'] = merged.apply(
            lambda row: DataComparator._calculate_diff_rate(
                row['sales_amount_monthly'],
                row['sales_amount_db']
            ),
            axis=1
        )

        merged['sales_qty_diff_rate'] = merged.apply(
            lambda row: DataComparator._calculate_diff_rate(
                row['sales_qty_monthly'],
                row['sales_qty_db']
            ),
            axis=1
        )

        # 컬럼 순서 정리
        result = merged[[
            'option_name',
            'sales_amount_monthly',
            'sales_amount_db',
            'sales_amount_diff',
            'sales_amount_diff_rate',
            'sales_qty_monthly',
            'sales_qty_db',
            'sales_qty_diff',
            'sales_qty_diff_rate'
        ]]

        # 컬럼명 변경
        result.columns = [
            '옵션명',
            '월별보고서_매출',
            'DB_매출',
            '매출_차이',
            '매출_차이율(%)',
            '월별보고서_판매량',
            'DB_판매량',
            '판매량_차이',
            '판매량_차이율(%)'
        ]

        # 차이가 있는 항목을 위로 정렬
        result['abs_sales_diff'] = result['매출_차이'].abs()
        result = result.sort_values('abs_sales_diff', ascending=False)
        result = result.drop('abs_sales_diff', axis=1)

        return result

    @staticmethod
    def _calculate_diff_rate(value1: float, value2: float) -> float:
        """
        두 값의 차이율을 계산

        Args:
            value1: 첫 번째 값
            value2: 두 번째 값

        Returns:
            float: 차이율 (%)
        """
        if value2 == 0:
            if value1 == 0:
                return 0.0
            else:
                return 100.0  # DB에 데이터가 없는 경우
        return ((value1 - value2) / value2) * 100

    @staticmethod
    def get_summary_statistics(result_df: pd.DataFrame) -> dict:
        """
        비교 결과의 요약 통계를 계산

        Args:
            result_df: 비교 결과 DataFrame

        Returns:
            dict: 요약 통계
        """
        summary = {
            '총_옵션_수': len(result_df),
            '차이가_있는_옵션_수': len(result_df[
                (result_df['매출_차이'] != 0) | (result_df['판매량_차이'] != 0)
            ]),
            '총_매출_차이': result_df['매출_차이'].sum(),
            '총_판매량_차이': result_df['판매량_차이'].sum(),
            '평균_매출_차이': result_df['매출_차이'].mean(),
            '평균_판매량_차이': result_df['판매량_차이'].mean(),
            '최대_매출_차이': result_df['매출_차이'].max(),
            '최소_매출_차이': result_df['매출_차이'].min(),
            '최대_판매량_차이': result_df['판매량_차이'].max(),
            '최소_판매량_차이': result_df['판매량_차이'].min(),
        }

        return summary
