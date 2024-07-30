def x_or_y(data):
    try:
        data = bool(data)
        if data:
            return '✅'
        else:
            return '❌'
    except Exception as err:
        logging.error(err)
        return ''