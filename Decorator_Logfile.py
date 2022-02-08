# Luckily, classes can also be used to build decorators. So, let’s rebuild logit as a class instead of a function.

class logit(object):

    _log_file = 'outclass.log'

    def __init__(self,func):
        self.func = func
    
    def __call__(self, *args):
        log_string = self.func.__name__ + "was called"
        print(log_string)

        with open(self._log_file, 'a') as opened_file:
             opened_file.write(log_string + '\n')

        # return base func
        return self.func(*args)

class email_logit(logit):
    
    '''A logit implementation for sending emails to admins when the function is called.'''
    def __init__(self, email='admin@dixit.com', *args,**kwargs):
        self.email=email
        super(email_logit,self).__init__(*args,**kwargs)

    def notify(self):
        # Send an email to self.email
        pass

logit._logfile = 'out2.log' # if change log file
@email_logit
def myfunc1():
    pass

myfunc1()
# Output: myfunc1 was called



