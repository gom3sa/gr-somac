INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SOMAC somac)

FIND_PATH(
    SOMAC_INCLUDE_DIRS
    NAMES somac/api.h
    HINTS $ENV{SOMAC_DIR}/include
        ${PC_SOMAC_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SOMAC_LIBRARIES
    NAMES gnuradio-somac
    HINTS $ENV{SOMAC_DIR}/lib
        ${PC_SOMAC_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SOMAC DEFAULT_MSG SOMAC_LIBRARIES SOMAC_INCLUDE_DIRS)
MARK_AS_ADVANCED(SOMAC_LIBRARIES SOMAC_INCLUDE_DIRS)

