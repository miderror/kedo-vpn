def pluralize_days(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return "ДЕНЬ"
    elif n % 10 in [2, 3, 4] and n % 100 not in [12, 13, 14]:
        return "ДНЯ"
    else:
        return "ДНЕЙ"
