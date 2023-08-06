# `os2ds-rules`: Next-generation, high-performance rule system for OS2datascanner

`os2ds-rules` is the next-generation rules system for use in [OS2datascanner](https://os2datascanner.dk/en/)
by [Magenta ApS](https://www.magenta.dk/), which aimes to deliver high-performance
with regards to processing speed and detection accuracy.

The project consists of several components: 

- A shared-library backend written in modern `C++20`.
- A Python C/C++ extension that exposes functionality from the backend to `python`.
- A `python` library that provides a safe, easy-to-use interface to the aforementioned extension.

WARNING: This is currently in a very early stage of development and frequently undergoes
substantial changes, so it is not ready for prime time, yet.

## Getting Started

You can install either or both of the `C++` library or the `python` extension.

### C++ backend library: `libos2dsrules`

For the `C++` library you need a few different things:

- A compiler that supports `C++20`. We recommend using either `g++` (GCC) or `clang` (LLVM).
- `cmake>=3.20`: Primary (meta) build system.
- `ninja`: Cross-platform backend for cmake.
- `gtest` (Google Test): For building and running the test suite.

For development, you additionally want:

- `cppcheck` or `clang-analyzer`: For static code analysis.
- `clang-format`: For formatting C++ code. We adhere to the LLVM style guide.
- `clang-tidy`: For C++ code linting.
- `gdb` or `lldb`: A suitable debugger.

To make a debug build on `linux`, run the following:

```sh
# Make a build directory 
cmake . --preset linux-debug
cmake --build --preset linux-build-debug
```

This will build the shared library `libos2dsrules.so` and the test suite `testsuite`.

To install the library, run the following from the build directory:

```sh
sudo cmake --install build_cmake/debug
```

By default, this will install headers into `/usr/include` and shared objects to
`/usr/lib`. 

To run the test suite:

```sh
ctest --preset linux-test-debug
```

Currently, this has only been tested on `linux`.
It remains to be tested on `windows` and `macos`.

#### Using CMake preset workflows

There are four preconfigured workflows that has been automated with cmake:

- `linux-debug-workflow`: Configures, Builds and Tests the debug version of the library for `linux`.
- `linux-release-workflow`: Configures, Builds and Packages the release version of the library for `linux`.
- `windows-debug-workflow`: Configures, Builds and Tests the debug version of the library for `windows`.
- `windows-release-workflow`: Configures, Builds and Packages the release version of the library for `windows`.

### The Python extension: `os2ds-rules`

You need the following:

- A compiler that supports `C++20`. We recommend using either `g++` (GCC) or `clang` (LLVM).
- The CPython development headers and libraries.
- `setuptools`: For building the extension.
- `pytest`: For python tests.
- `pytest-benchmark`: For python benchmarks.

NOTE: Depending on what OS you use and how `CPython` was installed on your system,
the development headers and libraries may or may not be installed.

The development headers and libraries can be installed using a package manager on the 
following systems:

- `ubuntu`/`debian`: `sudo apt install python3-dev`
- `fedora`: `sudo dnf install python3-devel`

To build the extension:

```sh
# From the project root.
python3 -m setup build
```

To install the extension locally:

```sh
# From the project root.
# You may want to use the `-e` option during development.
python3 -m pip install .
```

Uninstalling is as easy as running:

```sh
pip uninstall os2ds-rules
```

### Running the benchmark

After having installed the extension as described above, run the benchmarks with:

```sh
python3 -m pytest --benchmark-only test/benchmarks/
```

Currently, you need to build and install the extension before running the benchmark
until this gets fixed.

## Python Interpreter support

The Python3 extension uses the `CPython` C-API, which is supported by
`CPython` as standard.

We aim to support the `PyPy` interpreter as well.

## Usage Examples

### In Python

Let us scan a python `str` for occurances for CPR-Numbers:

```python
from os2ds_rules import CPRDetector


detector = CPRDetector()

matches = detector.find_matches('This is a fake, but valid CPR-Number: 1111111118')

for m in matches:
	print(m)
```

### In C++

Consider this simple file, `test.cpp`:

```cpp
#include <os2dsrules.hpp>
#include <name_rule.hpp>

#include <iostream>
#include <string>

using namespace OS2DSRules::NameRule;

int main(void) {
    NameRule rule;
    std::string s = "This is my friend, John.";
    auto results = rule.find_matches(s);

    std::cout << "Found matches: \n";
    for (auto m : results) {
        std::cout << m.match() << '\n';
    }

    return 0;
}
```

To compile, using `clang`, simply run:

```sh
clang++ -los2dsrules -std=c++20 test.cpp -o test 
```

This will produce an executable `test` in the current working directory.

Running it:

```sh
$ ./test
Found matches:
John
```
