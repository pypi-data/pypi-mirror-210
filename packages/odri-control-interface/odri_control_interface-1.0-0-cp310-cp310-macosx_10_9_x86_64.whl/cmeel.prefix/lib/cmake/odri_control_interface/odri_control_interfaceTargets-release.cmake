#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "odri_control_interface::odri_control_interface" for configuration "Release"
set_property(TARGET odri_control_interface::odri_control_interface APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(odri_control_interface::odri_control_interface PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libodri_control_interface.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libodri_control_interface.dylib"
  )

list(APPEND _cmake_import_check_targets odri_control_interface::odri_control_interface )
list(APPEND _cmake_import_check_files_for_odri_control_interface::odri_control_interface "${_IMPORT_PREFIX}/lib/libodri_control_interface.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
