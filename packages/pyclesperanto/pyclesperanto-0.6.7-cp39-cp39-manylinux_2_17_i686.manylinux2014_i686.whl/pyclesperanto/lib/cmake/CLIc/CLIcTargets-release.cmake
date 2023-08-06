#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "CLIc::CLIc" for configuration "Release"
set_property(TARGET CLIc::CLIc APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(CLIc::CLIc PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libCLIc.a"
  )

list(APPEND _cmake_import_check_targets CLIc::CLIc )
list(APPEND _cmake_import_check_files_for_CLIc::CLIc "${_IMPORT_PREFIX}/lib/libCLIc.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
