#тесты для проверки корректности расчетов
from pathlib import Path
#импорт объектов из расчетного модуля
from secure_filter.economic_calculation import (
    PRODUCT_FILES,
    TEST_FILES,
    build_calculation,
)
#определение корневой папки проекта 
ROOT = Path(__file__).resolve().parent.parent

# проверка, что метрики кода посчитались корректно
def test_code_metrics_are_positive():
    calc = build_calculation(ROOT) #расчет
    prod = calc["code_metrics"]["product"]
    #проверка метрик на условие
    assert prod["physical_lines"] > 0
    assert prod["effective_lines"] > 0
    assert prod["functions"] > 0
    assert prod["classes"] >= 0

# проверка, что результат расчета содержит все необходимые разделы
def test_economic_calculation_has_required_fields():
    calc = build_calculation(ROOT)
    # проверка наличия обязательных разделов
    assert "code_metrics" in calc
    assert "inputs" in calc
    assert "results" in calc
    # проверка наличия обязательных показателей
    res = calc["results"]
    assert "person_months" in res
    assert "total_cost" in res
    assert "tdev_months" in res

# проверка, что числовые значения соответствуют отчету
def test_calculation_values_match_report():
    calc = build_calculation(ROOT)
    res = calc["results"]
    inp = calc["inputs"]
    # проверка корректирующих множителей
    assert inp["rely"] == 1.00
    assert inp["rcpx"] == 1.00
    assert inp["ruse"] == 0.95
    assert inp["pdif"] == 1.00
    assert inp["prex"] == 1.22
    assert inp["fcil"] == 0.87
    assert inp["sced"] == 1.00
    # проверка результатов расчетов
    assert res["person_months"] == 1.05
    assert res["tdev_months"] == 3.05
    assert res["total_cost"] == 307125 + 504000 + 75600 + 120000