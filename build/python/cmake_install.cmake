# Install script for directory: /home/andre/GnuRadio-SOMAC/gr-somac/python

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/somac" TYPE FILE FILES
    "/home/andre/GnuRadio-SOMAC/gr-somac/python/__init__.py"
    "/home/andre/GnuRadio-SOMAC/gr-somac/python/decision.py"
    "/home/andre/GnuRadio-SOMAC/gr-somac/python/QLearningEGreedy.py"
    "/home/andre/GnuRadio-SOMAC/gr-somac/python/QLearningBoltzmann.py"
    "/home/andre/GnuRadio-SOMAC/gr-somac/python/FSMAC.py"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python2.7/dist-packages/somac" TYPE FILE FILES
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/__init__.pyc"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/decision.pyc"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/QLearningEGreedy.pyc"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/QLearningBoltzmann.pyc"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/FSMAC.pyc"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/__init__.pyo"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/decision.pyo"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/QLearningEGreedy.pyo"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/QLearningBoltzmann.pyo"
    "/home/andre/GnuRadio-SOMAC/gr-somac/build/python/FSMAC.pyo"
    )
endif()

