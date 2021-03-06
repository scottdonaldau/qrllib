# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

cmake_minimum_required(VERSION 3.5)
project(qrllib)

set(CMAKE_CXX_STANDARD 14)
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -Wall -Wextra -pedantic")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS} -std=c++14 -O3")

set(CMAKE_VERBOSE_MAKEFILE FALSE)
set(CMAKE_ERROR_DEPRECATED FALSE)
set(CMAKE_WARN_DEPRECATED FALSE)

set(BUILD_TESTS ON CACHE BOOL "Enables tests")
set(BUILD_GO OFF CACHE BOOL "Enables go wrapper")
set(BUILD_PYTHON OFF CACHE BOOL "Enables python wrapper")
set(BUILD_PYTHON_LOCALDEPLOY OFF CACHE BOOL "Deploys python locally")
set(BUILD_WEBASSEMBLY OFF CACHE BOOL "Enables emscripten build")

message(STATUS "BUILD_TESTS    " ${BUILD_TESTS})
message(STATUS "GOLANG WRAPPER " ${BUILD_GO})
message(STATUS "PYTHON WRAPPER " ${BUILD_PYTHON})
message(STATUS "WEBASSEMBLY    " ${BUILD_WEBASSEMBLY})

if (BUILD_PYTHON OR BUILD_GO)
    find_package(SWIG REQUIRED)
    INCLUDE(${SWIG_USE_FILE})
    unset(SWIG_LANG_TYPE)
endif ()

include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/src/api
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/deps
)

file(GLOB LIB_QRL_INCLUDES
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt
        ${CMAKE_CURRENT_SOURCE_DIR}/src/qrl
        )

file(GLOB LIB_DILITHIUM_INCLUDES
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium
        ${CMAKE_CURRENT_SOURCE_DIR}/src/dilithium
        )

file(GLOB LIB_KYBER_INCLUDES
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber
        ${CMAKE_CURRENT_SOURCE_DIR}/src/kyber
        )

file(GLOB_RECURSE LIB_QRL_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/qrl/*.cpp")

file(GLOB_RECURSE LIB_DILITHIUM_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/dilithium/*.cpp")

file(GLOB_RECURSE LIB_KYBER_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/kyber/*.cpp")

file(GLOB TEST_QRL_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/qrl/*.cpp")

file(GLOB TEST_DILITHIUM_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/dilithium/*.cpp")

file(GLOB TEST_KYBER_SRC
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/cpp/kyber/*.cpp")

set(LIBXMSSALT_SRC
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/algsxmss_fast.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/algsxmss.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/hash.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/hash_address.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/xmss_common.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/wots.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/xmss-alt/fips202.c
        )

set(REF_DILITHIUM_SRC
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/randombytes.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/sign.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/polyvec.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/packing.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/poly.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/reduce.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/ntt.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/rounding.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/dilithium/ref/fips202.c
        )

set(REF_KYBER_SRC
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/randombytes.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/kem.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/poly.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/polyvec.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/reduce.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/cbd.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/precomp.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/ntt.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/verify.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/indcpa.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/kex.c
        ${CMAKE_CURRENT_SOURCE_DIR}/deps/kyber/ref/fips202.c
        )

# Forcing XMSS to be compiled as C++
SET_SOURCE_FILES_PROPERTIES(${LIB_QRL_SRC} PROPERTIES LANGUAGE CXX)
SET_SOURCE_FILES_PROPERTIES(${TEST_QRL_SRC} PROPERTIES LANGUAGE CXX)
SET_SOURCE_FILES_PROPERTIES(${TEST_DILITHIUM_SRC} PROPERTIES LANGUAGE CXX)
SET_SOURCE_FILES_PROPERTIES(${TEST_KYBER_SRC} PROPERTIES LANGUAGE CXX)

SET_SOURCE_FILES_PROPERTIES(${LIBXMSSALT_SRC} PROPERTIES LANGUAGE CXX)
SET_SOURCE_FILES_PROPERTIES(${REF_DILITHIUM_SRC} PROPERTIES LANGUAGE CXX)
SET_SOURCE_FILES_PROPERTIES(${REF_KYBER_SRC} PROPERTIES LANGUAGE CXX)

if (BUILD_TESTS)
    message(STATUS "GTests enabled")

    ##############################
    # Google Test
    # Based on instructions in https://github.com/google/googletest/tree/master/googletest#incorporating-into-an-existing-cmake-project
    # Download and unpack googletest at configure time
    configure_file(CMakeLists.txt.gtest.in googletest-download/CMakeLists.txt)
    execute_process(COMMAND ${CMAKE_COMMAND} -G "${CMAKE_GENERATOR}" .
            RESULT_VARIABLE result
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-download)
    if (result)
        message(FATAL_ERROR "CMake step for googletest failed: ${result}")
    endif ()
    execute_process(COMMAND ${CMAKE_COMMAND} --build .
            RESULT_VARIABLE result
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/googletest-download)
    if (result)
        message(FATAL_ERROR "Build step for googletest failed: ${result}")
    endif ()

    # Prevent overriding the parent project's compiler/linker settings on Windows
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

    # Add googletest directly to our build. This defines
    # the gtest and gtest_main targets.
    add_subdirectory(
            ${CMAKE_BINARY_DIR}/googletest-src
            ${CMAKE_BINARY_DIR}/googletest-build
    )

    # The gtest/gtest_main targets carry header search path
    # dependencies automatically when using CMake 2.8.11 or
    # later. Otherwise we have to add them here ourselves.
    if (CMAKE_VERSION VERSION_LESS 2.8.11)
        include_directories("${gtest_SOURCE_DIR}/include")
    endif ()

    ###########################
    include(CTest)
    enable_testing()

    add_executable(qrllib_test
            ${TEST_QRL_SRC}
            ${LIB_QRL_SRC}
            ${LIBXMSSALT_SRC})

    target_include_directories( qrllib_test PRIVATE
            ${LIB_QRL_INCLUDES} )
    target_link_libraries(qrllib_test gtest_main)
    add_test(gtest ${PROJECT_BINARY_DIR}/qrllib_test)

    ###########################

    add_executable(dilithium_test
            ${TEST_DILITHIUM_SRC}
            ${LIB_DILITHIUM_SRC}
            ${REF_DILITHIUM_SRC})

    target_include_directories( dilithium_test PRIVATE
            ${LIB_DILITHIUM_INCLUDES} )

    target_link_libraries(dilithium_test gtest_main)
    add_test(gtest ${PROJECT_BINARY_DIR}/dilithium_test)

    ###########################

    add_executable(kyber_test
            ${TEST_KYBER_SRC}
            ${LIB_KYBER_SRC}
            ${REF_KYBER_SRC})

    target_include_directories( kyber_test PRIVATE
            ${LIB_KYBER_INCLUDES} )

    target_link_libraries(kyber_test gtest_main)
    add_test(gtest ${PROJECT_BINARY_DIR}/kyber_test)

endif ()

## SWIG + API - Python related stuff
if (BUILD_PYTHON)
    message(STATUS "Python wrapper enabled")

    if (NOT CMAKE_LIBRARY_OUTPUT_DIRECTORY)
        set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
    endif ()

    set(language python)
    find_package(PythonLibs 3.4 REQUIRED)
    include_directories(
          ${PYTHON_INCLUDE_PATH}
    )
    set(CMAKE_SWIG_OUTDIR ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/pyqrllib)
    set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/pyqrllib)

    set(SWIG_INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src/api/qrl.i)
    set(SWIG_LANG_LIBRARIES ${PYTHON_LIBRARIES})
    set_source_files_properties(${SWIG_INTERFACE} PROPERTIES CPLUSPLUS ON)
    set_property(SOURCE ${SWIG_INTERFACE} PROPERTY SWIG_FLAGS "-includeall" "-ignoremissing")
    message(STATUS "CMAKE_SWIG_OUTDIR: " ${CMAKE_SWIG_OUTDIR})
    message(STATUS "CMAKE_LIBRARY_OUTPUT_DIRECTORY: " ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

    # Intentionally use a deprecated version to provide support for the raspberry pi
    # Basic pyqrllib - Xmss, etc.
    SWIG_ADD_MODULE(pyqrllib
            ${language}
            ${SWIG_INTERFACE}
            ${LIB_QRL_SRC}
            ${LIBXMSSALT_SRC}
            )

    SWIG_LINK_LIBRARIES(pyqrllib
            ${SWIG_LANG_LIBRARIES})

    include_directories(
            ${PYTHON_INCLUDE_PATH}
            ${LIB_QRL_INCLUDES}
    )

    add_custom_command(TARGET ${SWIG_MODULE_pyqrllib_REAL_NAME}
            POST_BUILD
            COMMENT "Moving SWIG files to output dir"
            COMMAND ${CMAKE_COMMAND} -E
            copy_if_different $<TARGET_FILE:${SWIG_MODULE_pyqrllib_REAL_NAME}>
            ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/$<TARGET_LINKER_FILE_NAME:${SWIG_MODULE_pyqrllib_REAL_NAME}>
            )

    add_custom_command(TARGET ${SWIG_MODULE_pyqrllib_REAL_NAME}
            POST_BUILD
            COMMENT ${swig_extra_generated_files}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${swig_extra_generated_files} ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/pyqrllib.py
            )

    ###################################################
    # Dilithium
    set(SWIG_INTERFACE src/api/dilithium.i)
    set(SWIG_LANG_LIBRARIES ${PYTHON_LIBRARIES})
    set_source_files_properties(${SWIG_INTERFACE} PROPERTIES CPLUSPLUS ON)
    set_property(SOURCE ${SWIG_INTERFACE} PROPERTY SWIG_FLAGS "-includeall" "-ignoremissing")
    message(STATUS "CMAKE_SWIG_OUTDIR: " ${CMAKE_SWIG_OUTDIR})
    message(STATUS "CMAKE_LIBRARY_OUTPUT_DIRECTORY: " ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

    set(SWIG_INTERFACE
            src/api/dilithium.i)

    include_directories(
            ${PYTHON_INCLUDE_PATH}
            ${LIB_DILITHIUM_INCLUDES}
    )

    SWIG_ADD_MODULE(dilithium
            ${language}
            ${SWIG_INTERFACE}
            ${LIB_DILITHIUM_SRC}
            ${REF_DILITHIUM_SRC}
            )

    SWIG_LINK_LIBRARIES(dilithium
            ${SWIG_LANG_LIBRARIES})

    add_custom_command(TARGET ${SWIG_MODULE_dilithium_REAL_NAME}
            POST_BUILD
            COMMENT "Moving SWIG files to output dir"
            COMMAND ${CMAKE_COMMAND} -E
            copy_if_different $<TARGET_FILE:${SWIG_MODULE_dilithium_REAL_NAME}>
            ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/$<TARGET_LINKER_FILE_NAME:${SWIG_MODULE_dilithium_REAL_NAME}>
            )

    add_custom_command(TARGET ${SWIG_MODULE_dilithium_REAL_NAME}
            POST_BUILD
            COMMENT ${swig_extra_generated_files}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${swig_extra_generated_files} ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/dilithium.py
            )


    # Kyber
    set(SWIG_INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src/api/kyber.i)
    set(SWIG_LANG_LIBRARIES ${PYTHON_LIBRARIES})
    set_source_files_properties(${SWIG_INTERFACE} PROPERTIES CPLUSPLUS ON)
    set_property(SOURCE ${SWIG_INTERFACE} PROPERTY SWIG_FLAGS "-includeall" "-ignoremissing")
    message(STATUS "CMAKE_SWIG_OUTDIR: " ${CMAKE_SWIG_OUTDIR})
    message(STATUS "CMAKE_LIBRARY_OUTPUT_DIRECTORY: " ${CMAKE_LIBRARY_OUTPUT_DIRECTORY})

    SWIG_ADD_MODULE(kyber
            ${language}
            ${SWIG_INTERFACE}
            ${LIB_KYBER_SRC}
            ${REF_KYBER_SRC}
            )

    SWIG_LINK_LIBRARIES(kyber
            ${SWIG_LANG_LIBRARIES})

    add_custom_command(TARGET ${SWIG_MODULE_kyber_REAL_NAME}
            POST_BUILD
            COMMENT "Moving SWIG files to output dir"
            COMMAND ${CMAKE_COMMAND} -E
            copy_if_different $<TARGET_FILE:${SWIG_MODULE_kyber_REAL_NAME}>
            ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/$<TARGET_LINKER_FILE_NAME:${SWIG_MODULE_kyber_REAL_NAME}>
            )

    add_custom_command(TARGET ${SWIG_MODULE_kyber_REAL_NAME}
            POST_BUILD
            COMMENT ${swig_extra_generated_files}
            COMMAND ${CMAKE_COMMAND} -E copy_if_different ${swig_extra_generated_files} ${CMAKE_CURRENT_SOURCE_DIR}/pyqrllib/kyber.py
            )

endif ()

# SWIG + API - Golang related stuff
if (BUILD_GO)
    set(SWIG_INTERFACE
            ${CMAKE_CURRENT_SOURCE_DIR}/src/api/qrl.i)

    message(STATUS "golang wrapper enabled")
    set(language go)
    #find_package(go 1.5 REQUIRED)
    set(SWIG_LANG_LIBRARIES ${PYTHON_LIBRARIES})
    set(CMAKE_SWIG_OUTDIR ${CMAKE_CURRENT_SOURCE_DIR}/goqrllib)
    set_source_files_properties(${SWIG_INTERFACE} PROPERTIES CPLUSPLUS ON)
    set_property(SOURCE ${SWIG_INTERFACE} PROPERTY SWIG_FLAGS "-includeall" "-ignoremissing" "-intgosize" "64")

    SWIG_ADD_MODULE(goqrllib
            ${language}
            ${SWIG_INTERFACE}
            src/api/api.cxx
            ${LIB_SRC}
            ${LIBXMSSALT_SRC}
            )

    SWIG_LINK_LIBRARIES(goqrllib
            ${SWIG_LANG_LIBRARIES}
            pyqrllib/dilithium
            pyqrllib/kyber)

    add_custom_command(TARGET ${SWIG_MODULE_goqrllib_REAL_NAME}
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E cmake_echo_color --cyan $<TARGET_FILE:${SWIG_MODULE_goqrllib_REAL_NAME}>
            COMMENT "Moving SWIG files to output dir"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:${SWIG_MODULE_goqrllib_REAL_NAME}> ${CMAKE_CURRENT_SOURCE_DIR}/goqrllib
            )
endif ()

if (BUILD_WEBASSEMBLY)
    set(JS_QRL_INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src/jswrapper/jsqrlwrapper.cpp)
    set(JS_DILITHIUM_INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src/jswrapper/jsdilwrapper.cpp)
    set(JS_KYBINTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/src/jswrapper/jskybwrapper.cpp)

    message(STATUS "webassembly enabled")
    add_library(jsqrl SHARED
            ${JS_QRL_INTERFACE}
            ${LIB_QRL_SRC}
            ${LIBXMSSALT_SRC}
            )
    target_include_directories( jsqrl PRIVATE
            ${LIB_QRL_INCLUDES} )

    add_library(jsdilithium SHARED
            ${JS_DILITHIUM_INTERFACE}
            ${LIB_KYBER_SRC}
            ${LIBDILITHIUM_SRC}
            )
    target_include_directories( jsdilithium PRIVATE
            ${LIB_DILITHIUM_INCLUDES} )

    add_library(jskyber SHARED
            ${JS_KYBER_INTERFACE}
            ${LIB_KYBER_SRC}
            ${LIBKYBER_SRC}
            )
    target_include_directories( jskyber PRIVATE
            ${LIB_KYBER_INCLUDES} )

endif ()
