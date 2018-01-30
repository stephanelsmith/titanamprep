
import time
import functools

#retry decorator
def retrywrap(retries, delay=0, fnwarn=None, warnkwargs={}):
    def outter(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            for x in range(retries):
                try:
                    return func(*args, **kwargs)
                except SystemExit:
                    raise
                except Exception, err:
                    if callable(fnwarn):
                        fnwarn(**warnkwargs) #call warning message
                    time.sleep(delay)

                    if x == retries-1:
                        raise #reraise if last attempt
        return inner
    return outter

#retry functions
def retryfunc(retries=3, delay=0, func=None, args=[], kwargs={}, fnwarn=None, warnkwargs={}):
    if callable(func):
        for x in range(retries):
            try:
                return func(*args, **kwargs)
            except SystemExit:
                raise
            except Exception, err:
                if callable(fnwarn):
                    fnwarn(**warnkwargs) #call warning message
                time.sleep(delay)

                if x == retries-1:
                    raise #reraise if last attempt


if __name__ == '__main__':

    @retrywrap(3)
    def foo2(max):
        for x in range(max):
            if x == 5:
                raise Exception('-E-')
            print x

    def warn(msg=''):
        print msg

    @retrywrap(3, fnwarn=warn, warnkwargs={'msg':'-W-'})
    def foo2(max):
        for x in range(max):
            if x == 5:
                raise Exception('-E-')
            print x

    def foo3(max):
        for x in range(max):
            if x == 5:
                raise Exception('-E-')
            print x

    #foo2(max=10)

    print
    kwargs = {'max':10}
    retryfunc(retries=2, func=foo3, kwargs=kwargs,\
              fnwarn=warn, warnkwargs={'msg':'-W-'})






