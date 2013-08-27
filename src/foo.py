def foo(a):

    try:
        print 100 / a
    except ZeroDivisionError:
        print "zzzzzerrrrroooo"
        return None
    except:
        print "error catched"
        raise
    finally:
        print "FINALLY!"


def bar():
    print 100 / 0


def baz():
    # context manager
    with open("udi.txt") as f:
        return f.readlines()[9]


def kuku():
    pass

foo(0)
