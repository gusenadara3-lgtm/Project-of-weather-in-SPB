import csv
import random
from collections import deque

# =====================================================================
# 1. ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ
# =====================================================================

class Node:
    """Узел Бинарного Дерева Поиска (БДП) по температуре."""
    def __init__(self, temp, date):
        self.temp = temp
        # Храним список дат, так как температура в разные дни может совпадать
        self.dates = [date]
        self.left = None
        self.right = None

class WeatherBST:
    """Бинарное дерево поиска для быстрого поиска дней выше заданной температуры."""
    def __init__(self):
        self.root = None

    def insert(self, temp, date):
        """Вставка узла в дерево."""
        if self.root is None:
            self.root = Node(temp, date)
        else:
            self._insert_rec(self.root, temp, date)

    def _insert_rec(self, node, temp, date):
        if temp == node.temp:
            node.dates.append(date)
        elif temp < node.temp:
            if node.left is None:
                node.left = Node(temp, date)
            else:
                self._insert_rec(node.left, temp, date)
        else:
            if node.right is None:
                node.right = Node(temp, date)
            else:
                self._insert_rec(node.right, temp, date)

    def find_above_threshold(self, threshold):
        """Публичный метод для поиска всех дат с температурой > порога."""
        result = []
        self._inorder_above(self.root, threshold, result)
        return result

    def _inorder_above(self, node, threshold, result):
        """Рекурсивный обход дерева для извлечения дат."""
        if node is None:
            return
        
        # Рекурсивно идем в левое поддерево
        self._inorder_above(node.left, threshold, result)
        
        # Если температура в узле больше порога, сохраняем все даты
        if node.temp > threshold:
            for date in node.dates:
                result.append((node.temp, date))
                
        # Рекурсивно идем в правое поддерево
        self._inorder_above(node.right, threshold, result)

    def weather_by_levels(self):
        """
        ВСТРОЕННАЯ ФУНКЦИЯ ОБХОДА ПО УРОВНЯМ (BFS).
        Возвращает список температур, распределенных по уровням иерархии дерева.
        """
        if self.root is None:
            return []

        result = []
        current_level = [self.root]

        while current_level:
            temps_of_level = []
            next_level = []

            for node in current_level:
                temps_of_level.append(node.temp)
                if node.left:  
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)

            result.append(temps_of_level)
            current_level = next_level

        return result


# =====================================================================
# 2. ОСНОВНОЙ КЛАСС СИСТЕМЫ ПОГОДНОГО АНАЛИЗА
# =====================================================================

class WeatherAnalyzer:
    def __init__(self):
        self.dates = []         # Список дат (строки)
        self.temps = []         # Список температур (числа)
        self.months = []        # Список месяцев (строки вида '01', '02'...)
        self.prefix = []        # Массив префиксных сумм для температур
        self.undo_stack = []    # Стек для отмены последнего преобразования

    def load_from_csv(self, filename):
        """Чтение CSV-файла и инициализация базовых списков."""
        self.dates.clear()
        self.temps.clear()
        self.months.clear()
        
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.dates.append(row['date'])
                self.temps.append(float(row['temp']))
                self.months.append(row['date'].split('-')[1]) # Выделяем месяц
                
        self._build_prefix_sums()

    def _build_prefix_sums(self):
        """Построение массива префиксных сумм с округлением на каждом шаге."""
        n = len(self.temps)
        if n == 0:
            self.prefix = []
            return
            
        self.prefix = [0.0] * n
        self.prefix[0] = self.temps[0]
        for i in range(1, n):
            # Округляем до 1 знака после запятой на каждом шаге суммирования
            self.prefix[i] = round(self.prefix[i - 1] + self.temps[i], 1)

    def _sum_l_r(self, l, r):
        """Быстрый подсчет суммы температур на отрезке индексов [l, r] через префиксные сумму."""
        if l == 0:
            return self.prefix[r]
        return round(self.prefix[r] - self.prefix[l - 1], 1)

    def calculate_monthly_averages(self):
        """
        Вычисление средней температуры за каждый месяц.
        Использует префиксные суммы для быстрого нахождения суммы интервалов.
        """
        if not self.temps:
            return {}

        monthly_averages = {}
        unique_months = sorted(list(set(self.months)))

        for m in unique_months:
            # Находим первый и последний индекс вхождения месяца в массиве (интервал)
            l = self.months.index(m)
            r = len(self.months) - 1 - self.months[::-1].index(m)
            
            # Считаем сумму за интервал с помощью префиксных сумм
            total_temp = self._sum_l_r(l, r)
            count = r - l + 1
            monthly_averages[m] = round(total_temp / count, 2)
            
        return monthly_averages

    def find_extremes(self):
        """Линейный поиск самого теплого и самого холодного дня."""
        if not self.temps:
            return None, None
            
        min_temp = self.temps[0]
        max_temp = self.temps[0]
        min_date = self.dates[0]
        max_date = self.dates[0]
        
        for i in range(1, len(self.temps)):
            if self.temps[i] < min_temp:
                min_temp = self.temps[i]
                min_date = self.dates[i]
            if self.temps[i] > max_temp:
                max_temp = self.temps[i]
                max_date = self.dates[i]
                
        return (min_date, min_temp), (max_date, max_temp)

    def sort_months_by_temp(self, monthly_averages):
        """Сортировка месяцев по средней температуре (Сортировка выбором / Selection Sort)."""
        months_list = list(monthly_averages.items())
        n = len(months_list)
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if months_list[j][1] < months_list[min_idx][1]:
                    min_idx = j
            months_list[i], months_list[min_idx] = months_list[min_idx], months_list[i]
            
        return months_list

    def find_days_above_threshold(self, threshold):
        """Строит БДП по температурам и возвращает все дни выше порога."""
        bst = WeatherBST()
        for i in range(len(self.temps)):
            bst.insert(self.temps[i], self.dates[i])
            
        return bst.find_above_threshold(threshold)

    def get_bst_hierarchy_by_levels(self):
        """Строит дерево и возвращает его поуровневый список температур."""
        bst = WeatherBST()
        for i in range(len(self.temps)):
            bst.insert(self.temps[i], self.dates[i])
        return bst.weather_by_levels()

    def smooth_temperatures(self):
        """
        Сглаживание температурного ряда методом скользящего среднего с окном 7 дней.
        Для хранения последних 7 значений используется очередь (deque).
        """
        # Сохраняем копию текущего состояния в стек отмены перед изменением ряда
        self.undo_stack.append(list(self.temps))
        
        smoothed = []
        window = deque(maxlen=7)
        
        for temp in self.temps:
            window.append(temp)
            # Текущее среднее по элементам в очереди
            smoothed.append(round(sum(window) / len(window), 2))
            
        self.temps = smoothed
        self._build_prefix_sums()  # Перестраиваем префиксы для нового ряда
        print("Ряд температур успешно сглажен!")

    def undo_last_transformation(self):
        """Стек для отмены последнего преобразования (сглаживания)."""
        if self.undo_stack:
            self.temps = self.undo_stack.pop()
            self._build_prefix_sums()
            print("Последнее преобразование успешно отменено!")
        else:
            print("Нечего отменять. Стек отмены пуст.")


# =====================================================================
# 3. ДЕМОНСТРАЦИЯ И СВЯЗУЮЩИЙ КОД
# =====================================================================

def create_sample_csv():
    """Генерация реалистичного CSV-файла за ПОЛНЫЙ ГОД (365 дней) для защиты проекта."""
    filename = "weather_data.csv"
    
    # Количество дней в каждом месяце (обычный год)
    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Примерная базовая температура для каждого месяца (зимой холодно, летом тепло)
    base_temps = [-10, -8, -2, 6, 13, 18, 22, 20, 14, 7, 0, -6]
    
    data = []
    
    # Инициализируем генератор случайных чисел фиксированным сидом, 
    # чтобы при каждом запуске генерировались одинаковые красивые данные
    random.seed(42)
    
    for month_idx, days_count in enumerate(days_in_months):
        month_str = f"{month_idx + 1:02d}"  # Формат '01', '02' ...
        base_t = base_temps[month_idx]
        
        for day in range(1, days_count + 1):
            day_str = f"{day:02d}"
            date_str = f"2026-{month_str}-{day_str}"
            
            # Добавляем случайное колебание погоды вокруг средней нормы месяца
            temp = round(base_t + random.uniform(-4.5, 4.5), 1)
            
            data.append({"date": date_str, "temp": str(temp)})
            
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "temp"])
        writer.writeheader()
        writer.writerows(data)
        
    return filename


if __name__ == "__main__":
   # Шаг 1: Создаем полноценную базу данных на 365 дней и загружаем ее
    csv_file = create_sample_csv()

    analyzer = WeatherAnalyzer()
    analyzer.load_from_csv(csv_file)

print(f"Данные за год загружены (дней в архиве: {len(analyzer.temps)})")
print("Первые 5 дат:", analyzer.dates[:5])
print("Первые 5 температур:", analyzer.temps[:5])
print("Первые 5 префиксных сумм:", analyzer.prefix[:5])
print("-" * 60)


# Шаг 2: Средняя температура за каждый месяц
print("\nСредняя температура по месяцам (расчет через префиксные суммы):")
monthly_avgs = analyzer.calculate_monthly_averages()
for month, avg_t in monthly_avgs.items():
    print(f"  Месяц {month}: {avg_t}°C")


# Шаг 3: Линейный поиск экстремумов
print("\nТемпературные рекорды года (линейный поиск):")
coldest, warmest = analyzer.find_extremes()
print(f"  Самый холодный день: {coldest[0]} ({coldest[1]}°C)")
print(f"  Самый теплый день:   {warmest[0]} ({warmest[1]}°C)")


# Шаг 4: Сортировка месяцев выбором
print("\nРейтинг месяцев от холодных к теплым (сортировка выбором):")
sorted_months = analyzer.sort_months_by_temp(monthly_avgs)
for month, avg_t in sorted_months:
    print(f"  Месяц {month}: {avg_t}°C")


# Шаг 5: Поиск через БДП
threshold_temp = 24.5
print(f"\nДни с аномальной жарой выше {threshold_temp}°C (через БДП):")
days_above = analyzer.find_days_above_threshold(threshold_temp)
print(f"  Найдено дней: {len(days_above)}")
for temp, date in days_above[:5]:  # Выведем первые 5 для компактности
    print(f"    {date} - {temp}°C")


# Шаг 6: Проверка широтно-уровневого обхода дерева (Выводим только верхушку для теста)
print("\nСтруктура температурного дерева по уровням (BFS):")
levels = analyzer.get_bst_hierarchy_by_levels()
print(f"  Всего уровней в дереве: {len(levels)}")
print(f"  Корень дерева (уровень 0): {levels[0]}")
print(f"  Потомки корня (уровень 1): {levels[1]}")


# Шаг 7: Скользящее среднее (очередь) и Стек отмены
print("\nОбработка данных (скользящее среднее 7 дней) и отмена:")
print("  Исходные температуры (первые 5 дней января): ", analyzer.temps[:5])

analyzer.smooth_temperatures()
print("  После сглаживания шума (первые 5 дней):        ", analyzer.temps[:5])
print("  Префиксные суммы после сглаживания:            ", analyzer.prefix[:5])

analyzer.undo_last_transformation()
print("  Отмена сглаживания, возвращены исходные данные: ", analyzer.temps[:5])