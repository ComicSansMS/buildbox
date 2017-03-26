import os
import subprocess

env = {}
cwd = os.getcwd();
env["CATCH_ROOT"] = os.path.join(cwd, "catch", "src")
env["DATE_ROOT"] = os.path.join(cwd, "date", "src")
env["RAPIDJSON_ROOT"] = os.path.join(cwd, "rapidjson", "install")
env["SQLITE3_ROOT"] = os.path.join(cwd, "sqlite3", "install")
env["SQLPP11_ROOT"] = os.path.join(cwd, "sqlpp11", "install")
env["SQLPP11_CONNECTOR_SQLITE3_SOURCE_ROOT"] = os.path.join(cwd, "sqlpp11-connector-sqlite3", "src")

print("The build box environment is:")

for v, d in env.items():
    print(v + "=" + d)
