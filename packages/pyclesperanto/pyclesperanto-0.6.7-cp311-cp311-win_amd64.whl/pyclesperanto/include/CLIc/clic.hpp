#ifndef __CORE_CLIC_HPP
#  define __CORE_CLIC_HPP

# define CLIC_MAJOR_VERSION 0
# define CLIC_MINOR_VERSION 6
# define CLIC_PATCH_VERSION 3
# define CLIC_VERSION "0.6.3"

#  ifndef CL_HPP_DISABLE_EXCEPTIONS
#    define CL_HPP_DISABLE_EXCEPTIONS
#  endif

#  ifndef CL_HPP_TARGET_OPENCL_VERSION
#    define CL_HPP_TARGET_OPENCL_VERSION 120
#  endif

#  ifndef CL_HPP_MINIMUM_OPENCL_VERSION
#    define CL_HPP_MINIMUM_OPENCL_VERSION 120
#  endif

#  ifndef CL_TARGET_OPENCL_VERSION
#    define CL_TARGET_OPENCL_VERSION 120
#  endif

// #include <CL/opencl.h>
#  include <CL/opencl.hpp>
#  include <string>

static const std::string
GetOpenCLErrorName(cl_int error)
{
  switch (error)
  {
    // run-time and JIT compiler errors
    case 0:
      return "CL_SUCCESS";
    case -1:
      return "CL_DEVICE_NOT_FOUND";
    case -2:
      return "CL_DEVICE_NOT_AVAILABLE";
    case -3:
      return "CL_COMPILER_NOT_AVAILABLE";
    case -4:
      return "CL_MEM_OBJECT_ALLOCATION_FAILURE";
    case -5:
      return "CL_OUT_OF_RESOURCES";
    case -6:
      return "CL_OUT_OF_HOST_MEMORY";
    case -7:
      return "CL_PROFILING_INFO_NOT_AVAILABLE";
    case -8:
      return "CL_MEM_COPY_OVERLAP";
    case -9:
      return "CL_IMAGE_FORMAT_MISMATCH";
    case -10:
      return "CL_IMAGE_FORMAT_NOT_SUPPORTED";
    case -11:
      return "CL_BUILD_PROGRAM_FAILURE";
    case -12:
      return "CL_MAP_FAILURE";
    case -13:
      return "CL_MISALIGNED_SUB_BUFFER_OFFSET";
    case -14:
      return "CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST";
    case -15:
      return "CL_COMPILE_PROGRAM_FAILURE";
    case -16:
      return "CL_LINKER_NOT_AVAILABLE";
    case -17:
      return "CL_LINK_PROGRAM_FAILURE";
    case -18:
      return "CL_DEVICE_PARTITION_FAILED";
    case -19:
      return "CL_KERNEL_ARG_INFO_NOT_AVAILABLE";
    // compile-time errors
    case -30:
      return "CL_INVALID_VALUE";
    case -31:
      return "CL_INVALID_DEVICE_TYPE";
    case -32:
      return "CL_INVALID_PLATFORM";
    case -33:
      return "CL_INVALID_DEVICE";
    case -34:
      return "CL_INVALID_CONTEXT";
    case -35:
      return "CL_INVALID_QUEUE_PROPERTIES";
    case -36:
      return "CL_INVALID_COMMAND_QUEUE";
    case -37:
      return "CL_INVALID_HOST_PTR";
    case -38:
      return "CL_INVALID_MEM_OBJECT";
    case -39:
      return "CL_INVALID_IMAGE_FORMAT_DESCRIPTOR";
    case -40:
      return "CL_INVALID_IMAGE_SIZE";
    case -41:
      return "CL_INVALID_SAMPLER";
    case -42:
      return "CL_INVALID_BINARY";
    case -43:
      return "CL_INVALID_BUILD_OPTIONS";
    case -44:
      return "CL_INVALID_PROGRAM";
    case -45:
      return "CL_INVALID_PROGRAM_EXECUTABLE";
    case -46:
      return "CL_INVALID_KERNEL_NAME";
    case -47:
      return "CL_INVALID_KERNEL_DEFINITION";
    case -48:
      return "CL_INVALID_KERNEL";
    case -49:
      return "CL_INVALID_ARG_INDEX";
    case -50:
      return "CL_INVALID_ARG_VALUE";
    case -51:
      return "CL_INVALID_ARG_SIZE";
    case -52:
      return "CL_INVALID_KERNEL_ARGS";
    case -53:
      return "CL_INVALID_WORK_DIMENSION";
    case -54:
      return "CL_INVALID_WORK_GROUP_SIZE";
    case -55:
      return "CL_INVALID_WORK_ITEM_SIZE";
    case -56:
      return "CL_INVALID_GLOBAL_OFFSET";
    case -57:
      return "CL_INVALID_EVENT_WAIT_LIST";
    case -58:
      return "CL_INVALID_EVENT";
    case -59:
      return "CL_INVALID_OPERATION";
    case -60:
      return "CL_INVALID_GL_OBJECT";
    case -61:
      return "CL_INVALID_BUFFER_SIZE";
    case -62:
      return "CL_INVALID_MIP_LEVEL";
    case -63:
      return "CL_INVALID_GLOBAL_WORK_SIZE";
    case -64:
      return "CL_INVALID_PROPERTY";
    case -65:
      return "CL_INVALID_IMAGE_DESCRIPTOR";
    case -66:
      return "CL_INVALID_COMPILER_OPTIONS";
    case -67:
      return "CL_INVALID_LINKER_OPTIONS";
    case -68:
      return "CL_INVALID_DEVICE_PARTITION_COUNT";
    // extension errors
    case -1000:
      return "CL_INVALID_GL_SHAREGROUP_REFERENCE_KHR";
    case -1001:
      return "CL_PLATFORM_NOT_FOUND_KHR";
    case -1002:
      return "CL_INVALID_D3D10_DEVICE_KHR";
    case -1003:
      return "CL_INVALID_D3D10_RESOURCE_KHR";
    case -1004:
      return "CL_D3D10_RESOURCE_ALREADY_ACQUIRED_KHR";
    case -1005:
      return "CL_D3D10_RESOURCE_NOT_ACQUIRED_KHR";
    case -1006:
      return "CL_INVALID_D3D11_DEVICE_KHR";
    case -1007:
      return "CL_INVALID_D3D11_RESOURCE_KHR";
    case -1008:
      return "CL_D3D11_RESOURCE_ALREADY_ACQUIRED_KHR";
    case -1009:
      return "CL_D3D11_RESOURCE_NOT_ACQUIRED_KHR";
    case -1010:
      return "CL_INVALID_D3D9_DEVICE_NV";
    case -1011:
      return "CL_INVALID_D3D9_RESOURCE_NV";
    case -1012:
      return "CL_D3D9_RESOURCE_ALREADY_ACQUIRED_NV";
    case -1013:
      return "CL_D3D9_RESOURCE_NOT_ACQUIRED_NV";
    case -1092:
      return "CL_EGL_RESOURCE_NOT_ACQUIRED_KHR";
    case -1093:
      return "CL_INVALID_EGL_OBJECT_KHR";
    case -1094:
      return "CL_INVALID_ACCELERATOR_INTEL";
    case -1095:
      return "CL_INVALID_ACCELERATOR_TYPE_INTEL";
    case -1096:
      return "CL_INVALID_ACCELERATOR_DESCRIPTOR_INTEL";
    case -1097:
      return "CL_ACCELERATOR_TYPE_NOT_SUPPORTED_INTEL";
    case -1098:
      return "CL_INVALID_VA_API_MEDIA_ADAPTER_INTEL";
    case -1099:
      return "CL_INVALID_VA_API_MEDIA_SURFACE_INTEL";
    case -1100:
      return "CL_VA_API_MEDIA_SURFACE_ALREADY_ACQUIRED_INTEL";
    case -1101:
      return "CL_VA_API_MEDIA_SURFACE_NOT_ACQUIRED_INTEL";
    // others
    case -9999:
      return "NVIDIA_ILLEGAL_ACCESS_TO_MEMORY";
    default:
      return "UNKNOWN_ERROR_CODE";
  }
}

// from http://www.techdarting.com/2014/01/opencl-errors.html
static const std::string
GetOpenCLErrorDescription(cl_int error)
{
  std::string result = "";
  switch (error)
  {
    case CL_SUCCESS:
      result += "Everything is good!";
      break;
    case CL_DEVICE_NOT_FOUND:
      result += "No OpenCL devices that matched given device type were found";
      break;
    case CL_DEVICE_NOT_AVAILABLE:
      result += "No OpenCL compatible device was found";
      break;
    case CL_COMPILER_NOT_AVAILABLE:
      result += "OpenCL Compiler perhaps failed to configure itself, or check your OpenCL installation";
      break;
    case CL_MEM_OBJECT_ALLOCATION_FAILURE:
      result += "Failed to allocate memory for buffer object";
      break;
    case CL_OUT_OF_RESOURCES:
      result += "failure to allocate resources required by the OpenCL implementation on the device";
      break;
    case CL_OUT_OF_HOST_MEMORY:
      result += "failure to allocate resources required by the OpenCL implementation on the host";
      break;
    case CL_PROFILING_INFO_NOT_AVAILABLE:
      result += "returned by clGetEventProfilingInfo, if the CL_QUEUE_PROFILING_ENABLE flag is not set for the "
                "command-queue and if the profiling information is currently not available";
      break;
    case CL_MEM_COPY_OVERLAP:
      result +=
        "if source and destination buffers are the same buffer object and the source and destination regions overlap";
      break;
    case CL_IMAGE_FORMAT_MISMATCH:
      result += "src and dst image do not use the same image format";
      break;
    case CL_IMAGE_FORMAT_NOT_SUPPORTED:
      result += "the image format is not supported.";
      break;
    case CL_BUILD_PROGRAM_FAILURE:
      result += "program build error for given device, Use clGetProgramBuildInfo API call to get the build log of the "
                "kernel compilation.";
      break;
    case CL_MAP_FAILURE:
      result += "failed to map the requested region into the host address space. This error does not occur for buffer "
                "objects created with CL_MEM_USE_HOST_PTR or CL_MEM_ALLOC_HOST_PTR";
      break;
    case CL_MISALIGNED_SUB_BUFFER_OFFSET:
      result += "no devices in given context associated with buffer for which the origin value is aligned to the "
                "CL_DEVICE_MEM_BASE_ADDR_ALIGN value";
      break;
    case CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST:
      result += "returned by clWaitForEvents(), execution status of any of the events in event list is a negative "
                "integer value i.e., error";
      break;
    case CL_COMPILE_PROGRAM_FAILURE:
      result += "failed to compile the program source. Error occurs if clCompileProgram does not return until the "
                "compile has completed";
      break;
    case CL_LINKER_NOT_AVAILABLE:
      result += "Linker unavailable";
      break;
    case CL_LINK_PROGRAM_FAILURE:
      result += "failed to link the compiled binaries and perhaps libraries";
      break;
    case CL_DEVICE_PARTITION_FAILED:
      result +=
        "given partition name is supported by the implementation but input device couldn't be partitioned further";
      break;
    case CL_KERNEL_ARG_INFO_NOT_AVAILABLE:
      result += "argument information is not available for the given kernel";
      break;
    case CL_INVALID_VALUE:
      result += "values passed in the flags parameter is not valid";
      break;
    case CL_INVALID_DEVICE_TYPE:
      result += "device type specified is not valid, its returned by clCreateContextFromType / clGetDeviceIDs";
      break;
    case CL_INVALID_PLATFORM:
      result += "the specified platform is not a valid platform, its returned by clGetPlatformInfo /clGetDeviceIDs / "
                "clCreateContext / clCreateContextFromType";
      break;
    case CL_INVALID_DEVICE:
      result += "device/s specified are not valid";
      break;
    case CL_INVALID_CONTEXT:
      result += "the given context is invalid OpenCL context, or the context associated with certain parameters are "
                "not the same";
      break;
    case CL_INVALID_QUEUE_PROPERTIES:
      result += "specified properties are valid but are not supported by the device, its returned by "
                "clCreateCommandQueue / clSetCommandQueueProperty";
      break;
    case CL_INVALID_COMMAND_QUEUE:
      result += "the specified command-queue is not a valid command-queue";
      break;
    case CL_INVALID_HOST_PTR:
      result += "host pointer is NULL and CL_MEM_COPY_HOST_PTR or CL_MEM_USE_HOST_PTR are set in flags or if host_ptr "
                "is not NULL but CL_MEM_COPY_HOST_PTR or CL_MEM_USE_HOST_PTR are not set in flags. returned by "
                "clCreateBuffer / clCreateImage2D / clCreateImage3D";
      break;
    case CL_INVALID_MEM_OBJECT:
      result += "the passed parameter is not a valid memory, image, or buffer object";
      break;
    case CL_INVALID_IMAGE_FORMAT_DESCRIPTOR:
      result += "image format specified is not valid or is NULL, clCreateImage2D /clCreateImage3D returns this.";
      break;
    case CL_INVALID_IMAGE_SIZE:
      result += "Its returned by create Image functions 2D/3D, if specified image width or height are outbound or 0";
      break;
    case CL_INVALID_SAMPLER:
      result += "specified sampler is an invalid sampler object";
      break;
    case CL_INVALID_BINARY:
      result += "program binary is not a valid binary for the specified device, returned by clBuildProgram / "
                "clCreateProgramWithBinary";
      break;
    case CL_INVALID_BUILD_OPTIONS:
      result += "the given build options are not valid";
      break;
    case CL_INVALID_PROGRAM:
      result += "the given program is an invalid program object, returned by clRetainProgram / clReleaseProgram / "
                "clBuildProgram / clGetProgramInfo / clGetProgramBuildInfo / clCreateKernel / clCreateKernelsInProgram";
      break;
    case CL_INVALID_PROGRAM_EXECUTABLE:
      result +=
        "if there is no successfully built executable for program returned by clCreateKernel, there is no device in "
        "program then returned by clCreateKernelsInProgram, if no successfully built program executable present for "
        "device associated with command queue then returned by clEnqueueNDRangeKernel / clEnqueueTask";
      break;
    case CL_INVALID_KERNEL_NAME:
      result += "mentioned kernel name is not found in program";
      break;
    case CL_INVALID_KERNEL_DEFINITION:
      result +=
        "arguments mismatch for the __kernel function definition and the passed ones, returned by clCreateKernel";
      break;
    case CL_INVALID_KERNEL:
      result += "specified kernel is an invalid kernel object";
      break;
    case CL_INVALID_ARG_INDEX:
      result += "clSetKernelArg if an invalid argument index is specified";
      break;
    case CL_INVALID_ARG_VALUE:
      result += "the argument value specified is NULL, returned by clSetKernelArg";
      break;
    case CL_INVALID_ARG_SIZE:
      result += "the given argument size (arg_size) do not match size of the data type for an argument, returned by "
                "clSetKernelArg";
      break;
    case CL_INVALID_KERNEL_ARGS:
      result +=
        "the kernel argument values have not been specified, returned by clEnqueueNDRangeKernel / clEnqueueTask";
      break;
    case CL_INVALID_WORK_DIMENSION:
      result += "given work dimension is an invalid value, returned by clEnqueueNDRangeKernel";
      break;
    case CL_INVALID_WORK_GROUP_SIZE:
      result += "the specified local workgroup size and number of workitems specified by global workgroup size is not "
                "evenly divisible by local workgroup size";
      break;
    case CL_INVALID_WORK_ITEM_SIZE:
      result += "no. of workitems specified in any of local work group sizes is greater than the corresponding values "
                "specified by CL_DEVICE_MAX_WORK_ITEM_SIZES in that particular dimension";
      break;
    case CL_INVALID_GLOBAL_OFFSET:
      result += "global_work_offset is not NULL. Must currently be a NULL value. In a future revision of OpenCL, "
                "global_work_offset can be used but not until OCL 1.2";
      break;
    case CL_INVALID_EVENT_WAIT_LIST:
      result += "event wait list is NULL and (no. of events in wait list > 0), or event wait list is not NULL and no. "
                "of events in wait list is 0, or specified event objects are not valid events";
      break;
    case CL_INVALID_EVENT:
      result += "invalid event objects specified";
      break;
    case CL_INVALID_GL_OBJECT:
      result += "not a valid GL buffer object";
      break;
    case CL_INVALID_BUFFER_SIZE:
      result += "the value of the parameter size is 0 or exceeds CL_DEVICE_MAX_MEM_ALLOC_SIZE for all devices "
                "specified in the parameter context, returned by clCreateBuffer";
      break;
    case CL_INVALID_GLOBAL_WORK_SIZE:
      result += "specified global work size is NULL, or any of the values specified in global work dimensions are 0 or "
                "exceeds the range given by the sizeof(size_t) for the device on which the kernel will be enqueued, "
                "returned by clEnqueueNDRangeKernel";
      break;
    case CL_INVALID_PROPERTY:
      result += "context property name in properties is not a supported property name, returned by clCreateContext";
      break;
    case CL_INVALID_IMAGE_DESCRIPTOR:
      result += "values specified in image description are invalid";
      break;
    case CL_INVALID_COMPILER_OPTIONS:
      result += "compiler options specified by options are invalid, returned by clCompileProgram";
      break;
    case CL_INVALID_LINKER_OPTIONS:
      result += "linker options specified by options are invalid, returned by clLinkProgram";
      break;
    default:
      result += "No description available";
      break;
  }
  return result;
}

// from https://github.com/Dryopes/OpenCL-Examples/blob/master/OpenCLError.cpp
static const std::string
GetOpenCLErrorInfo(cl_int error)
{
  return "Error " + GetOpenCLErrorName(error) + " (" + std::to_string(static_cast<int>(error)) +
         ")\n\tDescription: " + GetOpenCLErrorDescription(error);
}

#endif // __CLIC_HPP
