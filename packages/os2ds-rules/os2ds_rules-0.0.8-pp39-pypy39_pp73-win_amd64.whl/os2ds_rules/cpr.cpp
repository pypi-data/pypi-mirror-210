#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <cpr-detector.hpp>
#include <cstddef>
#include <iostream>
#include <string>

using namespace OS2DSRules::CPRDetector;

#ifdef __cplusplus
extern "C" {
#endif

static PyObject *detector_find_matches(PyObject *self, PyObject *args) {
  const char *content;
  int check_mod11 = 0;
  int examine_context = 0;

  if (!PyArg_ParseTuple(args, "s|pp", &content, &check_mod11, &examine_context))
    return NULL;

  CPRDetector detector(static_cast<bool>(check_mod11), static_cast<bool>(examine_context));
  std::string text(content);
  auto results = detector.find_matches(text);
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

static PyMethodDef DetectorMethods[] = {
    {"find_matches", detector_find_matches, METH_VARARGS,
     "Find matches in a text."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static struct PyModuleDef detectormodule = {PyModuleDef_HEAD_INIT,
                                            "detector", /* name of module */
                                            NULL, /* No documentation, yet... */
                                            -1, DetectorMethods};

PyMODINIT_FUNC PyInit_cpr_detector(void) {
  return PyModule_Create(&detectormodule);
}

#ifdef __cplusplus
}
#endif
