#include "pytree.h"
#include <vector>
#include <string.h>
#include <errno.h>

extern PyTypeObject shareablebitmap_ObjectType;


template <int T>
struct intc;

template <>
struct intc<2>
{
	enum {
		square = 1,
	};
};

template <>
struct intc<4>
{
	enum {
		square = 2
	};
};

template <>
struct intc<8>
{
	enum {
		square = 3
	};
};



bool static load_data(shared_bitmap_object* obj)
{
	char* pbase = obj->sm.ptr();

	unsigned int magic = 0x5026;
	memcpy(&magic,pbase,sizeof(magic));
	if(magic != 0x5026){
		return false;
	}

	obj->p = (long*)(pbase + 8);
	obj->size = (long)(pbase + obj->sm.size() - (const char*)obj->p + 7) >> intc<sizeof(long)>::square;
	return true;
}

PyObject * py_shared_bitmap_set(PyObject *self, PyObject *args)
{
	if(self == NULL){
		return NULL;
	}
	long index = 0;
	char val = 0;
	if (!(PyArg_ParseTuple(args, "lb",&index, &val))) {
		return NULL;
	}
	shared_bitmap_object* obj = ((pylyramilkObject<shared_bitmap_object>*)(self))->obj;

	long offset = index % sizeof(long);
	long bytesindex = index  >> intc<sizeof(long)>::square;
	if(bytesindex > obj->size){
		PyErr_SetString(PyExc_KeyError, "index out of range");
		return NULL;
	}

	if(val){
		obj->p[bytesindex] |= 1<<offset;
	}else{
		obj->p[bytesindex] &= ~(1<<offset);
	}
	Py_RETURN_NONE;
}

PyObject * py_shared_bitmap_size(PyObject *self, PyObject *args)
{
	if(self == NULL){
		return NULL;
	}
	shared_bitmap_object* obj = ((pylyramilkObject<shared_bitmap_object>*)(self))->obj;
	return Py_BuildValue("l",obj->size << intc<sizeof(long)>::square);
}

PyObject * py_shared_bitmap_resize(PyObject *self, PyObject *args)
{
	if(self == NULL){
		return NULL;
	}
	long size = 0;
	if (!(PyArg_ParseTuple(args, "l",&size))) {
		return NULL;
	}
	long totalsize = size + 8;
	shared_bitmap_object* obj = ((pylyramilkObject<shared_bitmap_object>*)(self))->obj;

	if(obj->sm.resize(totalsize)){
		if(load_data(obj)){
			Py_RETURN_TRUE;
		}
	}
	Py_RETURN_FALSE;
}

PyObject * py_shared_bitmap_get(PyObject *self, PyObject *args)
{
	if(self == NULL){
		return NULL;
	}
	long index = 0;
	if (!(PyArg_ParseTuple(args, "l",&index))) {
		return NULL;
	}
	shared_bitmap_object* obj = ((pylyramilkObject<shared_bitmap_object>*)(self))->obj;
	long offset = index % sizeof(long);
	long bytesindex = index  >> intc<sizeof(long)>::square;

	if(bytesindex > obj->size){
		PyErr_SetString(PyExc_KeyError, "index out of range");
		return NULL;
	}

	if(obj->p[bytesindex] & (1<<offset)){
		Py_RETURN_TRUE;
	}
	Py_RETURN_FALSE;
}

PyObject * py_shared_bitmap_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject * self = type->tp_alloc(type, 0);
	if(self){
		char *sname;
		Py_ssize_t lname;
		char force = 0;

		static const char *kwlist[] = {"name", "force",NULL};
		if (!(PyArg_ParseTupleAndKeywords(args,kwds, "s#|b",(char**)kwlist, &sname, &lname,&force))) {
			Py_RETURN_NONE;
		}


		if (PyArg_ParseTuple(args, "s#", &sname, &lname)) {
			pylyramilkObject<shared_bitmap_object>* pobj = ((pylyramilkObject<shared_bitmap_object>*)(self));
			shared_bitmap_object* obj = pobj->obj = new shared_bitmap_object;
			obj->sharedmemoryname.assign(sname,lname);
			obj->key = strtokey(sname,lname,SHARED_TYPE_BITMAP);

			if(!obj->sm.init(obj->key,0,0)){
				delete obj;
				Py_TYPE(self)->tp_free((PyObject*)self);
				PyErr_SetString(PyExc_OSError, strerror(errno));
				return NULL;
			}

			if(load_data(obj)){
				return self;
			}
			delete obj;
		}
		Py_TYPE(self)->tp_free((PyObject*)self);
		PyErr_SetString(PyExc_OSError, strerror(errno));
		return NULL;
	}
	PyErr_SetString(PyExc_OSError, strerror(errno));
	return NULL;
}

PyObject * py_shared_bitmap_create(PyTypeObject *, PyObject *args, PyObject *kwds)
{
	PyTypeObject *type = &shareablebitmap_ObjectType;

	PyObject * self = type->tp_alloc(type, 0);
	if(self){
		char *sname;
		Py_ssize_t lname;
		long size = 0;
		char force = 0;

		static const char *kwlist[] = {"name", "size", "force",NULL};
		if (PyArg_ParseTupleAndKeywords(args,kwds, "s#l|b",(char**)kwlist, &sname, &lname, &size,&force)) {
			long totalsize = size + 8;
			pylyramilkObject<shared_bitmap_object>* pobj = ((pylyramilkObject<shared_bitmap_object>*)(self));
			shared_bitmap_object* obj = pobj->obj = new shared_bitmap_object;
			obj->sharedmemoryname.assign(sname,lname);
			obj->key = strtokey(sname,lname,SHARED_TYPE_BITMAP);

			if(!obj->sm.init(obj->key,totalsize,IPC_CREAT|IPC_EXCL|0666)){
				if(errno == EEXIST && force == 1){
					if(!sharememory::remove(obj->key)){
						delete obj;
						Py_TYPE(self)->tp_free((PyObject*)self);
						PyErr_SetString(PyExc_OSError, strerror(errno));
						return NULL;
					}
					if(!obj->sm.init(obj->key,totalsize,IPC_CREAT|IPC_EXCL|0666)){
						delete obj;
						Py_TYPE(self)->tp_free((PyObject*)self);
						PyErr_SetString(PyExc_OSError, strerror(errno));
						return NULL;
					}
				}else{
					delete obj;
					Py_TYPE(self)->tp_free((PyObject*)self);
					PyErr_SetString(PyExc_OSError, strerror(errno));
					return NULL;
				}
			}


			char* psharedmemory = obj->sm.ptr();
			unsigned int magic = 0x5026;
			memcpy(psharedmemory,&magic,sizeof(magic));

			if(load_data(obj)){
				return self;
			}
			delete obj;
		}
		Py_TYPE(self)->tp_free((PyObject*)self);
		PyErr_SetString(PyExc_OSError, strerror(errno));
		return NULL;
	}
	PyErr_SetString(PyExc_OSError, strerror(errno));
	return NULL;
}


void py_shared_bitmap_dealloc(PyObject* self)
{
	shared_bitmap_object* obj = ((pylyramilkObject<shared_bitmap_object>*)(self))->obj;


	delete obj;
	Py_TYPE(self)->tp_free((PyObject*)self);
}


/*
	申请内存对于整个服务器来说不是一个安全操作，如果通过size的index实现自动扩容，有可能因为传入了一个无效数字导致申请了过大的内存，所以resize必须主动调用，不实现自动扩容。
*/


PyMethodDef pyshareablebitmapObjectClassMethods[] = {
	{"create", (PyCFunction)py_shared_bitmap_create, METH_VARARGS | METH_STATIC|METH_KEYWORDS},
	{"set", py_shared_bitmap_set, METH_VARARGS},
	{"get", py_shared_bitmap_get, METH_VARARGS},
	{"size", py_shared_bitmap_size, METH_VARARGS},
	{"resize", py_shared_bitmap_resize, METH_VARARGS},
	{NULL, NULL},
};

PyTypeObject shareablebitmap_ObjectType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"sharedmap.sharedbitmap",				/*tp_name*/
	sizeof(pylyramilkObject<shared_bitmap_object>),		/*tp_basicsize*/
	0, /*tp_itemsize*/
	py_shared_bitmap_dealloc,
	0, /* tp_print */
	0, /* tp_getattr */
	0, /* tp_setattr */
	0, /* tp_reserved */
	0, /* tp_repr */
	0, /* tp_as_number */
	0, /* tp_as_sequence */
	0, /* tp_as_mapping */
	0, /* tp_hash */
	0, /* tp_call */
	0, /* tp_str */
	0, /* tp_getattro */
	0, /* tp_setattro */
	0, /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
	"sharedbitmap desc", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	pyshareablebitmapObjectClassMethods, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	0, /* tp_init */
	0, /* tp_alloc */
	py_shared_bitmap_new, /* tp_new */
};
