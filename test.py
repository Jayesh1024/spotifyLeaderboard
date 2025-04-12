def tenX(func):
    def wrapper(*args,**kwargs):
        res = func(*args,**kwargs)
        return 10 * res
    return wrapper

@tenX
def add_items(val1,val2):
    return val1 + val2

print(add_items(5,5))