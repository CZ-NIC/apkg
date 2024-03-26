def custom_fun_add(a, b):
    return a + b


def get_variables(_):
    return {
            'custom_fun_add': custom_fun_add,
            'custom_fun_echo': lambda x: str(x),
    }
