from main import get_first_matching_object, word_statistics

def test_get_first_matching_object():
    assert get_first_matching_object(lambda x: x > 0, [0, -1, 2, 3]) == 2
    assert get_first_matching_object(lambda x: x == 'a', ['b', 'a', 'c']) == 'a'
    assert get_first_matching_object(lambda x: x == 5, [1, 2, 3]) is None
    assert get_first_matching_object(lambda x: True, []) is None
    assert get_first_matching_object(lambda x: True) is None

def test_word_statistics():
    assert word_statistics([]) == {}
    assert word_statistics(['Hello, hello.']) == {'hello': 2}
    assert word_statistics(['Repeat repeat REPEAT']) == {'repeat': 3}
    # Проверка сортировки по частоте (убывание) и слову (возрастание)
    result = word_statistics(['banana, apple.Apple banana. cherry'])
    assert list(result.keys()) == ['apple', 'banana', 'cherry']
    # Проверка ограничения по количеству строк
    assert word_statistics(['word'] * 80_001) == {}