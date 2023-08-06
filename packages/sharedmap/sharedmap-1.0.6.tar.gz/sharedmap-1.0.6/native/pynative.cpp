#include "pynative.h"
#include "pytree.h"

static PyMethodDef sharedmapModuleMethods[] = {
	{NULL, NULL},
};

static bool pydefineobject(PyObject* m)
{
	if(!m){
		return false;
	}
	if(PyType_Ready(&rbtree_ObjectType) < 0){
		printf("sharedmap.rbtree not ready\n");
	}else{
		Py_INCREF(&rbtree_ObjectType);
		PyModule_AddObject(m, "rbtree", (PyObject *)&rbtree_ObjectType);
	}
	if(PyType_Ready(&shareabledict_ObjectType) < 0){
		printf("sharedmap.sharedmap not ready\n");
	}else{
		Py_INCREF(&shareabledict_ObjectType);
		PyModule_AddObject(m, "sharedmap", (PyObject *)&shareabledict_ObjectType);
	}

	if(PyType_Ready(&shareablebitmap_ObjectType) < 0){
		printf("sharedmap.sharedbitmap not ready\n");
	}else{
		Py_INCREF(&shareablebitmap_ObjectType);
		PyModule_AddObject(m, "sharedbitmap", (PyObject *)&shareablebitmap_ObjectType);
	}
	return true;
}




#if PY_MAJOR_VERSION == 3

	static int sharedmap_extension_traverse(PyObject *m, visitproc visit, void *arg) {
		return 0;
	}

	static int sharedmap_extension_clear(PyObject *m) {
		return 0;
	}

	/*
	#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
	struct module_state {
		PyObject *error;
	};
	*/
	static struct PyModuleDef sharedmapModuleDefine = {
		PyModuleDef_HEAD_INIT,//默认
		"sharedmap",//模块名
		NULL,
		-1,
		sharedmapModuleMethods, //上面的数组
		NULL,
		sharedmap_extension_traverse,
		sharedmap_extension_clear,
	};


	PyMODINIT_FUNC PyInit_sharedmap()
	{
		PyObject* m = PyModule_Create(&sharedmapModuleDefine);
		if(pydefineobject(m)){
			return m;
		}
		return NULL;
	}
#endif










#if PY_MAJOR_VERSION == 2
	__attribute__((visibility ("default"))) extern "C" void initsharedmap(){
		PyObject* m = Py_InitModule("sharedmap", sharedmapModuleMethods);
		pydefineobject(m);
	}
#endif
