import sys
import pdb as bp

def F():
    a,b = 0,1
    yield a
    yield b
    while True:
        a, b = b, a + b
	bp.set_trace()
        yield b

def SubFib(startNumber, endNumber):
    for cur in F():
        if cur > endNumber: return
        if cur >= startNumber:
            yield cur

if __name__ == '__main__':
    init = int(sys.argv[1])
    end = int(sys.argv[2]) 
    for i in SubFib(init, end):
        print i
