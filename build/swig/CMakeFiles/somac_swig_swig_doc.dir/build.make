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

# Utility rule file for somac_swig_swig_doc.

# Include the progress variables for this target.
include swig/CMakeFiles/somac_swig_swig_doc.dir/progress.make

swig/CMakeFiles/somac_swig_swig_doc: swig/somac_swig_doc.i


somac_swig_swig_doc: swig/CMakeFiles/somac_swig_swig_doc
somac_swig_swig_doc: swig/CMakeFiles/somac_swig_swig_doc.dir/build.make

.PHONY : somac_swig_swig_doc

# Rule to build all files generated by this target.
swig/CMakeFiles/somac_swig_swig_doc.dir/build: somac_swig_swig_doc

.PHONY : swig/CMakeFiles/somac_swig_swig_doc.dir/build

swig/CMakeFiles/somac_swig_swig_doc.dir/clean:
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build/swig && $(CMAKE_COMMAND) -P CMakeFiles/somac_swig_swig_doc.dir/cmake_clean.cmake
.PHONY : swig/CMakeFiles/somac_swig_swig_doc.dir/clean

swig/CMakeFiles/somac_swig_swig_doc.dir/depend:
	cd /home/andre/GnuRadio-SOMAC/gr-somac/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/andre/GnuRadio-SOMAC/gr-somac /home/andre/GnuRadio-SOMAC/gr-somac/swig /home/andre/GnuRadio-SOMAC/gr-somac/build /home/andre/GnuRadio-SOMAC/gr-somac/build/swig /home/andre/GnuRadio-SOMAC/gr-somac/build/swig/CMakeFiles/somac_swig_swig_doc.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : swig/CMakeFiles/somac_swig_swig_doc.dir/depend

