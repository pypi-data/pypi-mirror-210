import os
from setuptools import Extension, setup


CXX_FLAGS = ["/std:c++20"] if os.name == "nt" else ["-std=c++20", "-O3"]

CPR_SOURCES = (
    "src/os2ds_rules/cpr.cpp",
    "lib/cpr-detector.cpp",
    )

NAMERULE_SOURCES = (
    "src/os2ds_rules/name_rule.cpp",
    "lib/name_rule.cpp",
    )

ADDRESSRULE_SOURCES = (
    "src/os2ds_rules/address_rule.cpp",
    "lib/address_rule.cpp",
    )

WORDLISTRULE_SOURCES = (
    "src/os2ds_rules/wordlist_rule.cpp",
    "lib/wordlist_rule.cpp",
    )

cpr_detector = Extension(name="os2ds_rules.cpr_detector",
                         language="c++",
                         include_dirs=["include/"],
                         sources=[*CPR_SOURCES],
                         extra_compile_args=CXX_FLAGS)

name_rule = Extension(name="os2ds_rules.name_rule",
                      language="c++",
                      include_dirs=["include/"],
                      sources=[*NAMERULE_SOURCES],
                      extra_compile_args=CXX_FLAGS)

address_rule = Extension(name="os2ds_rules.address_rule",
                         language="c++",
                         include_dirs=["include/"],
                         sources=[*ADDRESSRULE_SOURCES],
                         extra_compile_args=CXX_FLAGS)

wordlist_rule = Extension(name="os2ds_rules.wordlist_rule",
                          language="c++",
                          include_dirs=["include/"],
                          sources=[*WORDLISTRULE_SOURCES],
                          extra_compile_args=CXX_FLAGS)

setup(
    ext_modules=[
        cpr_detector,
        name_rule,
        address_rule,
        wordlist_rule,
      ]
    )
