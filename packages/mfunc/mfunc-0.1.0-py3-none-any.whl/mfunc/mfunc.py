import dis
import sys
import os
class mfunc:
    def __init__(self,function):
        self.f=function
    def __getitem__(self,key):
        if isinstance(key,slice):
            return [self.f(x) for x in range(key.start or 0,key.stop,key.step or 1)]
        return self.f(key)
    def __repr__(self):
        return self.f
    def __add__(self,other):
        return mfunc(lambda x:self.f(x)+other.f(x))
    def __sub__(self,other):
        return mfunc(lambda x:self.f(x)-other.f(x))
    def __mul__(self,other):
        return mfunc(lambda x:self.f(x)*other.f(x))
    def __truediv__(self,other):
        return mfunc(lambda x:self.f(x)/other.f(x))
    def __floordiv__(self,other):
        return mfunc(lambda x:self.f(x)//other.f(x))
    def __pow__(self,other,mod):
        return mfunc(lambda x:pow(self.f(x),other.f(x),mod))
    def __radd__(self,other):
        return self+other
    def __rsub__(self,other):
        return other-self
    def __rmul__(self,other):
        return self*other
    def __rtruediv__(self,other):
        return other/self
    def __rfloordiv__(self,other):
        return other//self
    def __rpow__(self,other,mod):
        return pow(other,self,mod)
    def __eq__(self,other):
        out_backup=sys.stdout
        sys.stdout=open(os.devnull,"w")
        try:
            t=dis.dis(self.f)==dis.dis(other.f)
        finally:
            sys.stdout=out_backup
        return t