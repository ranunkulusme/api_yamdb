from django.core.exceptions import ValidationError


def validate_score(value):
    """
    Валидация оценки произведения,
    :param value: значение приходящее от пользователя
    :return: цело число от 0 до 10, иначе возбуждается ошибка
    """

    if 0 <= value <= 10:
        return value
    raise ValidationError(
        f'Не допустимое значение, введите значение от 0 до 10'
    )