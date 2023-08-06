#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "lager::gncpy" for configuration "Release"
set_property(TARGET lager::gncpy APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(lager::gncpy PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libgncpy.a"
  )

list(APPEND _cmake_import_check_targets lager::gncpy )
list(APPEND _cmake_import_check_files_for_lager::gncpy "${_IMPORT_PREFIX}/lib/libgncpy.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
