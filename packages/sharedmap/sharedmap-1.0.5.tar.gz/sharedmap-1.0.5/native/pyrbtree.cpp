#include "pytree.h"
#include <vector>
#include <string.h>
#include <errno.h>

PyObject * py_rbtree_set(PyObject *self, PyObject *args)
{
	if(self == NULL){
		return NULL;
	}
	const char *skey,*sval;
	Py_ssize_t lkey,lval;
	if (!(PyArg_ParseTuple(args, "s#s#", &skey, &lkey,&sval,&lval))) {
		return NULL;
	}
	rbtree_object* obj = ((pylyramilkObject<rbtree_object>*)(self))->obj;

	if(obj->sb == NULL) obj->sb = new lyramilk::data::stringbox();
	if(obj->avp == NULL){
		obj->avp= new tree_compare;
		obj->avp->sb = obj->sb;
	}
	if(obj->rbt == NULL) obj->rbt = new lyramilk::bintree::rbtree(obj->avp);
	boxdata avd;
	avd.ikey = obj->sb->alloc(skey,lkey);
	avd.ival = obj->sb->alloc(sval,lval);
	unsigned long idat = obj->sb->alloc((const char*)&avd,sizeof(avd));
	const void* p;
	obj->rbt->insert((void*)idat,&p);
	Py_RETURN_TRUE;
}

PyObject * py_rbtree_get(PyObject *self, PyObject *args)
{
	if(self == NULL){
		Py_RETURN_NONE;
	}

	const char *skey;
	Py_ssize_t lkey;
	if (!(PyArg_ParseTuple(args, "s#", &skey, &lkey))) {
		Py_RETURN_NONE;
	}

	rbtree_object* obj = ((pylyramilkObject<rbtree_object>*)(self))->obj;
	obj->avp->sv = skey;
	obj->avp->lv = lkey;

	const void* data;
	if(lyramilk::bintree::ec_ok == obj->rbt->get((void*)(unsigned long)-1l,&data)){
		unsigned long tmp;
		boxdata *d1;
		obj->sb->get((unsigned long)data,(const char**)&d1,&tmp);
		const char *s1;
		unsigned long l1;
		obj->sb->get(d1->ival,&s1,&l1);
		PyObject* sobj = PyString_FromStringAndSize(s1,l1);
		return sobj;
	}

	Py_RETURN_NONE;
}

PyObject * py_rbtree_share(PyObject *self, PyObject *args, PyObject *kwds)
{
	if(self == NULL){
		Py_RETURN_NONE;
	}
	const char *sname;
	Py_ssize_t lname;

	char force = 0;

	static const char *kwlist[] = {"name", "force",NULL};
	if (!(PyArg_ParseTupleAndKeywords(args,kwds, "s#|b",(char**)kwlist, &sname, &lname,&force))) {
		Py_RETURN_NONE;
	}


	rbtree_object* obj = ((pylyramilkObject<rbtree_object>*)(self))->obj;

	lyramilk::bintree::avltree tv(obj->avp);

	lyramilk::bintree::viterator* iter = obj->rbt->create_iterator();
	tv.from(iter,obj->rbt->size());
	obj->rbt->destory_iterator(iter);

	char* avlptr = (char*)tv.ptr();
	unsigned long avlsize = tv.bytescount();

	unsigned long avlid = obj->sb->alloc(avlptr,avlsize);

	unsigned long totalsize = sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/ + sizeof(unsigned long)/*avl树在stringbox中的id*/ + obj->sb->size();


	key_t key = strtokey(sname,lname,SHARED_TYPE_AVL);

	sharememory sm;
	if(!sm.init(key,totalsize,IPC_CREAT|IPC_EXCL|0666)){
		if(errno == EEXIST && force == 1){
			if(!sharememory::remove(key)){
				PyErr_SetString(PyExc_OSError, strerror(errno));
				return NULL;
			}
			if(!sm.init(key,totalsize,IPC_CREAT|IPC_EXCL|0666)){
				PyErr_SetString(PyExc_OSError, strerror(errno));
				return NULL;
			}
		}else{
			PyErr_SetString(PyExc_OSError, strerror(errno));
			return NULL;
		}
	}

	char* psharedmemory = sm.ptr();
	memcpy(psharedmemory,&totalsize,sizeof(totalsize));
	unsigned int magic = 0x5025;
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/,&magic,sizeof(magic));
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/,&avlid,sizeof(avlid));
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/ + sizeof(unsigned long)/*avl树在stringbox中的id*/,obj->sb->sb.c_str(),obj->sb->sb.size());
	Py_RETURN_TRUE;
}

PyObject * py_rbtree_dump(PyObject *self, PyObject *args)
{
	if(self == NULL){
		Py_RETURN_NONE;
	}

	rbtree_object* obj = ((pylyramilkObject<rbtree_object>*)(self))->obj;

	lyramilk::bintree::avltree tv(obj->avp);

	lyramilk::bintree::viterator* iter = obj->rbt->create_iterator();
	tv.from(iter,obj->rbt->size());
	obj->rbt->destory_iterator(iter);

	char* avlptr = (char*)tv.ptr();
	unsigned long avlsize = tv.bytescount();

	unsigned long avlid = obj->sb->alloc(avlptr,avlsize);

	unsigned long totalsize = sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/ + sizeof(unsigned long)/*avl树在stringbox中的id*/ + obj->sb->size();


	std::vector<char> buff;
	buff.resize(totalsize);

	char* psharedmemory = buff.data();
	memcpy(psharedmemory,&totalsize,sizeof(totalsize));
	unsigned int magic = 0x5025;
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/,&magic,sizeof(magic));
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/,&avlid,sizeof(avlid));
	memcpy(psharedmemory + sizeof(unsigned long long)/*totalsize的值*/ + sizeof(unsigned int)/*魔法数*/ + sizeof(unsigned long)/*avl树在stringbox中的id*/,obj->sb->sb.c_str(),obj->sb->sb.size());

	return PyBytes_FromStringAndSize(buff.data(),buff.size());
}

PyObject * py_rbtree_static_remove(PyObject *, PyObject *args)
{
	const char *sname;
	Py_ssize_t lname;
	if (!(PyArg_ParseTuple(args, "s#", &sname, &lname))) {
		Py_RETURN_NONE;
	}


	key_t key = strtokey(sname,lname,SHARED_TYPE_AVL);
	sharememory sm;
	if(!sm.init(key,0,0)){
		Py_RETURN_FALSE;
	}

	sharememory::remove(key);

	Py_RETURN_TRUE;
}

PyObject * py_rbtree_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	PyObject * self = type->tp_alloc(type, 0);
	if(self){
		pylyramilkObject<rbtree_object>* pobj = ((pylyramilkObject<rbtree_object>*)(self));
		rbtree_object* obj = pobj->obj = new rbtree_object;

		obj->avp = new tree_compare();
		obj->avp->sb = obj->sb = new lyramilk::data::stringbox();
		obj->rbt = new lyramilk::bintree::rbtree(obj->avp);
		return self;
	}
	PyErr_SetString(PyExc_OSError, strerror(errno));
	return NULL;
}

void py_rbtree_dealloc(PyObject* self)
{
	rbtree_object* obj = ((pylyramilkObject<rbtree_object>*)(self))->obj;

	if(obj->rbt){
		delete obj->rbt;
		obj->rbt = NULL;
	}
	if(obj->sb){
		delete obj->sb;
		obj->sb = NULL;
	}
	if(obj->avp){
		delete obj->avp;
		obj->avp = NULL;
	}

	delete obj;
	Py_TYPE(self)->tp_free((PyObject*)self);
}





PyMethodDef pyrbtreeClassMethods[] = {
	{"set", py_rbtree_set, METH_VARARGS},
	{"get", py_rbtree_get, METH_VARARGS},
	{"share", (PyCFunction)py_rbtree_share, METH_VARARGS|METH_KEYWORDS},
	{"dump", py_rbtree_dump, METH_VARARGS},
	{"remove", py_rbtree_static_remove, METH_VARARGS | METH_STATIC},
	{NULL, NULL},
};

PyTypeObject rbtree_ObjectType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"sharedmap.rbtree",				/*tp_name*/
	sizeof(pylyramilkObject<rbtree_object>),		/*tp_basicsize*/
	0, /*tp_itemsize*/
	py_rbtree_dealloc,
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
	"rbtree desc", /* tp_doc */
	0, /* tp_traverse */
	0, /* tp_clear */
	0, /* tp_richcompare */
	0, /* tp_weaklistoffset */
	0, /* tp_iter */
	0, /* tp_iternext */
	pyrbtreeClassMethods, /* tp_methods */
	0, /* tp_members */
	0, /* tp_getset */
	0, /* tp_base */
	0, /* tp_dict */
	0, /* tp_descr_get */
	0, /* tp_descr_set */
	0, /* tp_dictoffset */
	0, /* tp_init */
	0, /* tp_alloc */
	py_rbtree_new, /* tp_new */
};
