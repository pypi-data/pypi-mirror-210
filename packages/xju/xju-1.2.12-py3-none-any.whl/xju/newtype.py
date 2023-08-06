# Copyright (c) 2022 Trevor Taylor
# coding: utf-8
# 
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that all
# copyright notices and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# Utilities for creating distinct types mirroring a subset of a basic
# type (str, int, float).
#
# Unlike typing.NewType:
#   - works with isinstance (at runtime)
#   - many methods of the basic type are provided directly, e.g. for
#     new int type A, A+A->A
#
# For example to define an int-like Hours class:
#
#  class HoursTag:pass
#  class Hours(Int[HoursTag]):pass
#
# ... note do not use 'Hours=Int[HoursTag]' because that is an alias to a generic and
# therefore has not run-time presence and therefore cannot be used with isinstance.
#
from typing import Iterable,Sized,Container,Collection,Reversible,Protocol,Type,overload,TypeVar
from typing import Generic,Tuple,Mapping,Optional,List,Literal,Union,Any,Self

Tag=TypeVar('Tag',covariant=True)

def verify_same_type(x:Any,y:Any):
    if x.__class__ is not y.__class__:
        raise Exception(f"{x!r}'s type {x.__class__} is not the same as {y!r}'s type {y.__class__}")
    pass

def eq(x:Any,y:Any)->bool:
    verify_same_type(x,y)
    return x.value().__eq__(y.value())

class Int(Generic[Tag]):
    __value:int

    def __init__(self, value:int):
        self.__value=value
        pass

    def value(self)->int:
        return self.__value

    def __eq__(self,other)->bool:
        '''equality test, only valid for two object of exactly the same class; except that
           python insists supporting __eq__ for objects of any type, so this function's signature
           allows it and calls out all nonsense at runtime'''
        '''i.e. recommend stick to using Int[X] like:
              class Hours(Int[HoursTag]):pass
           ... and not inherit from Hours.
           If you choose to inherit from Hours, make sure you write your own __eq__'''
        return eq(self,other)

    def __ne__(self,other)->bool:
        return not eq(self,other)

    def __str__(self)->str:
        return str(self.value())

    def __repr__(self)->str:
        return repr(self.value())

    def __format__(self, format_spec:str)->str:
        return self.value().__format__(format_spec)

    def __float__(self)->float:
        return self.value().__float__()
    
    def conjugate(self):
        return self.value().conjugate()

    @overload
    def __divmod__(self, x:int) -> Tuple[Self,Self]:
        pass
    @overload
    def __divmod__(self, x:float) -> Tuple[float,float]:
        pass
    @overload
    def __divmod__(self, x:Self) -> Tuple[int,int]:
        pass
    def __divmod__(self, x):
        if isinstance(x,int):
            q,r=self.value().__divmod__(x)
            return self.__class__(q),self.__class__(r)
        if isinstance(x,float):
            return divmod(self.value(),x)
        else:
            return divmod(self.value(),x.value())
        pass

    @overload
    def __floordiv__(self, x:int) -> Self:
        pass
    @overload
    def __floordiv__(self, x:float) -> float:
        pass
    @overload
    def __floordiv__(self, x:Self) -> int:
        pass
    def __floordiv__(self, x):
        if isinstance(x,int):
            return self.__class__(self.value()//x)
        elif isinstance(x,float):
            return self.value()//x
        else:
            return self.value()//x.value()
        pass

    def __truediv__(self, x:float|int|Self) -> float:
        if isinstance(x,float) or isinstance(x,int):
            return self.value()/x
        else:
            return self.value()/x.value()
        pass
    
    @overload
    def __mul__(self, x:int) -> Self:
        pass
    @overload
    def __mul__(self, x:Any):  # -> NotImplemented:
        pass
    def __mul__(self, x):
        if isinstance(x,int):
            return self.__class__(self.value()*x)
        else:
            return NotImplemented
        pass

    @overload
    def __rmul__(self, x:int):  # -> Self:
        pass
    @overload
    def __rmul__(self, x:Any):  # -> NotImplemented
        pass
    def __rmul__(self, x):
        if isinstance(x,int):
            return self.__class__(x*self.value())
        else:
            return NotImplemented
        pass

    @overload
    def __mod__(self, other:int)->Self:
        pass
    @overload
    def __mod__(self, other:float)->float:
        pass
    @overload
    def __mod__(self, other:Self)->int:
        pass
    def __mod__(self, other):
        if type(other) is int:
            return self.__class__(self.value()%other)
        if type(other) is float:
            return self.value()%other
        else:
            return self.value()%other.value()

    def __round__(self, ndigits:int=0)->Self:
        return self.__class__(self.value().__round__(ndigits))

    
    def __abs__(self) -> Self:
        return self.__class__(self.value().__abs__())
    def __invert__(self) -> Self:
        return self.__class__(self.value().__invert__())
    def __neg__(self) -> Self:
        return self.__class__(self.value().__neg__())
    def __pos__(self) -> Self:
        return self.__class__(self.value().__pos__())
    def __int__(self)->int:
        return self.value().__int__()
    def __sizeof__(self)->int:
        return self.value().__sizeof__()
    def bit_count(self)->int:
        return self.value().bit_count()
    def bit_length(self)->int:
        return self.value().bit_length()
    def __index__(self)->int:
        return self.value().__index__()
    def __hash__(self)->int:
        return self.value().__hash__()
    def __bool__(self)->bool:
        return self.value().__bool__()
    def __ror__(self,n:int) -> Self:
        return self.__class__(self.value().__ror__(n))
    def __rrshift__(self,n:int) -> Self:
        return self.__class__(self.value().__rrshift__(n))
    def __lshift__(self,n:int) -> Self:
        return self.__class__(self.value().__lshift__(n))
    def __rlshift__(self,n:int) -> Self:
        return self.__class__(self.value().__rlshift__(n))
    def __rshift__(self,n:int) -> Self:
        return self.__class__(self.value().__rshift__(n))
    def __gt__(self,other:Self)->bool:
        return self.value().__gt__(other.value())
    def __lt__(self,other:Self)->bool:
        return self.value().__lt__(other.value())
    def __le__(self,other:Self)->bool:
        return self.value().__le__(other.value())
    def __ge__(self,other:Self)->bool:
        return self.value().__ge__(other.value())
    def __add__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__add__(other.value()))
    def __sub__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__sub__(other.value()))
    def __and__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__and__(other.value()))
    def __or__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__or__(other.value()))
    def __xor__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__xor__(other.value()))
    def as_integer_ratio(self)->Tuple[int,int]:
        return self.value().as_integer_ratio()

    pass


class Float(Generic[Tag]):
    __value:float

    def __init__(self, value:float):
        self.__value=value
        pass

    def value(self)->float:
        return self.__value

    def __eq__(self,other)->bool:
        '''equality test, only valid for two object of exactly the same class; except
           that python insists on supporting __eq__ for objects of any type, so this
           function's signature allows it and calls out all nonsense at runtime'''
        '''i.e. recommend stick to using Float[X] like:
              class Timestamp(Float[TimestampTag]):pass
           ... and not inherit from Timestamp.
           If you choose to inherit from Timestamp, make sure you write your own __eq__'''
        return eq(self,other)

    def __ne__(self,other)->bool:
        return not eq(self,other)

    def __str__(self)->str:
        return str(self.value())

    def __repr__(self)->str:
        return repr(self.value())

    def __format__(self, format_spec:str)->str:
        return self.value().__format__(format_spec)

    def __int__(self)->int:
        return self.value().__int__()
    
    def __float__(self)->float:
        return self.value().__float__()
    
    def hex(self)->str:
        return self.value().hex()
    
    def conjugate(self):
        return self.value().conjugate()

    @overload
    def __divmod__(self, x:int) -> Tuple[Self,Self]:
        pass
    @overload
    def __divmod__(self, x:float) -> Tuple[Self,Self]:
        pass
    @overload
    def __divmod__(self, x:Self) -> Tuple[float,float]:
        pass
    def __divmod__(self, x):
        if isinstance(x,int) or isinstance(x,float):
            q,r=self.value().__divmod__(x)
            return self.__class__(q),self.__class__(r)
        else:
            return divmod(self.value(),x.value())
        pass

    @overload
    def __floordiv__(self, x:int) -> Self:
        pass
    @overload
    def __floordiv__(self, x:float) -> Self:
        pass
    @overload
    def __floordiv__(self, x:Self) -> float:
        pass
    def __floordiv__(self, x):
        if isinstance(x,int) or isinstance(x,float):
            return self.__class__(self.value()//x)
        else:
            return self.value()//x.value()
        pass

    @overload
    def __truediv__(self, x:Union[float,int]) -> Self:
        pass
    @overload
    def __truediv__(self, x:Self) -> float:
        pass
    def __truediv__(self, x):
        if isinstance(x,int) or isinstance(x,float):
            return self.__class__(self.value()/x)
        else:
            return self.value()/x.value()
        pass
    
    @overload
    def __mul__(self, x:int) -> Self:
        pass
    @overload
    def __mul__(self, x:float) -> Self:
        pass
    def __mul__(self, x):
        return self.__class__(self.value()*x)

    @overload
    def __rmul__(self, x:int) -> Self:
        pass
    @overload
    def __rmul__(self, x:float) -> Self:
        pass
    def __rmul__(self, x):
        return self.__class__(x*self.value())

    @overload
    def __mod__(self, other:int)->Self:
        pass
    @overload
    def __mod__(self, other:float)->Self:
        pass
    @overload
    def __mod__(self, other:Self)->float:
        pass
    def __mod__(self, other):
        if isinstance(other,int) or isinstance(other,float):
            return self.__class__(self.value()%other)
        else:
            return self.value()%other.value()

    def __round__(self, ndigits:int=0)->Self:
        return self.__class__(self.value().__round__(ndigits))

    
    def __abs__(self)->Self:
        return self.__class__(self.value().__abs__())
    def __neg__(self)->Self:
        return self.__class__(self.value().__neg__())
    def __pos__(self)->Self:
        return self.__class__(self.value().__pos__())
    def __trunc__(self)->Self:
        return self.__class__(self.value().__trunc__())
    def __ceil__(self)->Self:
        return self.__class__(self.value().__ceil__())
    def __floor__(self)->Self:
        return self.__class__(self.value().__floor__())
    def __sizeof__(self)->int:
        return self.value().__sizeof__()
    def __hash__(self)->int:
        return self.value().__hash__()
    def __bool__(self)->bool:
        return float(self.value()).__bool__()
    def is_integer(self)->bool:
        return float(self.value()).is_integer()
    def __gt__(self,other:Self)->bool:
        return self.value().__gt__(other.value())
    def __lt__(self,other:Self)->bool:
        return self.value().__lt__(other.value())
    def __le__(self,other:Self)->bool:
        return self.value().__le__(other.value())
    def __ge__(self,other:Self)->bool:
        return self.value().__ge__(other.value())
    def __add__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__add__(other.value()))
    def __sub__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__sub__(other.value()))
    def as_integer_ratio(self)->Tuple[float,float]:
        return self.value().as_integer_ratio()

    pass


class Str(Generic[Tag]):
    __value:str
    def __init__(self, value:str):
        self.__value=value
        pass

    def value(self)->str:
        return self.__value

    def __eq__(self,other)->bool:
        '''equality test ignores possible subclass relationships, i.e. only valid
           for two object of exactly the same class; except that python insists
           supporting __eq__ for objects of any type, so this functions allows
           comparing any Str[X] with anything but calls out nonsense at runtime'''
        '''i.e. recommend stick to using Str[X] like:
              class FirstName(Str[FirstNameTag]):pass
           ... and not inherit from FirstName.
           If you choose to inherit from Timestamp, make sure you write your own __eq__'''
        return eq(self,other)

    def __ne__(self,other)->bool:
        return not eq(self,other)

    def __str__(self)->str:
        return str(self.value())

    def __repr__(self)->str:
        return repr(self.value())

    def __format__(self, format_spec:str)->str:
        return self.value().__format__(format_spec)

    def splitlines(self,keepends=False)->List:
        return [self.__class__(_) for _ in self.value().splitlines()]

    def encode(self,encoding:str='utf-8', errors:str='strict')->bytes:
        return self.value().encode()

    def __contains__(self,other:str)->bool:
        return self.value().__contains__(other)

    def zfill(self,width:int)->Self:
        return self.__class__(self.value().zfill(width))

    def format_map(self,mapping:Mapping):
        return self.__class__(self.value().format_map(mapping))

    def format(self,*args,**kwargs):
        return self.__class__(self.value().format(*args,**kwargs))
    
    def expandtabs(self,tabsize=8)->Self:
        return self.__class__(self.value().expandtabs(tabsize))

    def __getitem__(self,key):
        return self.value().__getitem__(key)

    
    def capitalize(self)->Self:
        return self.__class__(self.value().capitalize())
    def lower(self)->Self:
        return self.__class__(self.value().lower())
    def swapcase(self)->Self:
        return self.__class__(self.value().swapcase())
    def title(self)->Self:
        return self.__class__(self.value().title())
    def casefold(self)->Self:
        return self.__class__(self.value().casefold())
    def upper(self)->Self:
        return self.__class__(self.value().upper())
    def __len__(self)->int:
        return self.value().__len__()
    def __sizeof__(self)->int:
        return self.value().__sizeof__()
    def __hash__(self)->int:
        return self.value().__hash__()
    def isalnum(self)->bool:
        return self.value().isalnum()
    def isdecimal(self)->bool:
        return self.value().isdecimal()
    def isidentifier(self)->bool:
        return self.value().isidentifier()
    def isprintable(self)->bool:
        return self.value().isprintable()
    def isascii(self)->bool:
        return self.value().isascii()
    def islower(self)->bool:
        return self.value().islower()
    def isnumeric(self)->bool:
        return self.value().isnumeric()
    def isspace(self)->bool:
        return self.value().isspace()
    def isupper(self)->bool:
        return self.value().isupper()
    def isalpha(self)->bool:
        return self.value().isalpha()
    def isdigit(self)->bool:
        return self.value().isdigit()
    def istitle(self)->bool:
        return self.value().istitle()
    def __mul__(self,n:int)->Self:
        return self.__class__(self.value().__mul__(n))
    def __gt__(self,other:Self)->bool:
        return self.value().__gt__(other.value())
    def __lt__(self,other:Self)->bool:
        return self.value().__lt__(other.value())
    def __le__(self,other:Self)->bool:
        return self.value().__le__(other.value())
    def __ge__(self,other:Self)->bool:
        return self.value().__ge__(other.value())
    def __add__(self,other:Self)->Self:
        if type(other) is not type(self):
            return NotImplemented
        return self.__class__(self.value().__add__(other.value()))
    @overload
    def rfind(self, sub:str) -> int:
        pass
    @overload
    def rfind(self, sub:str, start:int)->int:
        pass
    @overload
    def rfind(self, sub:str, start:int, end:int)->int:
        pass
    def rfind(self, sub, *args):
        return self.value().rfind(sub,*args)
    @overload
    def find(self, sub:str) -> int:
        pass
    @overload
    def find(self, sub:str, start:int)->int:
        pass
    @overload
    def find(self, sub:str, start:int, end:int)->int:
        pass
    def find(self, sub, *args):
        return self.value().find(sub,*args)
    @overload
    def rindex(self, sub:str) -> int:
        pass
    @overload
    def rindex(self, sub:str, start:int)->int:
        pass
    @overload
    def rindex(self, sub:str, start:int, end:int)->int:
        pass
    def rindex(self, sub, *args):
        return self.value().rindex(sub,*args)
    @overload
    def index(self, sub:str) -> int:
        pass
    @overload
    def index(self, sub:str, start:int)->int:
        pass
    @overload
    def index(self, sub:str, start:int, end:int)->int:
        pass
    def index(self, sub, *args):
        return self.value().index(sub,*args)
    @overload
    def count(self, sub:str) -> int:
        pass
    @overload
    def count(self, sub:str, start:int)->int:
        pass
    @overload
    def count(self, sub:str, start:int, end:int)->int:
        pass
    def count(self, sub, *args):
        return self.value().count(sub,*args)
    @overload
    def translate(self, sub:str) -> int:
        pass
    @overload
    def translate(self, sub:str, start:int)->int:
        pass
    @overload
    def translate(self, sub:str, start:int, end:int)->int:
        pass
    def translate(self, sub, *args):
        return self.value().translate(sub,*args)
    @overload
    def endswith(self, s:str) -> bool:
        pass
    @overload
    def endswith(self, s:str, start:int)->bool:
        pass
    @overload
    def endswith(self, s:str, start:int, end:int)->bool:
        pass
    def endswith(self, s, *args):
        return self.value().endswith(s,*args)
    @overload
    def startswith(self, s:str) -> bool:
        pass
    @overload
    def startswith(self, s:str, start:int)->bool:
        pass
    @overload
    def startswith(self, s:str, start:int, end:int)->bool:
        pass
    def startswith(self, s, *args):
        return self.value().startswith(s,*args)
    def strip(self, chars:Optional[str]=None)->Self:
        return self.__class__(self.value().strip(chars))
    def lstrip(self, chars:Optional[str]=None)->Self:
        return self.__class__(self.value().lstrip(chars))
    def rstrip(self, chars:Optional[str]=None)->Self:
        return self.__class__(self.value().rstrip(chars))
    def replace(self, old:str, new:str, count=-1)->Self:
        return self.__class__(self.value().replace(old,new,count))
    def split(self, sep:Optional[str]=None, max_split=-1)->List[str]:
        return self.value().split(sep,max_split)
    def rsplit(self, sep:Optional[str]=None, max_split=-1)->List[str]:
        return self.value().rsplit(sep,max_split)
    def partition(self,sep:str) -> Tuple[str,str,str]:
        return self.value().partition(sep)
    def rpartition(self,sep:str) -> Tuple[str,str,str]:
        return self.value().rpartition(sep)
    def removeprefix(self,sub:str)->Self:
        return self.__class__(self.value().removeprefix(sub))
    def removesuffix(self,sub:str)->Self:
        return self.__class__(self.value().removesuffix(sub))
    def center(self,width:int,fillchar:str=' ')->Self:
        return self.__class__(self.value().center(width,fillchar))
    def ljust(self,width:int,fillchar:str=' ')->Self:
        return self.__class__(self.value().ljust(width,fillchar))
    def rjust(self,width:int,fillchar:str=' ')->Self:
        return self.__class__(self.value().rjust(width,fillchar))

    pass

