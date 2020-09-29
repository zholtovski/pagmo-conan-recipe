import os
from conans import ConanFile, CMake, tools
from conans.tools import os_info, SystemPackageTool


class PagmoConan(ConanFile):
    name = "pagmo"
    version = "2.15.0"
    license = "GPL3"
    author = "Stefan Zholtovski <zholtovski@gmail.com>"
    url = "https://github.com/zholtovski/pagmo-conan-recipe.git"
    description = (
        "A C++ / Python platform to perform parallel computations "
        "of optimisation tasks (global and local) via the"
        " asynchronous generalized island model."
    )
    topics = ("parallelization", "optimization")
    homepage = "https://esa.github.io/pagmo2/index.html"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_ipopt": [True, False],
    }
    default_options = {
        "with_ipopt": False,
    }
    generators = "cmake_find_package"
    requires = [("boost/1.69.0"), ("cmake_findboost_modular/1.69.0@bincrafters/stable"), ("eigen/3.3.7"), ("nlopt/2.6.1")]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"


    def _system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ":i386"
            elif self.settings.arch == "x86_64":
                return ":amd64"
            elif self.settings.arch == "armv6" or self.settings.arch == "armv7":
                return ":armel"
            elif self.settings.arch == "armv7hf":
                return ":armhf"
            elif self.settings.arch == "armv8":
                return ":arm64"

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return ".i686"
            elif self.settings.arch == "x86_64":
                return ".x86_64"
        return ""


    def system_requirements(self):
        packages = []
        if self.options.with_ipopt:
            packages.append("coinor-libipopt-dev")

        installer = tools.SystemPackageTool()
        arch_suffix = self._system_package_architecture()
        for package in packages:
            installer.install("{}{}".format(package, arch_suffix))


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC


    def source(self):
        source_url = "https://github.com/zholtovski/pagmo2.git"
        git = tools.Git(folder=self._source_subfolder)
        git.clone(source_url, "v2.15_rename_CMake_targets")
        extracted_dir = "source"


    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.verbose = True
        cmake.definitions["PAGMO_BUILD_TESTS"] = False
        cmake.definitions["PAGMO_WITH_EIGEN3"] = True
        cmake.definitions["PAGMO_WITH_NLOPT"] = True
        # Disable optional components
        cmake.definitions["PAGMO_WITH_IPOPT"] = self.options.with_ipopt
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.options.with_ipopt:
            self.cpp_info.libs.append("ipopt")
        self.cpp_info.libs.append("pthread")
