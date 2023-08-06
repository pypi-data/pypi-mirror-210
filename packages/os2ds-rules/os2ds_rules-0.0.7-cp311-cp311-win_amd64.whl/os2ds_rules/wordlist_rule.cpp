#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>
#include <wordlist_rule.hpp>

using namespace OS2DSRules::WordListRule;

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  PyObject_HEAD WordListRule *rule;
} PyWordListRule;

static void PyWordListRule_dealloc(PyWordListRule *self) {
  if (self->rule)
    delete self->rule;
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *PyWordListRule_new(PyTypeObject *type, PyObject *args,
                                    PyObject *kwds) {
  PyWordListRule *self;
  self = (PyWordListRule *)type->tp_alloc(type, 0);
  if (self != NULL)
    self->rule = nullptr;
  return (PyObject *)self;
}

static int PyWordListRule_init(PyWordListRule *self, PyObject *args,
                               PyObject *kwds) {
  static char *kwlist[] = {(char *) "words", NULL};
  PyObject *words = NULL;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &words)) {
    return -1;
  }

  if (words && PyList_Check(words)) {
    std::vector<std::string_view> words_v;
    for (Py_ssize_t i = 0; i < PyList_Size(words); ++i) {
      PyObject *py_string = PyList_GetItem(words, i);

      if (PyUnicode_Check(py_string)) {
        words_v.push_back(std::string_view(
            PyBytes_AsString(PyUnicode_AsUTF8String(py_string))));
      }
    }

    self->rule = new WordListRule(words_v.begin(), words_v.end());
  }

  return 0;
}

static PyObject *PyWordListRule_find_matches(PyWordListRule *self,
                                             PyObject *args) {
  const char *content;

  if (!PyArg_ParseTuple(args, "s", &content))
    return NULL;

  std::string text(content);
  auto results = self->rule->find_matches(text);

  Py_ssize_t len = Py_ssize_t(results.size());

  PyObject *list_of_results = PyList_New(len);

  for (Py_ssize_t i = 0; i < len; ++i) {
    auto res = results[i];
    PyObject *obj = Py_BuildValue(
        "{s:s, s:i, s:i, s:d}", "match", res.match().c_str(), "start",
        res.start(), "end", res.end(), "probability", res.probability());
    PyList_SetItem(list_of_results, i, obj);
  }

  return list_of_results;
}

static PyMethodDef PyWordListRule_methods[] = {
    {"find_matches", (PyCFunction)PyWordListRule_find_matches, METH_VARARGS,
     "Find matches in a text."},
    {NULL} /* Sentinel */
};

static PyTypeObject PyWordListRuleType = {
    PyVarObject_HEAD_INIT(NULL, 0) "wordlist_rule.WordListRule", /* tp_name */
    sizeof(PyWordListRule),             /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)PyWordListRule_dealloc, /* tp_dealloc */
    0,                                  /* tp_vectorcall_offset */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_as_async */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    0,                                  /* tp_flags */
    PyDoc_STR("WordListRule bindings"), /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    PyWordListRule_methods,             /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)PyWordListRule_init,      /* tp_init */
    0,                                  /* tp_alloc */
    PyWordListRule_new,                 /* tp_new */
};

static PyModuleDef wordlistrulemodule = {
    PyModuleDef_HEAD_INIT,
    "wordlist_rule",
    NULL,
    -1,
};

PyMODINIT_FUNC PyInit_wordlist_rule(void) {
  PyObject *m;
  if (PyType_Ready(&PyWordListRuleType) < 0)
    return NULL;

  m = PyModule_Create(&wordlistrulemodule);
  if (m == NULL)
    return NULL;

  Py_INCREF(&PyWordListRuleType);
  if (PyModule_AddObject(m, "WordListRule", (PyObject *)&PyWordListRuleType) <
      0) {
    Py_DECREF(&PyWordListRuleType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}

#ifdef __cplusplus
}
#endif
