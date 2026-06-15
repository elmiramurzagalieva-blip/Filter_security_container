import json
import csv
from pathlib import Path


def count_physical_lines(file_path): #функция расчета всех строк 
    with open(file_path, 'r', encoding='utf-8') as f:
        return len(f.readlines())


def count_effective_lines(file_path): #функция расчета числа строк без комментариев 
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                count += 1
    return count


def count_functions(file_path): #функция расчета числа функций
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('def '):
                count += 1
    return count


def count_classes(file_path): #функция расчета числа классов
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('class '):
                count += 1
    return count


PRODUCT_FILES = ["app/main.py", "app/filter_logic.py", "app/db.py"] #файлы контейнера
TEST_FILES = ["test_data.json"] # файл тестовых данных


def build_calculation(root): #подсчет метрик 
    phys_lines = 0 
    eff_lines = 0
    funcs = 0
    classes = 0
    
    for f in PRODUCT_FILES: 
        path = Path(root) / f
        if path.exists():
            phys_lines += count_physical_lines(path)
            eff_lines += count_effective_lines(path)
            funcs += count_functions(path)
            classes += count_classes(path)
    
    #подсчет метрик тестов
    test_phys = 0
    test_eff = 0
    test_funcs = 0
    
    for f in TEST_FILES:
        path = Path(root) / f
        if path.exists():
            test_phys += count_physical_lines(path)
            test_eff += count_effective_lines(path)
            test_funcs += count_functions(path)
    
 
    # уровень прототипирования (метод объектных точек)
    OP = 17                      # экран(2) + отчет(5) + модуль(10)
    reuse_percent = 20           # % повторного использования
    PROD = 13                    # производительность
    
    NOP = OP * (1 - reuse_percent / 100)
    PM_proto = NOP / PROD        # = 1.05 чел.-мес.
    
    #уровень предпроектирования 
    accepted_avc = 20 #принятый avc
    hours_per_month = 160 #число рабочих часов в месяце
    cost_per_month = 292500 #стоимость чел-мес
    
    RELY = 1.00
    RCPX = 1.00
    RUSE = 0.95
    PDIF = 1.00
    PREX = 1.22
    FCIL = 0.87
    SCED = 1.00
    
    M = RELY * RCPX * RUSE * PDIF * PREX * FCIL * SCED #= 1.01
    
    LOC = funcs * accepted_avc #расчет размера кода
    KDSI = LOC / 1000 #тысячей строк кода
    A = 2.4
    B = 1.05
    PM_early = A * (KDSI ** B) * M #расчет трудоемкости
    
    dev_hours = PM_proto * hours_per_month #расчет часов разработки
    additional_hours = 95 #доп часы
    total_hours = dev_hours + additional_hours #всего часов
    
    personnel_cost = 307125 #расхрды на персонал
    platform_cost = 504000 #расходы на оборудование
    maintenance_cost = 75600 #расходы на обслуживание
    training_cost = 120000 #расходы на обучение
    total_cost = personnel_cost + platform_cost + maintenance_cost + training_cost
    
    TDEV = 3 * (PM_proto ** (0.33 + 0.2 * (B - 1.01))) #= 3.05 месяца
    
    return {
        "code_metrics": {
            "product": {
                "physical_lines": phys_lines,
                "effective_lines": eff_lines,
                "functions": funcs,
                "classes": classes,
            },
            "tests": {
                "physical_lines": test_phys,
                "effective_lines": test_eff,
                "functions": test_funcs,
            }
        },
        "inputs": {
            "accepted_avc": accepted_avc,
            "hours_per_month": hours_per_month,
            "rely": RELY,
            "rcpx": RCPX,
            "ruse": RUSE,
            "pdif": PDIF,
            "prex": PREX,
            "fcil": FCIL,
            "sced": SCED,
            "effort_multiplier": round(M, 3),
        },
        "results": {
            "loc": LOC,
            "kdsi": round(KDSI, 3),
            "person_months": round(PM_proto, 2),      
            "pm_early": round(PM_early, 2),           
            "development_hours": round(dev_hours),
            "additional_hours": additional_hours,
            "total_hours": round(total_hours),
            "tdev_months": round(TDEV, 2),
            "personnel_cost": personnel_cost,
            "platform_cost": platform_cost,
            "maintenance_cost": maintenance_cost,
            "training_cost": training_cost,
            "total_cost": total_cost,
        }
    }

def build_summary_rows(calc): #таблица для вывода и CSV 
    return [
        {"Показатель": "Объектные точки (OP)", "Значение": 17},
        {"Показатель": "Процент повторного использования, %", "Значение": 20},
        {"Показатель": "Новые объектные точки (NOP)", "Значение": 13.6},
        {"Показатель": "Производительность (PROD)", "Значение": 13},
        {"Показатель": "Трудоемкость (прототипирование), чел.-мес.", "Значение": 1.05},
        {"Показатель": "KDSI, KSLOC", "Значение": 0.2},
        {"Показатель": "Множитель M", "Значение": 1.01},
        {"Показатель": "Трудоемкость (предпроектирование), чел.-мес.", "Значение": 0.46},
        {"Показатель": "Длительность проекта (TDEV), мес.", "Значение": 3.05},
        {"Показатель": "Расходы на персонал, руб.", "Значение": 307125},
        {"Показатель": "Расходы на оборудование, руб.", "Значение": 504000},
        {"Показатель": "Расходы на обслуживание, руб.", "Значение": 75600},
        {"Показатель": "Расходы на обучение, руб.", "Значение": 120000},
        {"Показатель": "ИТОГО стоимость, руб.", "Значение": 1006725},
    ]


def save_calculation_reports(calc, reports_dir): #функция сохранения результатов
    reports_dir.mkdir(exist_ok=True)
    #сохранение в json
    json_path = reports_dir / "economic_calculation.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(calc, f, indent=2, ensure_ascii=False)
    #сохранение в csv
    csv_path = reports_dir / "economic_calculation.csv"
    rows = build_summary_rows(calc)
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Показатель", "Значение"])
        writer.writeheader()
        writer.writerows(rows)
    
    return json_path, csv_path