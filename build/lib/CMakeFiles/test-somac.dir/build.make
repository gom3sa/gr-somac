# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.10

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/andre/GnuRadio-SOMAC/gr-somac

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/andre/GnuRadio-SOMAC/gr-somac/build

# Include any dependencies generated for this target.
include lib/CMakeFiles/test-somac.dir/depend.make

# Include the progress variables for this target.
include lib/CMakeFiles/test-somac.dir/progress.make

# Include the compile flags for this target's objects.
include lib/CMakeFiles/test-somac.dir/flags.make

lib/CMakeFiles/test-somac.dir/test_somac.cc.o: lib/CMakeFiles/test-somac.dir/flags.make
lib/CMakeFiles/test-somac.dir/test_somac.cc.o: ../lib/test_somac.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/andre/GnuRadio-SOMAC/gr-somac/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object lib/CMakeFiles/test-somac.dir/test_somac.cc.o"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/test-somac.dir/test_somac.cc.o -c /home/andre/GnuRadio-SOMAC/gr-somac/lib/test_somac.cc

lib/CMakeFiles/test-somac.dir/test_somac.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/test-somac.dir/test_somac.cc.i"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/andre/GnuRadio-SOMAC/gr-somac/lib/test_somac.cc > CMakeFiles/test-somac.dir/test_somac.cc.i

lib/CMakeFiles/test-somac.dir/test_somac.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/test-somac.dir/test_somac.cc.s"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/andre/GnuRadio-SOMAC/gr-somac/lib/test_somac.cc -o CMakeFiles/test-somac.dir/test_somac.cc.s

lib/CMakeFiles/test-somac.dir/test_somac.cc.o.requires:

.PHONY : lib/CMakeFiles/test-somac.dir/test_somac.cc.o.requires

lib/CMakeFiles/test-somac.dir/test_somac.cc.o.provides: lib/CMakeFiles/test-somac.dir/test_somac.cc.o.requires
	$(MAKE) -f lib/CMakeFiles/test-somac.dir/build.make lib/CMakeFiles/test-somac.dir/test_somac.cc.o.provides.build
.PHONY : lib/CMakeFiles/test-somac.dir/test_somac.cc.o.provides

lib/CMakeFiles/test-somac.dir/test_somac.cc.o.provides.build: lib/CMakeFiles/test-somac.dir/test_somac.cc.o


lib/CMakeFiles/test-somac.dir/qa_somac.cc.o: lib/CMakeFiles/test-somac.dir/flags.make
lib/CMakeFiles/test-somac.dir/qa_somac.cc.o: ../lib/qa_somac.cc
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/andre/GnuRadio-SOMAC/gr-somac/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Building CXX object lib/CMakeFiles/test-somac.dir/qa_somac.cc.o"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/test-somac.dir/qa_somac.cc.o -c /home/andre/GnuRadio-SOMAC/gr-somac/lib/qa_somac.cc

lib/CMakeFiles/test-somac.dir/qa_somac.cc.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/test-somac.dir/qa_somac.cc.i"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/andre/GnuRadio-SOMAC/gr-somac/lib/qa_somac.cc > CMakeFiles/test-somac.dir/qa_somac.cc.i

lib/CMakeFiles/test-somac.dir/qa_somac.cc.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/test-somac.dir/qa_somac.cc.s"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/andre/GnuRadio-SOMAC/gr-somac/lib/qa_somac.cc -o CMakeFiles/test-somac.dir/qa_somac.cc.s

lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.requires:

.PHONY : lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.requires

lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.provides: lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.requires
	$(MAKE) -f lib/CMakeFiles/test-somac.dir/build.make lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.provides.build
.PHONY : lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.provides

lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.provides.build: lib/CMakeFiles/test-somac.dir/qa_somac.cc.o


# Object files for target test-somac
test__somac_OBJECTS = \
"CMakeFiles/test-somac.dir/test_somac.cc.o" \
"CMakeFiles/test-somac.dir/qa_somac.cc.o"

# External object files for target test-somac
test__somac_EXTERNAL_OBJECTS =

lib/test-somac: lib/CMakeFiles/test-somac.dir/test_somac.cc.o
lib/test-somac: lib/CMakeFiles/test-somac.dir/qa_somac.cc.o
lib/test-somac: lib/CMakeFiles/test-somac.dir/build.make
lib/test-somac: /usr/lib/x86_64-linux-gnu/libgnuradio-runtime.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libgnuradio-pmt.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/liblog4cpp.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_filesystem.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_system.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_thread.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_chrono.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_date_time.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_atomic.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libpthread.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libcppunit.so
lib/test-somac: lib/libgnuradio-somac.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libgnuradio-runtime.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libgnuradio-pmt.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/liblog4cpp.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_filesystem.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_system.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_thread.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_chrono.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_date_time.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libboost_atomic.so
lib/test-somac: /usr/lib/x86_64-linux-gnu/libpthread.so
lib/test-somac: lib/CMakeFiles/test-somac.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/andre/GnuRadio-SOMAC/gr-somac/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "Linking CXX executable test-somac"
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/test-somac.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
lib/CMakeFiles/test-somac.dir/build: lib/test-somac

.PHONY : lib/CMakeFiles/test-somac.dir/build

lib/CMakeFiles/test-somac.dir/requires: lib/CMakeFiles/test-somac.dir/test_somac.cc.o.requires
lib/CMakeFiles/test-somac.dir/requires: lib/CMakeFiles/test-somac.dir/qa_somac.cc.o.requires

.PHONY : lib/CMakeFiles/test-somac.dir/requires

lib/CMakeFiles/test-somac.dir/clean:
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/lib && $(CMAKE_COMMAND) -P CMakeFiles/test-somac.dir/cmake_clean.cmake
.PHONY : lib/CMakeFiles/test-somac.dir/clean

lib/CMakeFiles/test-somac.dir/depend:
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/andre/GnuRadio-SOMAC/gr-somac /home/andre/GnuRadio-SOMAC/gr-somac/lib /home/andre/GnuRadio-SOMAC/gr-somac/build /home/andre/GnuRadio-SOMAC/gr-somac/build/lib /home/andre/GnuRadio-SOMAC/gr-somac/build/lib/CMakeFiles/test-somac.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : lib/CMakeFiles/test-somac.dir/depend

