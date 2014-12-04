# - Find ArrayFire

# Defines the following variables:
# ArrayFire_INCLUDE_DIRS    - Location of ArrayFire's include directory.
# ArrayFire_LIBRARIES       - Location of ArrayFire's libraries. This will default
#                             to a GPU backend if one is found.
# ArrayFire_FOUND           - True if ArrayFire has been located
#
# You may provide a hint to where ArrayFire's root directory may be located
# by setting ArrayFire_ROOT_DIR before calling this script.
#
# ----------------------------------------------------------------------------
#
# ArrayFire_CPU_FOUND        - True of the ArrayFire CPU library has been found.
# ArrayFire_CPU_LIBRARIES    - Location of ArrayFire's CPU library, if found
# ArrayFire_CUDA_FOUND       - True of the ArrayFire CUDA library has been found.
# ArrayFire_CUDA_LIBRARIES   - Location of ArrayFire's CUDA library, if found
# ArrayFire_OpenCL_FOUND     - True of the ArrayFire OpenCL library has been found.
# ArrayFire_OpenCL_LIBRARIES - Location of ArrayFire's OpenCL library, if found
#
# Variables used by this module, they can change the default behaviour and
# need to be set before calling find_package:
#
#=============================================================================
# Copyright (c) 2014, ArrayFire
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# 
# * Neither the name of the ArrayFire nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#=============================================================================

IF(ArrayFire_INCLUDE_DIRS)
  # Already in cache, be silent
  set (ArrayFire_FIND_QUIETLY TRUE)
ENDIF()

# Find the ArrayFire install directories and headers:
FIND_PATH(ArrayFire_ROOT_DIR
    NAMES include/arrayfire.h
    HINTS "${CMAKE_INSTALL_PREFIX}" "${ArrayFire_ROOT_DIR}" "${ArrayFire_ROOT_DIR}/lib64"
    DOC "ArrayFire root directory.")
    
FIND_PATH(ArrayFire_INCLUDE_DIRS
    NAMES arrayfire.h
    HINTS "${ArrayFire_ROOT_DIR}/include"
    DOC "ArrayFire Include directory")

# Find all libraries used by all backends first

# Find all libraries required for the CPU backend
FIND_LIBRARY(ArrayFire_CPU_LIBRARY
    NAMES afcpu
    HINTS "${ArrayFire_ROOT_DIR}/lib")

IF(ArrayFire_CPU_LIBRARY)
    SET(ArrayFire_CPU_LIBRARIES ${ArrayFire_CPU_LIBRARY} 
        CACHE INTERNAL "All libraries required for ArrayFire's CPU implementation")
    SET(ArrayFire_CPU_FOUND TRUE CACHE BOOL "Whether or not ArrayFire's CPU library has been located.")
    SET(_ArrayFire_LIBRARIES ${ArrayFire_CPU_LIBRARIES})
ENDIF()

# Find all libraries required for the OpenCL backend
FIND_LIBRARY(ArrayFire_OPENCL_LIBRARY
    NAMES afopencl
    HINTS "${ArrayFire_ROOT_DIR}/lib")
        
IF(ArrayFire_OPENCL_LIBRARY)    
    SET(ArrayFire_OPENCL_LIBRARIES ${ArrayFire_OPENCL_LIBRARY}  
        CACHE INTERNAL "All libraries for ArrayFire's OpenCL implementation.")
    
    SET(ArrayFire_OPENCL_FOUND TRUE CACHE BOOL "Whether the ArrayFire's OpenCL library has been located.")
    SET(_ArrayFire_LIBRARIES ${ArrayFire_OPENCL_LIBRARIES})
ENDIF()

# Find all libraries required for the CUDA backend
FIND_LIBRARY(ArrayFire_CUDA_LIBRARY
    NAMES afcuda
    HINTS "${ArrayFire_ROOT_DIR}/lib")
        
IF(ArrayFire_CUDA_LIBRARY)
    SET(ArrayFire_CUDA_LIBRARIES ${ArrayFire_CUDA_LIBRARY} 
        CACHE INTERNAL "All libraries required for ArrayFire's CUDA implementation")
        
    SET(ArrayFire_CUDA_FOUND TRUE CACHE BOOL "Whether the ArrayFire's CUDA library has been located.")
    SET(_ArrayFire_LIBRARIES ${ArrayFire_CUDA_LIBRARIES})
ENDIF()

SET(ArrayFire_LIBRARIES ${_ArrayFire_LIBRARIES})

# handle the QUIETLY and REQUIRED arguments and set ArrayFire_FOUND to TRUE if
# all listed variables are TRUE
INCLUDE (FindPackageHandleStandardArgs)

FIND_PACKAGE_HANDLE_STANDARD_ARGS(ArrayFire DEFAULT_MSG ArrayFire_LIBRARIES ArrayFire_INCLUDE_DIRS)
MARK_AS_ADVANCED(ArrayFire_LIBRARIES ArrayFire_INCLUDE_DIRS ArrayFire_CPU_LIBRARY ArrayFire_CUDA_LIBRARY ArrayFire_OPENCL_LIBRARY)
