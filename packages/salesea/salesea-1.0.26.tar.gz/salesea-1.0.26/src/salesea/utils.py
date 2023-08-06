from sys import stdout

def out_print(*args, end='\n'):
    stdout.write("".join([str(_) for _ in args]) + end)
    stdout.flush()