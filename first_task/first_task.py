from typing import Callable, Iterable, Optional, List, Dict
from collections import Counter

NUMBER_OF_ROWS: int = 80_000

def get_first_matching_object(predicate: Callable[[object], bool], objects: Optional[Iterable[object]] = None) -> Optional[object]:
    """
    Возвращает первый объект из iterable, удовлетворяющий условию predicate.
    Если таких объектов нет, возвращает None.

    Args:
        predicate: функция, принимающая объект и возвращающая bool.
        objects: итерируемая коллекция объектов (по умолчанию пустой список).

    Returns:
        Первый объект, для которого predicate вернул True, или None.
    """
    if objects is None:
        objects = []
    for obj in objects:
        if predicate(obj):
            return obj
    return None

def word_statistics(lines: List[str]) -> Dict[str, int]:
    """
    Подсчитывает частоту встречаемости слов в списке строк.
    Слова приводятся к нижнему регистру, знаки препинания запятая и точка удаляются.
    Если количество строк больше 80 000, возвращает пустой словарь.
    Результат отсортирован по частоте (убывание), при равных значениях — по слову (рост).

    Args:
        lines: список строк для анализа.

    Returns:
        Словарь, где ключ — слово в нижнем регистре, значение — количество его появлений.
    """
    if len(lines) > NUMBER_OF_ROWS:
        return {}

    freq = Counter()
    for line in lines:
        words = line.replace(",", " ").replace(".", " ").split()
        freq.update(word.lower() for word in words)

    sorted_stat = dict(sorted(freq.items(), key=lambda x: (-x[1], x[0])))
    return sorted_stat

