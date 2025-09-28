from zodiac import infer_zodiac


def test_leo():
assert infer_zodiac(8, 20) == 'Leo'


def test_capricorn_wrap():
assert infer_zodiac(1, 10) == 'Capricorn'
