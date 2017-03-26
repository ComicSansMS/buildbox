
import os
import platform
import shutil
import subprocess
import versions

def call(args, cwd=os.getcwd()):
    p = subprocess.Popen(args, cwd=cwd)
    if p.wait() != 0:
        raise RuntimeError("Error in subprocess.")

def initialize_directories(dirs):
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

def cmake_generator_for_toolchain(toolchain):
    if(toolchain == "Win64-MSVC14"):
        return "Visual Studio 14 2015 Win64"
    elif((toolchain == "MacOS-Make") or (toolchain == "Linux-Make")):
        return "Unix Makefiles"
    raise RuntimeError("Unsupported toolchain: " + toolchain)


def build_sqlite3(toolchain):
    cwd = os.getcwd()
    source_dir = os.path.join(cwd, "sqlite3", "src")
    build_dir = os.path.join(cwd, "sqlite3", "build");
    install_dir = os.path.join(cwd, "sqlite3", "install")
    initialize_directories([build_dir, install_dir])

    cmake_generator = cmake_generator_for_toolchain(toolchain)
    call(["cmake", "-G", cmake_generator, source_dir], cwd=build_dir)
    call(["cmake", "--build", build_dir, "--config", "Release"])

    os.makedirs(os.path.join(install_dir, "include"))
    shutil.copy(os.path.join(source_dir, "sqlite3.h"), os.path.join(install_dir, "include"))
    shutil.copy(os.path.join(source_dir, "sqlite3ext.h"), os.path.join(install_dir, "include"))
    os.makedirs(os.path.join(install_dir, "lib"))
    if(os.name == "nt"):
        shutil.copy(os.path.join(build_dir, "Release", "sqlite3.lib"), os.path.join(install_dir, "lib"))
    else:
        shutil.copy(os.path.join(build_dir, "libsqlite3.a"), os.path.join(install_dir, "lib"))

def build_sqlpp11(toolchain):
    cwd = os.getcwd()
    source_dir = os.path.join(cwd, "sqlpp11", "src")
    build_dir = os.path.join(cwd, "sqlpp11", "build");
    install_dir = os.path.join(cwd, "sqlpp11", "install")
    initialize_directories([build_dir, install_dir])

    cmake_generator = cmake_generator_for_toolchain(toolchain)
    call(["cmake", "-G", cmake_generator,
                   "-DHinnantDate_ROOT_DIR=" + os.path.join(cwd, "date", "src"),
                   "-DENABLE_TESTS=OFF",
                   "-DCMAKE_INSTALL_PREFIX=" + install_dir, source_dir],
         cwd=build_dir)
    call(["cmake", "--build", build_dir, "--config", "Release"])
    call(["cmake", "--build", build_dir, "--config", "Release", "--target", "install"])

def build_sqlpp11_connector_sqlite3(toolchain):
    cwd = os.getcwd()
    source_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "src")
    build_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "build");
    install_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "install")
    initialize_directories([build_dir, install_dir])

    cmake_generator = cmake_generator_for_toolchain(toolchain)
    call(["cmake", "-G", cmake_generator,
                   "-DDATE_INCLUDE_DIR=" + os.path.join(cwd, "date", "src"),
                   "-DSQLPP11_INCLUDE_DIR=" + os.path.join(cwd, "sqlpp11", "install", "include"),
                   "-DSQLITE3_INCLUDE_DIR=" + os.path.join(cwd, "sqlite3", "install", "include"),
                   "-DSQLITE3_LIBRARY=" + os.path.join(cwd, "sqlite3", "install", "lib", ("sqlite3.lib" if toolchain == "Win64-MSVC14" else "libsqlite3.a")),
                   "-DCMAKE_INSTALL_PREFIX=" + install_dir, source_dir],
         cwd=build_dir)
    call(["cmake", "--build", build_dir, "--config", "Debug", "--target", "sqlpp11-connector-sqlite3"])
    call(["cmake", "--build", build_dir, "--config", "Release", "--target", "sqlpp11-connector-sqlite3"])
    call(["cmake", "--build", build_dir, "--config", "Release", "--target", "install"])



if os.name == "nt":
    toolchain = "Win64-MSVC14"
elif os.name == "posix":
    if platform.system() == "Darwin":
        toolchain = "MacOS-Make"
    elif platform.system() == "Linux":
        toolchain = "Linux-Make"

build_sqlite3(toolchain)
build_sqlpp11(toolchain)
build_sqlpp11_connector_sqlite3(toolchain)