def format(moves):
    if moves is None:
        return "None"

    if moves % 1000 == 0:
        return str(moves // 1000)
    else:
        return str(moves / 1000)
