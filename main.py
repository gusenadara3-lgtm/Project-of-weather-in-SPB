import csv
from collections import deque

class Node:
    """Узел бинарного дерева поиска по температуре."""

    def __init__(self, temp, date):
        self.temp = temp
        self.dates = [date]
        self.left = None
        self.right = None


class WeatherBST:
    """Бинарное дерево поиска для работы с днями по значениям температуры."""

    def __init__(self):
        self.root = None

    def insert(self, temp, date):
        """Добавили новый день с заданной температурой в дерево."""
        if self.root is None:
            self.root = Node(temp, date)
        else:
            self._insert_rec(self.root, temp, date)

    def _insert_rec(self, node, temp, date):
        """Рекурсивная вставка узла в нужное место дерева."""
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

    def get_hot_days(self, threshold):
        """Нашли все дни с температурой выше заданного порога."""
        result = []
        self._traverse_hot_days(self.root, threshold, result)
        return result

    def _traverse_hot_days(self, node, threshold, result):
        """Обход дерева, который собирает все даты с температурой выше порога."""
        if node is None:
            return
        
        self._traverse_hot_days(node.left, threshold, result)
        
        if node.temp > threshold:
            for date in node.dates:
                result.append((node.temp, date))
                
        self._traverse_hot_days(node.right, threshold, result)

    def get_tree_levels(self):
        """Обход дерева по уровням (BFS), возвращает температуры по уровням."""
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


class WeatherAnalyzer:
    """Класс для загрузки, анализа и преобразования погодных данных."""

    def __init__(self):
        self.dates = []
        self.temps = []
        self.months = []
        self.prefix = []
        self.undo_stack = []

    def load_data(self, filename):
        """Загрузили данные из CSV и подготовить массивы для анализа."""
        self.dates.clear()
        self.temps.clear()
        self.months.clear()
        
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.dates.append(row['date'])
                self.temps.append(float(row['temp']))
                self.months.append(row['date'].split('-')[1])
                
        self._build_prefix()

    def _build_prefix(self):
        """Построили массив префиксных сумм температур для быстрых запросов по диапазонам."""
        n = len(self.temps)
        if n == 0:
            self.prefix = []
            return
            
        self.prefix = [0.0] * n
        self.prefix[0] = self.temps[0]
        for i in range(1, n):
            self.prefix[i] = round(self.prefix[i - 1] + self.temps[i], 1)

    def _sum_l_r(self, l, r):
        """Вернули сумму температур на отрезке индексов [l, r] используя префиксные суммы."""
        if l == 0:
            return self.prefix[r]
        return round(self.prefix[r] - self.prefix[l - 1], 1)

    def get_month_average(self):
        """Посчитали среднюю температуру по каждому месяцу."""
        if not self.temps:
            return {}

        monthly_averages = {}
        unique_months = sorted(list(set(self.months)))

        for m in unique_months:
            l = self.months.index(m)
            r = len(self.months) - 1 - self.months[::-1].index(m)
            
            total_temp = self._sum_l_r(l, r)
            count = r - l + 1
            monthly_averages[m] = round(total_temp / count, 2)
            
        return monthly_averages

    def get_min_max_day(self):
        """Найшли самый холодный и самый тёплый день за период."""
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

    def sort_months(self, monthly_averages):
        """Отсортировали месяцы по средней температуре с помощью сортировки выбором."""
        months_list = list(monthly_averages.items())
        n = len(months_list)
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if months_list[j][1] < months_list[min_idx][1]:
                    min_idx = j
            months_list[i], months_list[min_idx] = months_list[min_idx], months_list[i]
            
        return months_list

    def get_hot_days_bst(self, threshold):
        """Получили все дни с температурой выше порога, используя дерево поиска."""
        bst = WeatherBST()
        for i in range(len(self.temps)):
            bst.insert(self.temps[i], self.dates[i])
            
        return bst.get_hot_days(threshold)

    def get_bst_levels(self):
        """Построили дерево температур и вернули уровни дерева."""
        bst = WeatherBST()
        for i in range(len(self.temps)):
            bst.insert(self.temps[i], self.dates[i])
        return bst.get_tree_levels()

    def smooth_temps(self):
        """Сгладили температурный ряд скользящим средним с окном 7 дней и сохранили возможность отката."""
        self.undo_stack.append(list(self.temps))
        
        smoothed = []
        window = deque(maxlen=7)
        
        for temp in self.temps:
            window.append(temp)
            smoothed.append(round(sum(window) / len(window), 2))
            
        self.temps = smoothed
        self._build_prefix()
        print("Ряд температур успешно сглажен!")

    def undo_last_change(self):
        """Отменили последнее преобразование температурного ряда, если это возможно."""
        if self.undo_stack:
            self.temps = self.undo_stack.pop()
            self._build_prefix()
            print("Последнее преобразование успешно отменено!")
        else:
            print("Нечего отменять. Стек отмены пуст.")


if __name__ == "__main__":
    csv_file = "WEATHER_SPB.csv"

    analyzer = WeatherAnalyzer()
    analyzer.load_data(csv_file)

    print(f"Данные за год загружены (дней в архиве: {len(analyzer.temps)})")
    print("Первые 5 дат:", analyzer.dates[:5])
    print("Первые 5 температур:", analyzer.temps[:5])
    print("Первые 5 префиксных сумм:", analyzer.prefix[:5])
    print("-" * 60)

    print("\nСредняя температура по месяцам (расчет через префиксные суммы):")
    monthly_avgs = analyzer.get_month_average()
    for month, avg_t in monthly_avgs.items():
        print(f"  Месяц {month}: {avg_t}°C")

    print("\nТемпературные рекорды года (линейный поиск):")
    coldest, warmest = analyzer.get_min_max_day()
    print(f"  Самый холодный день: {coldest[0]} ({coldest[1]}°C)")
    print(f"  Самый теплый день:   {warmest[0]} ({warmest[1]}°C)")

    print("\nРейтинг месяцев от холодных к теплым (сортировка выбором):")
    sorted_months = analyzer.sort_months(monthly_avgs)
    for month, avg_t in sorted_months:
        print(f"  Месяц {month}: {avg_t}°C")

    threshold_temp = 24.5
    print(f"\nДни с аномальной жарой выше {threshold_temp}°C (через БДП):")
    days_above = analyzer.get_hot_days_bst(threshold_temp)
    print(f"  Найдено дней: {len(days_above)}")
    for temp, date in days_above[:5]:
        print(f"    {date} - {temp}°C")

    print("\nСтруктура температурного дерева по уровням (BFS):")
    levels = analyzer.get_bst_levels()
    print(f"  Всего уровней в дереве: {len(levels)}")
    print(f"  Корень дерева (уровень 0): {levels[0]}")
    print(f"  Потомки корня (уровень 1): {levels[1]}")

    print("\nОбработка данных (скользящее среднее 7 дней) и отмена:")
    print("  Исходные температуры (первые 5 дней января): ", analyzer.temps[:5])

    analyzer.smooth_temps()
    print("  После сглаживания шума (первые 5 дней):        ", analyzer.temps[:5])
    print("  Префиксные суммы после сглаживания:            ", analyzer.prefix[:5])

    analyzer.undo_last_change()
    print("  Отмена сглаживания, возвращены исходные данные: ", analyzer.temps[:5]) сглаживания, возвращены исходные данные: ", analyzer.temps[:5])
