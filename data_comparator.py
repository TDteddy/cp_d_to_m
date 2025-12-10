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
        월별 보고서와 DB 데이터를 옵션 ID 기준으로 비교하여 차이를 계산

        Args:
            monthly_df: 월별 보고서 데이터 (컬럼: option_id, option_name, sales_amount, sales_qty)
            db_df: DB 데이터 (컬럼: option_id, option_name, sales_amount, sales_qty)

        Returns:
            pd.DataFrame: 비교 결과 (옵션 ID, 양쪽 옵션명, 매출/판매량 비교)
        """
        # 디버깅: 옵션 ID 샘플 출력
        print("\n[디버깅] 옵션 ID 비교:")
        print(f"월별 보고서 옵션 ID 샘플 (처음 5개):")
        print(f"  {monthly_df['option_id'].head().tolist()}")
        print(f"  타입: {monthly_df['option_id'].dtype}")
        print(f"\nDB 옵션 ID 샘플 (처음 5개):")
        print(f"  {db_df['option_id'].head().tolist()}")
        print(f"  타입: {db_df['option_id'].dtype}")

        # 공통 옵션 ID 확인
        common_ids = set(monthly_df['option_id']) & set(db_df['option_id'])
        print(f"\n공통 옵션 ID 개수: {len(common_ids)}")
        if len(common_ids) > 0:
            print(f"공통 옵션 ID 샘플: {list(common_ids)[:5]}")

        # 두 데이터를 옵션 ID 기준으로 병합
        merged = pd.merge(
            monthly_df,
            db_df,
            on='option_id',
            how='outer',
            suffixes=('_monthly', '_db')
        )

        # 옵션명은 빈 문자열로 채우기
        merged['option_name_monthly'] = merged['option_name_monthly'].fillna('')
        merged['option_name_db'] = merged['option_name_db'].fillna('')

        # 숫자 컬럼을 확실하게 숫자형으로 변환 후 NaN을 0으로 채우기
        merged['sales_amount_monthly'] = pd.to_numeric(merged['sales_amount_monthly'], errors='coerce').fillna(0)
        merged['sales_amount_db'] = pd.to_numeric(merged['sales_amount_db'], errors='coerce').fillna(0)
        merged['sales_qty_monthly'] = pd.to_numeric(merged['sales_qty_monthly'], errors='coerce').fillna(0)
        merged['sales_qty_db'] = pd.to_numeric(merged['sales_qty_db'], errors='coerce').fillna(0)

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
            'option_id',
            'option_name_monthly',
            'option_name_db',
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
            '옵션_ID',
            '월별보고서_옵션명',
            'DB_옵션명',
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
