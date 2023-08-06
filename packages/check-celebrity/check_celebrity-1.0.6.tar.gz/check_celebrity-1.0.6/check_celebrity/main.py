import celebrity_match

function_list = [func for func in dir(celebrity_match) if callable(getattr(celebrity_match, func))]
print(function_list)
