from first_task.first_task import get_first_matching_object, word_statistics, NUMBER_OF_ROWS

NEW_NUMBER_OF_ROWS = NUMBER_OF_ROWS + 1


def test_get_first_matching_object():
    """
    Тесты для функции get_first_matching_object.
    """
    assert get_first_matching_object(lambda x: x > 0, [0, -1, 2, 3]) == 2
    assert get_first_matching_object(lambda x: x == 'a', ['b', 'a', 'c']) == 'a'
    assert get_first_matching_object(lambda x: x == 5, [1, 2, 3]) is None
    assert get_first_matching_object(lambda x: True, []) is None
    assert get_first_matching_object(lambda x: True) is None



def test_word_statistics():
    """
    Тесты для функции word_statistics.
    """
    assert word_statistics([]) == {}
    assert word_statistics(['']) == {}
    assert word_statistics(['Hello, hello.']) == {'hello': 2}
    assert word_statistics(['Repeat repeat REPEAT']) == {'repeat': 3}
    result = word_statistics(['banana, apple.Apple banana. cherry'])
    assert list(result.keys()) == ['apple', 'banana', 'cherry']
    assert word_statistics(['word'] * NEW_NUMBER_OF_ROWS) == {}