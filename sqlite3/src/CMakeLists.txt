cmake_minimum_required(VERSION 3.0)

project(sqlite3 C)

add_library(sqlite3 sqlite3.c)
target_include_directories(sqlite3 PUBLIC ${PROJECT_SOURCE_DIR})

add_executable(shell shell.c)
target_link_libraries(shell PRIVATE sqlite3)
set_property(TARGET sqlite3 PROPERTY DEBUG_POSTFIX d)
