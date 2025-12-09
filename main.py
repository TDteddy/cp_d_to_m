#!/usr/bin/env python3
"""
쿠팡 월별 판매 보고서와 DB 일별 데이터 비교 프로그램

사용법:
    python main.py

설명:
    1. data 디렉토리에 쿠팡 월별 판매 보고서 파일(.xlsx)을 넣습니다.
    2. 프로그램을 실행하고 연도와 월을 입력합니다.
    3. DB에서 해당 월의 일별 데이터를 조회하여 비교합니다.
    4. 결과를 output 디렉토리에 Excel 파일로 저장합니다.
"""
import os
import sys
from datetime import datetime

from monthly_report_reader import MonthlyReportReader
from db_reader import DBReader
from data_comparator import DataComparator
from report_generator import ReportGenerator


def get_user_input() -> tuple:
    """
    사용자로부터 연도와 월 입력 받기

    Returns:
        tuple: (year, month)
    """
    print("\n" + "=" * 60)
    print("쿠팡 판매 보고서 비교 프로그램")
    print("=" * 60)

    while True:
        try:
            year_input = input("\n비교할 연도를 입력하세요 (예: 2024): ").strip()
            if not year_input:
                current_year = datetime.now().year
                print(f"입력이 없어 현재 연도({current_year})를 사용합니다.")
                year = current_year
            else:
                year = int(year_input)

            month_input = input("비교할 월을 입력하세요 (1-12): ").strip()
            if not month_input:
                current_month = datetime.now().month
                print(f"입력이 없어 현재 월({current_month})을 사용합니다.")
                month = current_month
            else:
                month = int(month_input)

            if 1 <= month <= 12:
                return year, month
            else:
                print("월은 1에서 12 사이의 숫자여야 합니다.")
        except ValueError:
            print("올바른 숫자를 입력해주세요.")
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            sys.exit(0)


def main():
    """메인 함수"""
    try:
        # 사용자 입력
        year, month = get_user_input()

        print(f"\n비교 대상: {year}년 {month}월")
        print("-" * 60)

        # 1. 월별 보고서 읽기
        print("\n[1/4] 월별 판매 보고서 읽는 중...")
        monthly_reader = MonthlyReportReader('data')
        monthly_df_raw = monthly_reader.read_report()
        monthly_df = monthly_reader.extract_option_data(monthly_df_raw)
        print(f"✓ 월별 보고서: {len(monthly_df)} 개 옵션")

        # 2. DB에서 일별 데이터 조회
        print("\n[2/4] DB에서 일별 데이터 조회 중...")
        db_reader = DBReader()
        db_df_raw = db_reader.get_daily_data_by_month(year, month)
        db_df = db_reader.extract_option_summary(db_df_raw)
        print(f"✓ DB 데이터: {len(db_df)} 개 옵션")

        # 3. 데이터 비교
        print("\n[3/4] 데이터 비교 중...")
        comparator = DataComparator()
        result_df = comparator.compare_data(monthly_df, db_df)
        summary = comparator.get_summary_statistics(result_df)
        print(f"✓ 비교 완료: {summary['총_옵션_수']} 개 옵션 분석")
        print(f"  - 차이가 있는 옵션: {summary['차이가_있는_옵션_수']} 개")
        print(f"  - 총 매출 차이: {summary['총_매출_차이']:,.0f} 원")
        print(f"  - 총 판매량 차이: {summary['총_판매량_차이']:,.0f} 개")

        # 4. 결과 보고서 생성
        print("\n[4/4] 결과 보고서 생성 중...")
        report_gen = ReportGenerator('output')
        output_file = report_gen.generate_excel_report(result_df, summary, year, month)
        print(f"✓ 보고서 저장 완료!")

        # 완료 메시지
        print("\n" + "=" * 60)
        print("처리 완료!")
        print("=" * 60)
        print(f"\n결과 파일: {output_file}")
        print(f"\n요약:")
        print(f"  • 총 옵션 수: {summary['총_옵션_수']:,} 개")
        print(f"  • 차이가 있는 옵션: {summary['차이가_있는_옵션_수']:,} 개")
        print(f"  • 총 매출 차이: {summary['총_매출_차이']:,.0f} 원")
        print(f"  • 총 판매량 차이: {summary['총_판매량_차이']:,.0f} 개")
        print("\n" + "=" * 60)

        # DB 연결 종료
        db_reader.close()

    except FileNotFoundError as e:
        print(f"\n오류: {e}")
        print("\ndata 디렉토리에 월별 보고서 파일(.xlsx)을 넣어주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
