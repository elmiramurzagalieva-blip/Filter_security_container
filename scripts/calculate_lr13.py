#!/usr/bin/env python3
import sys
from pathlib import Path
# определение корневой папки проекта
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from secure_filter.economic_calculation import (
    build_calculation, #выполняет все расчеты (трудоемкость, стоимость, длительность)
    build_summary_rows, #формирует таблицу показателей для вывода
    save_calculation_reports, #сохраняет результаты в JSON и CSV
)


def main():
    calc = build_calculation(ROOT) # выполняется расчет
    # сохранение результатов в папку reports/
    json_path, csv_path = save_calculation_reports(calc, ROOT / "reports")

    print("Автоматизированный расчет")
    for row in build_summary_rows(calc):
        print(f"{row['Показатель']}: {row['Значение']}")
    print(f"\nJSON сохранен: {json_path}")
    print(f"CSV сохранен: {csv_path}")


if __name__ == "__main__":
    main()