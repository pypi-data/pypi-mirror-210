#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cstddef>
#include <name_rule.hpp>
#include <string>

using namespace OS2DSRules::NameRule;

#ifdef __cplusplus
extern "C" {
#endif

static PyObject *name_rule_find_matches(PyObject *self, PyObject *args) {
  const char *content;
  int expansive = 0;

  if (!PyArg_ParseTuple(args, "s|p", &content, &expansive))
    return NULL;

  NameRule rule(static_cast<bool>(expansive));
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

static PyMethodDef NameRuleMethods[] = {
    {"find_matches", name_rule_find_matches, METH_VARARGS,
     "Find matches in a text."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef namerulemodule = {PyModuleDef_HEAD_INIT,
                                            "name_rule", /* name of module */
                                            NULL, /* No documentation, yet... */
                                            -1, NameRuleMethods};

PyMODINIT_FUNC PyInit_name_rule(void) {
  return PyModule_Create(&namerulemodule);
}

#ifdef __cplusplus
}
#endif
