#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <address_rule.hpp>
#include <cstddef>
#include <string>

using namespace OS2DSRules::AddressRule;

#ifdef __cplusplus
extern "C" {
#endif

static PyObject *address_rule_find_matches(PyObject *self, PyObject *args) {
  const char *content;

  if (!PyArg_ParseTuple(args, "s", &content))
    return NULL;

  AddressRule rule;
  std::string text(content);
  auto results = rule.find_matches(text);
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

static PyMethodDef AddressRuleMethods[] = {
    {"find_matches", address_rule_find_matches, METH_VARARGS,
     "Find matches in a text."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef addressrulemodule = {
    PyModuleDef_HEAD_INIT, "address_rule", /* name of module */
    NULL,                                  /* No documentation, yet... */
    -1, AddressRuleMethods};

PyMODINIT_FUNC PyInit_address_rule(void) {
  return PyModule_Create(&addressrulemodule);
}

#ifdef __cplusplus
}
#endif
