
import hashlib
import os
import multiprocessing
import platform
import shutil
import subprocess
import urllib.request
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
    if(toolchain == "Win64-MSVC15"):
        return "Visual Studio 15 2017 Win64"
    elif (toolchain == "Win64-MSVC14"):
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
    call(["cmake", "--build", build_dir, "--config", "Debug"])
    call(["cmake", "--build", build_dir, "--config", "RelWithDebInfo"])

    os.makedirs(os.path.join(install_dir, "include"))
    shutil.copy(os.path.join(source_dir, "sqlite3.h"), os.path.join(install_dir, "include"))
    shutil.copy(os.path.join(source_dir, "sqlite3ext.h"), os.path.join(install_dir, "include"))
    os.makedirs(os.path.join(install_dir, "lib"))
    if(os.name == "nt"):
        shutil.copy(os.path.join(build_dir, "Debug", "sqlite3d.lib"), os.path.join(install_dir, "lib"))
        shutil.copy(os.path.join(build_dir, "RelWithDebInfo", "sqlite3.lib"), os.path.join(install_dir, "lib"))
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
    call(["cmake", "--build", build_dir, "--config", "RelWithDebInfo", "-j", str(multiprocessing.cpu_count())])
    call(["cmake", "--build", build_dir, "--config", "RelWithDebInfo", "--target", "install"])

def build_sqlpp11_connector_sqlite3(toolchain):
    cwd = os.getcwd()
    source_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "src")
    build_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "build");
    install_dir = os.path.join(cwd, "sqlpp11-connector-sqlite3", "install")
    initialize_directories([build_dir, install_dir])

    cmake_generator = cmake_generator_for_toolchain(toolchain)
    call(["cmake", "-G", cmake_generator,
                   "-DHinnantDate_ROOT_DIR=" + os.path.join(cwd, "date", "src"),
                   "-DSQLPP11_INCLUDE_DIR=" + os.path.join(cwd, "sqlpp11", "install", "include"),
                   "-DSQLITE3_INCLUDE_DIR=" + os.path.join(cwd, "sqlite3", "install", "include"),
                   "-DSQLITE3_LIBRARY=" + os.path.join(cwd, "sqlite3", "install", "lib", ("sqlite3.lib" if toolchain.startswith("Win64-") else "libsqlite3.a")),
                   "-DCMAKE_INSTALL_PREFIX=" + install_dir, source_dir],
         cwd=build_dir)
    call(["cmake", "--build", build_dir, "--config", "Debug", "--target", "sqlpp11-connector-sqlite3", "-j", str(multiprocessing.cpu_count())])
    call(["cmake", "--build", build_dir, "--config", "RelWithDebInfo", "--target", "sqlpp11-connector-sqlite3", "-j", str(multiprocessing.cpu_count())])
    call(["cmake", "--build", build_dir, "--config", "RelWithDebInfo", "--target", "install"])

def build_rapidjson(toolchain):
    cwd = os.getcwd()
    source_dir = os.path.join(cwd, "rapidjson", "src")
    build_dir = os.path.join(cwd, "rapidjson", "build");
    install_dir = os.path.join(cwd, "rapidjson", "install")
    initialize_directories([build_dir, install_dir])

    cmake_generator = cmake_generator_for_toolchain(toolchain)
    call(["cmake", "-G", cmake_generator,
                   "-DBUILD_TESTING=OFF",
                   "-DRAPIDJSON_BUILD_ASAN=OFF",
                   "-DRAPIDJSON_BUILD_CXX11=ON",
                   "-DRAPIDJSON_BUILD_DOC=OFF",
                   "-DRAPIDJSON_BUILD_EXAMPLES=OFF",
                   "-DRAPIDJSON_BUILD_TESTS=OFF",
                   "-DRAPIDJSON_BUILD_THIRDPARTY_GTEST=OFF",
                   "-DRAPIDJSON_BUILD_UBSAN=OFF",
                   "-DRAPIDJSON_HAS_STDSTRING=ON",
                   "-DCMAKE_INSTALL_PREFIX=" + install_dir, source_dir],
         cwd=build_dir)
    call(["cmake", "--build", build_dir, "--config", "Release", "-j", str(multiprocessing.cpu_count())])
    call(["cmake", "--build", build_dir, "--config", "Release", "--target", "install"])

def download_vswhere():
    cwd = os.getcwd()
    source_url = "https://github.com/Microsoft/vswhere/releases/download/2.2.13%2Bg0952074227/vswhere.exe"
    source_md5 = "39f56924d03d2e18bbd0c8f0f4de3b4b"
    target_path = os.path.join(cwd, "vswhere", "vswhere.exe")
    if(not os.path.isfile(target_path)):
        print("Downloading vswhere...")
        urllib.request.urlretrieve(source_url, target_path)
    hash = hashlib.md5(open(target_path, 'rb').read()).hexdigest()
    if(hash != source_md5):
        raise RuntimeError("Hash mismatch on downloaded vswhere (expected: " + source_md5 + ", got: " + hash)

if os.name == "nt":
    download_vswhere()
    toolchain = "Win64-MSVC15"
elif os.name == "posix":
    if platform.system() == "Darwin":
        toolchain = "MacOS-Make"
    elif platform.system() == "Linux":
        toolchain = "Linux-Make"


print("*******************************************************************************")
print("***  SQLite3                                                                ***")
print("*******************************************************************************")
build_sqlite3(toolchain)
print("*******************************************************************************")
print("***  sqlpp11                                                                ***")
print("*******************************************************************************")
build_sqlpp11(toolchain)
print("*******************************************************************************")
print("***  sqlpp11-sqlite-connector                                               ***")
print("*******************************************************************************")
build_sqlpp11_connector_sqlite3(toolchain)
print("*******************************************************************************")
print("***  RapidJSON                                                              ***")
print("*******************************************************************************")
build_rapidjson(toolchain)
