# $BEGIN_AUDIOMATH_LICENSE$
# 
# This file is part of the audiomath project, a Python package for
# recording, manipulating and playing sound files.
# 
# Copyright (c) 2008-2023 Jeremy Hill
# 
# audiomath is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# The audiomath distribution includes binaries from the third-party
# AVbin and PortAudio projects, released under their own licenses.
# See the respective copyright, licensing and disclaimer information
# for these projects in the subdirectories `audiomath/_wrap_avbin`
# and `audiomath/_wrap_portaudio` . It also includes a fork of the
# third-party Python package `pycaw`, released under its original
# license (see `audiomath/pycaw_fork.py`).
# 
# $END_AUDIOMATH_LICENSE$

'''
Wrapper for portaudio.h

Generated with::
	python ctypesgen.py  -lportaudio32bit -lportaudio64bit ../pa_stable_v190600_20161030/portaudio/include/portaudio.h -o portaudio.py
	2to3 -w portaudio.py

...then modified by hand in many places
'''

__docformat__ =  'restructuredtext'

# Begin preamble
import os, sys, platform, inspect, struct
import ctypes, ctypes.util; from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

def POINTER(obj):
    if getattr( obj, '__name__', None ) == 'CFunctionType': return obj # easier than removing the automatically-generated POINTER() wrappers that shouldn't be there, below
    elif obj is None: return ctypes.c_void_p
    else: return ctypes.POINTER( obj )

NULL = POINTER(None)()


class UserString:
    def __init__(self, seq):
        if isinstance(seq, str):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return int(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, str):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, str):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, str):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, str):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble

###########

def LoadLib( dllNameStem, usePlatformInflection=True, searchIfNotFoundHere=True ):
	machine = platform.machine().lower()
	if machine in [ '', 'i386', 'x86_64', 'amd64' ]:
		arch = '%dbit' % ( struct.calcsize( 'P' ) * 8 ) # remember this will depend on the Python executable, not just the machine
	else:
		arch = machine
		if arch.startswith( 'armv' ): arch = arch.rstrip( 'l' )
	uname = platform.system()
	if   uname.lower().startswith( 'win'    ): dllPrefix, dllExtension = '',    '.dll'
	elif uname.lower().startswith( 'darwin' ): dllPrefix, dllExtension = 'lib', '.dylib'
	else:                                      dllPrefix, dllExtension = 'lib', '.so'
	platformInflection = '-' + uname + '-' + arch
	if isinstance( usePlatformInflection, str ) and usePlatformInflection.lower() == 'win64only':
		platformInflection = '64' if platformInflection == '-Windows-64bit' else ''
	uninflectedStem = dllNameStem
	if usePlatformInflection: dllNameStem += platformInflection
	dllName = ( '' if dllNameStem.startswith( dllPrefix ) else dllPrefix ) + dllNameStem + dllExtension
	dllNameStem = dllNameStem[ len( dllPrefix ): ]
	try: file = __file__
	except NameError: file = None
	if not file:
		try: frame = inspect.currentframe(); file = inspect.getfile( frame )
		finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
	HERE = os.path.dirname( os.path.realpath( file ) )
	dllPath = os.path.join( HERE, dllName )
	if not os.path.isfile( dllPath ) and searchIfNotFoundHere:
		found = ctypes.util.find_library( uninflectedStem )
		if not found and uninflectedStem.startswith( 'lib' ): found = ctypes.util.find_library( uninflectedStem[ 3: ] )
		if found: dllPath = found
	try: dll = ctypes.CDLL( dllPath )
	except Exception as err:
		msg = "file exists, but may be corrupt" if os.path.isfile( dllPath ) else "file is missing---perhaps it has not been compiled for your platform?"
		raise OSError( "%s\nfailed to load shared library %s\n%s" % ( err, os.path.basename( dllPath ), msg ) )
	return dll

###########
_libs = {}
_libs[ 'portaudio' ] = LoadLib( 'libportaudio' )

# No modules

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 58
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetVersion'):
        continue
    Pa_GetVersion = _lib.Pa_GetVersion
    Pa_GetVersion.argtypes = []
    Pa_GetVersion.restype = c_int
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 67
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetVersionText'):
        continue
    Pa_GetVersionText = _lib.Pa_GetVersionText
    Pa_GetVersionText.argtypes = []
    if sizeof(c_int) == sizeof(c_void_p):
        Pa_GetVersionText.restype = ReturnString
    else:
        Pa_GetVersionText.restype = String
        Pa_GetVersionText.errcheck = ReturnString
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 102
class struct_PaVersionInfo(Structure):
    pass

struct_PaVersionInfo.__slots__ = [
    'versionMajor',
    'versionMinor',
    'versionSubMinor',
    'versionControlRevision',
    'versionText',
]
struct_PaVersionInfo._fields_ = [
    ('versionMajor', c_int),
    ('versionMinor', c_int),
    ('versionSubMinor', c_int),
    ('versionControlRevision', String),
    ('versionText', String),
]

PaVersionInfo = struct_PaVersionInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 102

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 114
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetVersionInfo'):
        continue
    Pa_GetVersionInfo = _lib.Pa_GetVersionInfo
    Pa_GetVersionInfo.argtypes = []
    Pa_GetVersionInfo.restype = POINTER(PaVersionInfo)
    break

PaError = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 121

enum_PaErrorCode = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paNoError = 0 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paNotInitialized = (-10000) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paUnanticipatedHostError = (paNotInitialized + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInvalidChannelCount = (paUnanticipatedHostError + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInvalidSampleRate = (paInvalidChannelCount + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInvalidDevice = (paInvalidSampleRate + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInvalidFlag = (paInvalidDevice + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paSampleFormatNotSupported = (paInvalidFlag + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paBadIODeviceCombination = (paSampleFormatNotSupported + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInsufficientMemory = (paBadIODeviceCombination + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paBufferTooBig = (paInsufficientMemory + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paBufferTooSmall = (paBufferTooBig + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paNullCallback = (paBufferTooSmall + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paBadStreamPtr = (paNullCallback + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paTimedOut = (paBadStreamPtr + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInternalError = (paTimedOut + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paDeviceUnavailable = (paInternalError + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paIncompatibleHostApiSpecificStreamInfo = (paDeviceUnavailable + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paStreamIsStopped = (paIncompatibleHostApiSpecificStreamInfo + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paStreamIsNotStopped = (paStreamIsStopped + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInputOverflowed = (paStreamIsNotStopped + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paOutputUnderflowed = (paInputOverflowed + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paHostApiNotFound = (paOutputUnderflowed + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paInvalidHostApi = (paHostApiNotFound + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paCanNotReadFromACallbackStream = (paInvalidHostApi + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paCanNotWriteToACallbackStream = (paCanNotReadFromACallbackStream + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paCanNotReadFromAnOutputOnlyStream = (paCanNotWriteToACallbackStream + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paCanNotWriteToAnInputOnlyStream = (paCanNotReadFromAnOutputOnlyStream + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paIncompatibleStreamHostApi = (paCanNotWriteToAnInputOnlyStream + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

paBadBufferPtr = (paIncompatibleStreamHostApi + 1) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

PaErrorCode = enum_PaErrorCode # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 155

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 161
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetErrorText'):
        continue
    Pa_GetErrorText = _lib.Pa_GetErrorText
    Pa_GetErrorText.argtypes = [PaError]
    if sizeof(c_int) == sizeof(c_void_p):
        Pa_GetErrorText.restype = ReturnString
    else:
        Pa_GetErrorText.restype = String
        Pa_GetErrorText.errcheck = ReturnString
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 183
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_Initialize'):
        continue
    Pa_Initialize = _lib.Pa_Initialize
    Pa_Initialize.argtypes = []
    Pa_Initialize.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 202
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_Terminate'):
        continue
    Pa_Terminate = _lib.Pa_Terminate
    Pa_Terminate.argtypes = []
    Pa_Terminate.restype = PaError
    break

PaDeviceIndex = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 212

PaHostApiIndex = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 238

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 250
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetHostApiCount'):
        continue
    Pa_GetHostApiCount = _lib.Pa_GetHostApiCount
    Pa_GetHostApiCount.argtypes = []
    Pa_GetHostApiCount.restype = PaHostApiIndex
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 261
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetDefaultHostApi'):
        continue
    Pa_GetDefaultHostApi = _lib.Pa_GetDefaultHostApi
    Pa_GetDefaultHostApi.argtypes = []
    Pa_GetDefaultHostApi.restype = PaHostApiIndex
    break

enum_PaHostApiTypeId = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paInDevelopment = 0 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paDirectSound = 1 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paMME = 2 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paASIO = 3 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paSoundManager = 4 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paCoreAudio = 5 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paOSS = 7 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paALSA = 8 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paAL = 9 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paBeOS = 10 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paWDMKS = 11 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paJACK = 12 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paWASAPI = 13 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

paAudioScienceHPI = 14 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

PaHostApiTypeId = enum_PaHostApiTypeId # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 291

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 324
class struct_PaHostApiInfo(Structure):
    pass

struct_PaHostApiInfo.__slots__ = [
    'structVersion',
    'type',
    'name',
    'deviceCount',
    'defaultInputDevice',
    'defaultOutputDevice',
]
struct_PaHostApiInfo._fields_ = [
    ('structVersion', c_int),
    ('type', PaHostApiTypeId),
    ('name', String),
    ('deviceCount', c_int),
    ('defaultInputDevice', PaDeviceIndex),
    ('defaultOutputDevice', PaDeviceIndex),
]

PaHostApiInfo = struct_PaHostApiInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 324

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 340
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetHostApiInfo'):
        continue
    Pa_GetHostApiInfo = _lib.Pa_GetHostApiInfo
    Pa_GetHostApiInfo.argtypes = [PaHostApiIndex]
    Pa_GetHostApiInfo.restype = POINTER(PaHostApiInfo)
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 358
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_HostApiTypeIdToHostApiIndex'):
        continue
    Pa_HostApiTypeIdToHostApiIndex = _lib.Pa_HostApiTypeIdToHostApiIndex
    Pa_HostApiTypeIdToHostApiIndex.argtypes = [PaHostApiTypeId]
    Pa_HostApiTypeIdToHostApiIndex.restype = PaHostApiIndex
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 382
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_HostApiDeviceIndexToDeviceIndex'):
        continue
    Pa_HostApiDeviceIndexToDeviceIndex = _lib.Pa_HostApiDeviceIndexToDeviceIndex
    Pa_HostApiDeviceIndexToDeviceIndex.argtypes = [PaHostApiIndex, c_int]
    Pa_HostApiDeviceIndexToDeviceIndex.restype = PaDeviceIndex
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 393
class struct_PaHostErrorInfo(Structure):
    pass

struct_PaHostErrorInfo.__slots__ = [
    'hostApiType',
    'errorCode',
    'errorText',
]
struct_PaHostErrorInfo._fields_ = [
    ('hostApiType', PaHostApiTypeId),
    ('errorCode', c_long),
    ('errorText', String),
]

PaHostErrorInfo = struct_PaHostErrorInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 393

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 409
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetLastHostErrorInfo'):
        continue
    Pa_GetLastHostErrorInfo = _lib.Pa_GetLastHostErrorInfo
    Pa_GetLastHostErrorInfo.argtypes = []
    Pa_GetLastHostErrorInfo.restype = POINTER(PaHostErrorInfo)
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 422
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetDeviceCount'):
        continue
    Pa_GetDeviceCount = _lib.Pa_GetDeviceCount
    Pa_GetDeviceCount.argtypes = []
    Pa_GetDeviceCount.restype = PaDeviceIndex
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 431
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetDefaultInputDevice'):
        continue
    Pa_GetDefaultInputDevice = _lib.Pa_GetDefaultInputDevice
    Pa_GetDefaultInputDevice.argtypes = []
    Pa_GetDefaultInputDevice.restype = PaDeviceIndex
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 449
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetDefaultOutputDevice'):
        continue
    Pa_GetDefaultOutputDevice = _lib.Pa_GetDefaultOutputDevice
    Pa_GetDefaultOutputDevice.argtypes = []
    Pa_GetDefaultOutputDevice.restype = PaDeviceIndex
    break

PaTime = c_double # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 460

PaSampleFormat = c_ulong # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 484

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 517
class struct_PaDeviceInfo(Structure):
    pass

struct_PaDeviceInfo.__slots__ = [
    'structVersion',
    'name',
    'hostApi',
    'maxInputChannels',
    'maxOutputChannels',
    'defaultLowInputLatency',
    'defaultLowOutputLatency',
    'defaultHighInputLatency',
    'defaultHighOutputLatency',
    'defaultSampleRate',
]
struct_PaDeviceInfo._fields_ = [
    ('structVersion', c_int),
    ('name', String),
    ('hostApi', PaHostApiIndex),
    ('maxInputChannels', c_int),
    ('maxOutputChannels', c_int),
    ('defaultLowInputLatency', PaTime),
    ('defaultLowOutputLatency', PaTime),
    ('defaultHighInputLatency', PaTime),
    ('defaultHighOutputLatency', PaTime),
    ('defaultSampleRate', c_double),
]

PaDeviceInfo = struct_PaDeviceInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 517

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 533
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetDeviceInfo'):
        continue
    Pa_GetDeviceInfo = _lib.Pa_GetDeviceInfo
    Pa_GetDeviceInfo.argtypes = [PaDeviceIndex]
    Pa_GetDeviceInfo.restype = POINTER(PaDeviceInfo)
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 581
class struct_PaStreamParameters(Structure):
    pass

struct_PaStreamParameters.__slots__ = [
    'device',
    'channelCount',
    'sampleFormat',
    'suggestedLatency',
    'hostApiSpecificStreamInfo',
]
struct_PaStreamParameters._fields_ = [
    ('device', PaDeviceIndex),
    ('channelCount', c_int),
    ('sampleFormat', PaSampleFormat),
    ('suggestedLatency', PaTime),
    ('hostApiSpecificStreamInfo', POINTER(None)),
]

PaStreamParameters = struct_PaStreamParameters # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 581

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 609
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_IsFormatSupported'):
        continue
    Pa_IsFormatSupported = _lib.Pa_IsFormatSupported
    Pa_IsFormatSupported.argtypes = [POINTER(PaStreamParameters), POINTER(PaStreamParameters), c_double]
    Pa_IsFormatSupported.restype = PaError
    break

PaStream = None # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 635

PaStreamFlags = c_ulong # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 653

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 703
class struct_PaStreamCallbackTimeInfo(Structure):
    pass

struct_PaStreamCallbackTimeInfo.__slots__ = [
    'inputBufferAdcTime',
    'currentTime',
    'outputBufferDacTime',
]
struct_PaStreamCallbackTimeInfo._fields_ = [
    ('inputBufferAdcTime', PaTime),
    ('currentTime', PaTime),
    ('outputBufferDacTime', PaTime),
]

PaStreamCallbackTimeInfo = struct_PaStreamCallbackTimeInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 703

PaStreamCallbackFlags = c_ulong # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 712

enum_PaStreamCallbackResult = c_int # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 758

paContinue = 0 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 758

paComplete = 1 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 758

paAbort = 2 # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 758

PaStreamCallbackResult = enum_PaStreamCallbackResult # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 758

PaStreamCallback = CFUNCTYPE(UNCHECKED(c_int), POINTER(None), POINTER(None), c_ulong, POINTER(PaStreamCallbackTimeInfo), PaStreamCallbackFlags, POINTER(None)) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 830

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 892
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_OpenStream'):
        continue
    Pa_OpenStream = _lib.Pa_OpenStream
    Pa_OpenStream.argtypes = [POINTER(POINTER(PaStream)), POINTER(PaStreamParameters), POINTER(PaStreamParameters), c_double, c_ulong, PaStreamFlags, POINTER(PaStreamCallback), POINTER(None)]
    Pa_OpenStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 932
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_OpenDefaultStream'):
        continue
    Pa_OpenDefaultStream = _lib.Pa_OpenDefaultStream
    Pa_OpenDefaultStream.argtypes = [POINTER(POINTER(PaStream)), c_int, c_int, PaSampleFormat, c_double, c_ulong, POINTER(PaStreamCallback), POINTER(None)]
    Pa_OpenDefaultStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 945
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_CloseStream'):
        continue
    Pa_CloseStream = _lib.Pa_CloseStream
    Pa_CloseStream.argtypes = [POINTER(PaStream)]
    Pa_CloseStream.restype = PaError
    break

PaStreamFinishedCallback = CFUNCTYPE(UNCHECKED(None), POINTER(None)) # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 962

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 983
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_SetStreamFinishedCallback'):
        continue
    Pa_SetStreamFinishedCallback = _lib.Pa_SetStreamFinishedCallback
    Pa_SetStreamFinishedCallback.argtypes = [POINTER(PaStream), POINTER(PaStreamFinishedCallback)]
    Pa_SetStreamFinishedCallback.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 988
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_StartStream'):
        continue
    Pa_StartStream = _lib.Pa_StartStream
    Pa_StartStream.argtypes = [POINTER(PaStream)]
    Pa_StartStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 994
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_StopStream'):
        continue
    Pa_StopStream = _lib.Pa_StopStream
    Pa_StopStream.argtypes = [POINTER(PaStream)]
    Pa_StopStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1000
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_AbortStream'):
        continue
    Pa_AbortStream = _lib.Pa_AbortStream
    Pa_AbortStream.argtypes = [POINTER(PaStream)]
    Pa_AbortStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1015
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_IsStreamStopped'):
        continue
    Pa_IsStreamStopped = _lib.Pa_IsStreamStopped
    Pa_IsStreamStopped.argtypes = [POINTER(PaStream)]
    Pa_IsStreamStopped.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1031
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_IsStreamActive'):
        continue
    Pa_IsStreamActive = _lib.Pa_IsStreamActive
    Pa_IsStreamActive.argtypes = [POINTER(PaStream)]
    Pa_IsStreamActive.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1069
class struct_PaStreamInfo(Structure):
    pass

struct_PaStreamInfo.__slots__ = [
    'structVersion',
    'inputLatency',
    'outputLatency',
    'sampleRate',
]
struct_PaStreamInfo._fields_ = [
    ('structVersion', c_int),
    ('inputLatency', PaTime),
    ('outputLatency', PaTime),
    ('sampleRate', c_double),
]

PaStreamInfo = struct_PaStreamInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1069

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1085
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetStreamInfo'):
        continue
    Pa_GetStreamInfo = _lib.Pa_GetStreamInfo
    Pa_GetStreamInfo.argtypes = [POINTER(PaStream)]
    Pa_GetStreamInfo.restype = POINTER(PaStreamInfo)
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1103
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetStreamTime'):
        continue
    Pa_GetStreamTime = _lib.Pa_GetStreamTime
    Pa_GetStreamTime.argtypes = [POINTER(PaStream)]
    Pa_GetStreamTime.restype = PaTime
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1122
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetStreamCpuLoad'):
        continue
    Pa_GetStreamCpuLoad = _lib.Pa_GetStreamCpuLoad
    Pa_GetStreamCpuLoad.argtypes = [POINTER(PaStream)]
    Pa_GetStreamCpuLoad.restype = c_double
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1146
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_ReadStream'):
        continue
    Pa_ReadStream = _lib.Pa_ReadStream
    Pa_ReadStream.argtypes = [POINTER(PaStream), POINTER(None), c_ulong]
    Pa_ReadStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1173
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_WriteStream'):
        continue
    Pa_WriteStream = _lib.Pa_WriteStream
    Pa_WriteStream.argtypes = [POINTER(PaStream), POINTER(None), c_ulong]
    Pa_WriteStream.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1186
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetStreamReadAvailable'):
        continue
    Pa_GetStreamReadAvailable = _lib.Pa_GetStreamReadAvailable
    Pa_GetStreamReadAvailable.argtypes = [POINTER(PaStream)]
    Pa_GetStreamReadAvailable.restype = c_long
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1197
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetStreamWriteAvailable'):
        continue
    Pa_GetStreamWriteAvailable = _lib.Pa_GetStreamWriteAvailable
    Pa_GetStreamWriteAvailable.argtypes = [POINTER(PaStream)]
    Pa_GetStreamWriteAvailable.restype = c_long
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1208
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_GetSampleSize'):
        continue
    Pa_GetSampleSize = _lib.Pa_GetSampleSize
    Pa_GetSampleSize.argtypes = [PaSampleFormat]
    Pa_GetSampleSize.restype = PaError
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1218
for _lib in _libs.values():
    if not hasattr(_lib, 'Pa_Sleep'):
        continue
    Pa_Sleep = _lib.Pa_Sleep
    Pa_Sleep.argtypes = [c_long]
    Pa_Sleep.restype = None
    break

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 81
def paMakeVersionNumber(major, minor, subminor):
    return ((((major & 255) << 16) | ((minor & 255) << 8)) | (subminor & 255))

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 220
try:
    paNoDevice = (-1)
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 228
try:
    paUseHostApiSpecificDeviceSpecification = (-2)
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 487
try:
    paFloat32 = 1
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 488
try:
    paInt32 = 2
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 489
try:
    paInt24 = 4
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 490
try:
    paInt16 = 8
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 491
try:
    paInt8 = 16
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 492
try:
    paUInt8 = 32
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 493
try:
    paCustomFormat = 65536
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 495
try:
    paNonInterleaved = 2147483648
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 585
try:
    paFormatIsSupported = 0
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 642
try:
    paFramesPerBufferUnspecified = 0
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 656
try:
    paNoFlag = 0
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 661
try:
    paClipOff = 1
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 666
try:
    paDitherOff = 2
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 677
try:
    paNeverDropInput = 4
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 685
try:
    paPrimeOutputBuffersUsingStreamCallback = 8
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 690
try:
    paPlatformSpecificFlags = 4294901760
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 721
try:
    paInputUnderflow = 1
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 730
try:
    paInputOverflow = 2
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 736
try:
    paOutputUnderflow = 4
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 741
try:
    paOutputOverflow = 8
except:
    pass

# pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 747
try:
    paPrimingOutput = 16
except:
    pass

PaVersionInfo = struct_PaVersionInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 102

PaHostApiInfo = struct_PaHostApiInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 324

PaHostErrorInfo = struct_PaHostErrorInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 393

PaDeviceInfo = struct_PaDeviceInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 517

PaStreamParameters = struct_PaStreamParameters # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 581

PaStreamCallbackTimeInfo = struct_PaStreamCallbackTimeInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 703

PaStreamInfo = struct_PaStreamInfo # pa_stable_v190600_20161030\\portaudio\\include\\portaudio.h: 1069

# No inserted files	
