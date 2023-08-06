#include "pytree.h"
#include <string.h>
#include <errno.h>

bool static load_data(shareabledict_object* obj)
{
	if(obj->avt){
		delete obj->avt;
		obj->avt = NULL;
	}
	if(obj->sbr){
		delete obj->sbr;
		obj->sbr = NULL;
	}
	if(obj->avp){
		delete obj->avp;
		obj->avp = NULL;
	}

	char* pbase = NULL;
	if(!obj->sm.init(obj->key,0,0)){
		return false;
	}
	pbase = obj->sm.ptr();

	unsigned long totalsize = 0;
	memcpy(&totalsize,pbase,sizeof(totalsize));
	unsigned int magic = 0x5025;
	memcpy(&magic,pbase+sizeof(unsigned long long)/*totalsize的值*/,sizeof(magic));
	if(magic != 0x5025){
		return false;
	}

	unsigned long avloffset = sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/ + sizeof(unsigned long)/*avl树在stringbox中的id*/;

	obj->avp = new tree_compare();
	obj->avp->sb = obj->sbr = new lyramilk::data::stringbox_reader(pbase + avloffset,totalsize - avloffset);

	unsigned long avlid = 0;
	memcpy(&avlid,pbase + sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/,sizeof(avlid));

	const char* avldata = NULL;
	unsigned long avlsize = 0;

	if(!obj->sbr->get(avlid,&avldata,&avlsize)){
		return false;
	}

	obj->avt = new lyramilk::bintree::avltree(obj->avp);
	obj->avt->mmap(avldata,avlsize);
	
	return true;
}



PyObject * py_shareabledict_get(PyObject *self, PyObject *args)
{
	if(self == NULL){
		Py_RETURN_NONE;
	}

	const char *skey;
	Py_ssize_t lkey;
	if (!(PyArg_ParseTuple(args, "s#", &skey, &lkey))) {
		Py_RETURN_NONE;
	}


	shareabledict_object* obj = ((pylyramilkObject<shareabledict_object>*)(self))->obj;

	obj->avp->sv = skey;
	obj->avp->lv = lkey;

	const void* data;
	if(lyramilk::bintree::ec_ok == obj->avt->get((void*)(unsigned long)-1l,&data)){
		unsigned long tmp;
		boxdata *d1;
		obj->sbr->get((unsigned long)data,(const char**)&d1,&tmp);
		const char *s1;
		unsigned long l1;
		obj->sbr->get(d1->ival,&s1,&l1);
		PyObject* sobj = PyString_FromStringAndSize(s1,l1);
		return sobj;
	}

	Py_RETURN_NONE;
}

PyObject * py_shareabledict_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject * self = type->tp_alloc(type, 0);
	if(self){
		char *sname;
		Py_ssize_t lname;
		if (PyArg_ParseTuple(args, "s#", &sname, &lname)) {

			pylyramilkObject<shareabledict_object>* pobj = ((pylyramilkObject<shareabledict_object>*)(self));
			shareabledict_object* obj = pobj->obj = new shareabledict_object;


			obj->key = strtokey(sname,lname,SHARED_TYPE_AVL);
			sharememory sm;
			if(!sm.init(obj->key,0,0)){
				delete obj;
				Py_TYPE(self)->tp_free((PyObject*)self);
				PyErr_SetString(PyExc_OSError, strerror(errno));
				return NULL;
			}

			if(load_data(obj)){
				return self;
			}
			delete obj;
			Py_TYPE(self)->tp_free((PyObject*)self);
			PyErr_SetString(PyExc_OSError, strerror(errno));
			return NULL;
		}
	}
	PyErr_SetString(PyExc_OSError, strerror(errno));
	return NULL;
}

void py_shareabledict_dealloc(PyObject* self)
{
	shareabledict_object* obj = ((pylyramilkObject<shareabledict_object>*)(self))->obj;

	if(obj->avt){
		delete obj->avt;
		obj->avt = NULL;
	}
	if(obj->sbr){
		delete obj->sbr;
		obj->sbr = NULL;
	}
	if(obj->avp){
		delete obj->avp;
		obj->avp = NULL;
	}

	delete obj;
	Py_TYPE(self)->tp_free((PyObject*)self);
}







PyMethodDef pyshareabledictObjectClassMethods[] = {
	{"get", py_shareabledict_get, METH_VARARGS},
	{NULL, NULL},
};

PyTypeObject shareabledict_ObjectType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"sharedmap.sharedmap",			/*tp_name*/
	sizeof(pylyramilkObject<shareabledict_object>),		/*tp_basicsize*/
	0, /*tp_itemsize*/
	py_shareabledict_dealloc,
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
	"sharedmap desc", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	pyshareabledictObjectClassMethods, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	0, /* tp_init */
	0, /* tp_alloc */
	py_shareabledict_new, /* tp_new */
};
