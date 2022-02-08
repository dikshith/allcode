from functools import wraps

def a_new_decorator(a_func):
    @wraps(a_func)
    def wrapTheFunction():
        print("I am doing some boring work before executing a_func()")
        a_func()
        print("I am doing some boring work after executing a_func()")
    return wrapTheFunction

@a_new_decorator
def a_function_requiring_decoration():
    print("I am the function which needs some decoration to remove my foul smell")

#a_function_requiring_decoration()
#outputs: "I am the function which needs some decoration to remove my foul smell"

#the @a_new_decorator is just a short way of saying:
#a_function_requiring_decoration = a_new_decorator(a_function_requiring_decoration)
#now a_function_requiring_decoration is wrapped by wrapTheFunction()

a_function_requiring_decoration()

print(a_function_requiring_decoration.__name__)
# Output: wrapTheFunction

from functools import wraps

def logit(logfile='output.log'):
    def logging_decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            log_string = func.__name__ + " was called"
            print(log_string)
            #open the logfile and append
            with open(logfile,'a') as opened_file:
                #now we write specific log
                opened_file.write(log_string + '\n')
            return func(*args,**kwargs)
        return wrapped_function
    return logging_decorator

@logit()
def myfunc():
    pass

myfunc()

@logit(logfile='func2.log')
def myfunc2():
    pass

myfunc2()