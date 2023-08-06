#ifndef _pylyramilk_native_h_
#define _pylyramilk_native_h_

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#if PY_MAJOR_VERSION == 3
	//#define PyString_FromStringAndSize PyBytes_FromStringAndSize
	#define PyString_FromStringAndSize PyUnicode_FromStringAndSize
#endif



template <typename T>
struct pylyramilkObject{
	PyObject_HEAD
	T* obj;
} ;

#endif
