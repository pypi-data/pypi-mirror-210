#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <windows.h>
#include <objbase.h>
#include <dshow.h>
#include <tchar.h>
#include <uuids.h>
#include <WinError.h>
#include <OleAuto.h>

#define TOF_VID L"2560"
#define TOF_PID L"C0D6"
#define	DB_LOW						0x01

namespace py = pybind11;

int32_t indexList = -1;

typedef struct
{
    char deviceName[50];
    char vid[5];
    char pid[5];
    char devicePath[500];
    char serialNo[50];
}DeviceInfo;

bool getDeviceCount(uint32_t *gDeviceCount) ;
bool getDeviceListInfo(uint32_t deviceCount,DeviceInfo* gDevicesList);
bool getDeviceInfo(uint32_t deviceIndex,DeviceInfo* gDevice) ;

	void DebugMessage(BOOL bEnable, LPTSTR szFormat, ...)
	{
		if (bEnable)
		{
			static TCHAR szBuffer[2048] = { 0 };
			const size_t NUMCHARS = sizeof(szBuffer) / sizeof(szBuffer[0]);
			const int LASTCHAR = NUMCHARS - 1;

			// Format the input string
			va_list pArgs;
			va_start(pArgs, szFormat);
			// Use a bounded buffer size to prevent buffer overruns.  Limit count to
			// character size minus one to allow for a NULL terminating character.
			HRESULT hr = StringCchVPrintf(szBuffer, NUMCHARS - 1, szFormat, pArgs);
			va_end(pArgs);

			// Ensure that the formatted string is NULL-terminated
			szBuffer[LASTCHAR] = TEXT('\0');

			OutputDebugString(szBuffer);
		}
	}
	 
	bool isValidIndex(uint32_t deviceIndex) 
	{
	  uint32_t device_count;
	  
	  if (getDeviceCount(&device_count)==false)
	  {
		 return false;
	  }
	  if (deviceIndex > device_count || deviceIndex < 0)
	  {
		  return false;
	  }
	  
	  return true;
	}
	
	void getDevNodeNumber(uint32_t *nodeNo) 
	{
	  uint32_t auto_index = 0, count = 0;
	  while (auto_index < 16) {
		  if ((1 << auto_index) & indexList) {
			  if (count == *nodeNo) {
				  *nodeNo = auto_index;
				  break;
			  }
			  count++;
		  }
		  auto_index++;
	  }
  }

	bool isValidNode(std::string deviceNodeName) 
	{
		return true;
	}
  
	void deInitialize()
	{
	  indexList = -1;
	}
  
	bool initialize() 
	{
		try
		{
	  		printf("initialize is statred\n");
	  		CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
	  		TCHAR devicePath[MAX_PATH] = _T("");
	  		TCHAR extrctd_vid[10] = _T("");
	  		TCHAR extrctd_pid[10] = _T("");
	  		TCHAR* vid_substr;
	  		TCHAR* pid_substr;
	  		HRESULT hr;
	  		ULONG cFetched;
	  		IMoniker* pM;
	  		ICreateDevEnum* pCreateDevEnum = 0;
	  		IEnumMoniker* pEm = 0;
	  		UINT8 Count = 0;
	  		//Modified by Abishek on 10/04/2023 
	  		//Reason : To clear the indexList even when no video streaming device is present
	  		indexList = 0;
	  
	  		hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER,
		  	IID_ICreateDevEnum, (void**)&pCreateDevEnum);
	  		if (hr != NO_ERROR)
	  		{
		 		SetLastError(0);
		  		printf("NotInitialized Error\n");
		  		return false;
		  		//return DEPTHVISTAError::setErrno(Result::NotInitialized);
	  		}

			hr = pCreateDevEnum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &pEm, 0);
			if (hr != NOERROR)
			{
				printf("NotInitialized Error\n");
				return false;
			}
			pEm->Reset();
			printf("Before While loop\n");
			while (hr = pEm->Next(1, &pM, &cFetched), hr == S_OK)
			{
				printf("Entered a While loop\n");
				IPropertyBag* pBag = 0;
				hr = pM->BindToStorage(0, 0, IID_IPropertyBag, (void**)&pBag);

				if (SUCCEEDED(hr))
				{
					printf(" While loop hr successed\n");
					VARIANT var;
					var.vt = VT_BSTR;
					hr = pBag->Read(L"DevicePath", &var, 0);
					if (hr == S_OK)
					{
						printf(" While loop hr S_OK successed\n");
						StringCbPrintf(devicePath, MAX_PATH, L"%s", var.bstrVal);

						if (devicePath != NULL)
						{
							printf(" While loop hr devicePath != NULL successed\n");
							vid_substr = wcsstr(wcsupr(devicePath), TEXT("VID_"));

							if (vid_substr != NULL)
							{
								wcsncpy_s(extrctd_vid, vid_substr + 4, 4);
								extrctd_vid[5] = '\0';
								printf(" While loop hr wcsncpy_s(extrctd_vid, vid_substr + 4, 4) successed\n");
							}

							pid_substr = wcsstr(wcsupr(devicePath), TEXT("PID_"));

							if (pid_substr != NULL)
							{
								wcsncpy_s(extrctd_pid, pid_substr + 4, 4);
								extrctd_pid[5] = '\0';
								printf("While loop - pid_substr != NULL - wcsncpy_s(extrctd_pid, pid_substr + 4, 4);\n");
							}
						
							if ((wcscmp(wcsupr(extrctd_vid), TOF_VID) == 0) && (wcscmp(wcsupr(extrctd_pid), TOF_PID) == 0))
							{
								indexList |= (1 << Count);
								Count++;
					        }
						}
						SysFreeString(var.bstrVal);
					}
					pM->AddRef();
				}
				else
				{
					pEm->Release();
				}
				pM->Release();
			}
			pEm->Release();
			return true;
		}
  	catch (...)
  	{
	  printf("NotInitialized Error");
	  return false;
  	}
	return true;
  }
  
	bool getDeviceCount1(pybind11::object& gDeviceCount) 
	{
	  initialize();
	  int list = indexList;
	  gDeviceCount.attr("value") = 0;
	  if (!indexList) 
	  {
		 printf("Device is not connected");
		 return false;
	  }
	  while (list)
	  {
		  printf("Before list =  %d\n",list);
		  list &= (list - 1);
		  printf("After list =  %d\n",list);
		  gDeviceCount.attr("value") = pybind11::int_(gDeviceCount.attr("value").cast<int>() + 1);
	  }
	  return true;
  }
  
	bool getDeviceCount(uint32_t* gDeviceCount) 
	{
	  initialize();
	  int list = indexList;
	  *gDeviceCount = 0;
	  if (!indexList) 
	  {
		 printf("Device is not connected");
		 return false;
	  }
	  while (list)
	  {
		  printf("Before list =  %d\n",list);
		  list &= (list - 1);
		  printf("After list =  %d\n",list);
		  printf("Before gdevice list =  %d\n",*gDeviceCount);
		  *gDeviceCount += 1;
		  printf("After gdevice list =  %d\n",*gDeviceCount);
	  }
	  return true;
  }
  
	bool getDeviceListInfo(uint32_t deviceCount,DeviceInfo* gDevicesList) 
	{
	  for (uint32_t index = 0; index < deviceCount; index++) 
	  {
		  DebugMessage(DB_LOW, L"Device index is : %d\n", index);
			if (getDeviceInfo(index, (gDevicesList + index))== false) 
			{
			  printf("other issue");
			  return false;
			}
		  DebugMessage(DB_LOW, L"Device Name is : %s\n", (gDevicesList + index)->deviceName);
	  }
	 return true;
  }
  
	bool getDeviceInfo(uint32_t deviceIndex,DeviceInfo* gDevice) 
	{
	  try
	  {
		  TCHAR devicePath[MAX_PATH] = _T("");
		  TCHAR deviceName[MAX_PATH] = _T("");
		  TCHAR extrctd_vid[10] = _T("");
		  TCHAR extrctd_pid[10] = _T("");
		  TCHAR* vid_substr;
		  TCHAR* pid_substr;
		  TCHAR device_name[MAX_PATH] = _T("");

		  std::wstring arr_w;
		  std::string str;
		  HRESULT hr;
		  ULONG cFetched;
		  IMoniker* pM;
		  ICreateDevEnum* pCreateDevEnum = 0;
		  IEnumMoniker* pEm = 0;
		  UINT8 Count = 0;
		  if (!isValidIndex(deviceIndex)) 
		  {
			  return false;
		  }
		  getDevNodeNumber(&deviceIndex);
		  hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER,
			  IID_ICreateDevEnum, (void**)&pCreateDevEnum);
		  if (hr != NO_ERROR)
		  {
			  SetLastError(0);
			  return false;
		  }

		  hr = pCreateDevEnum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &pEm, 0);
		  if (hr != NOERROR)
		  {
			  return false;
		  }
		  
		  pEm->Reset();

		  while (hr = pEm->Next(1, &pM, &cFetched), hr == S_OK)
		  {
			  IPropertyBag* pBag = 0;
			  hr = pM->BindToStorage(0, 0, IID_IPropertyBag, (void**)&pBag);

			  if (SUCCEEDED(hr))
			  {
				  VARIANT var;
				  var.vt = VT_BSTR;
				  hr = pBag->Read(L"DevicePath", &var, 0);
				  if (hr == S_OK)
				  {
					  StringCbPrintf(devicePath, MAX_PATH, L"%s", var.bstrVal);

					  if (devicePath != NULL)
					  {
						  vid_substr = wcsstr(wcsupr(devicePath), TEXT("VID_"));

						  if (vid_substr != NULL)
						  {
							  wcsncpy_s(extrctd_vid, vid_substr + 4, 4);
							  extrctd_vid[5] = '\0';
						  }

						  pid_substr = wcsstr(wcsupr(devicePath), TEXT("PID_"));

						  if (pid_substr != NULL)
						  {
							  wcsncpy_s(extrctd_pid, pid_substr + 4, 4);
							  extrctd_pid[5] = '\0';
						  }

						  if ((wcscmp(wcsupr(extrctd_vid), TOF_VID) == 0) && (wcscmp(wcsupr(extrctd_pid), TOF_PID) == 0))
						  {
							  if (Count == deviceIndex) {
								  VARIANT var_FriendlyName;
								  var_FriendlyName.vt = VT_BSTR;
								  hr = pBag->Read(L"FriendlyName", &var_FriendlyName, NULL);
								  if (hr == S_OK)
								  {
									  wcstombs(gDevice->vid, extrctd_vid, wcslen(extrctd_vid) + 1);
									  wcstombs(gDevice->pid, extrctd_pid, wcslen(extrctd_pid) + 1);
									  wcstombs(gDevice->deviceName, var_FriendlyName.bstrVal, wcslen(var_FriendlyName.bstrVal) + 1);
									  wcstombs(gDevice->devicePath, devicePath, wcslen(devicePath) + 1);

								  }
							  }
							  Count++;
						  }
					  }
					  SysFreeString(var.bstrVal);
				  }
				  pM->AddRef();

			  }
			  else
			  {
				  pEm->Release();
				  printf("NotInitialized");
				  return false;
			  }
			  pM->Release();
		  }
		  pEm->Release();
		 return true;
	  }
	  catch (...)
	  {
		  DebugMessage(DB_LOW, L"Exception EnumerateVideoDevices....\r\n");
		  return false;
	  }
  }
  
  
	PYBIND11_MODULE(pyeCam, m)
	{
    	m.def("getDeviceInfo", &getDeviceInfo, "getDeviceInfo");
		m.def("getDeviceListInfo", &getDeviceListInfo, "getDeviceListInfo");
		m.def("getDeviceCount", &getDeviceCount, R"pbdoc(Get device count)pbdoc");
		 
		py::class_<DeviceInfo>(m, "DeviceInfo")
        .def(py::init<>())
        .def_property("deviceName",
            [](const DeviceInfo& info) {
                return py::array(py::buffer_info(
                    const_cast<char*>(info.deviceName),
                    sizeof(char),
                    py::format_descriptor<char>::format(),
                    1,
                    {50},
                    {sizeof(char)}
                ));
            },
            [](DeviceInfo& info, const py::array_t<char>& arr) {
                auto buf = arr.request();
                if (buf.size != 50)
                    throw std::runtime_error("Invalid array size");
                std::memcpy(info.deviceName, buf.ptr, buf.size * sizeof(char));
            }
        )
        .def_property("vid",
            [](const DeviceInfo& info) {
                return py::array(py::buffer_info(
                    const_cast<char*>(info.vid),
                    sizeof(char),
                    py::format_descriptor<char>::format(),
                    1,
                    {5},
                    {sizeof(char)}
                ));
            },
            [](DeviceInfo& info, const py::array_t<char>& arr) {
                auto buf = arr.request();
                if (buf.size != 5)
                    throw std::runtime_error("Invalid array size");
                std::memcpy(info.vid, buf.ptr, buf.size * sizeof(char));
            }
        )
        .def_property("pid",
            [](const DeviceInfo& info) {
                return py::array(py::buffer_info(
                    const_cast<char*>(info.pid),
                    sizeof(char),
                    py::format_descriptor<char>::format(),
                    1,
                    {5},
                    {sizeof(char)}
                ));
            },
            [](DeviceInfo& info, const py::array_t<char>& arr) {
                auto buf = arr.request();
                if (buf.size != 5)
                    throw std::runtime_error("Invalid array size");
                std::memcpy(info.pid, buf.ptr, buf.size * sizeof(char));
            }
        )
        .def_property("devicePath",
            [](const DeviceInfo& info) {
                return py::array(py::buffer_info(
                    const_cast<char*>(info.devicePath),
                    sizeof(char),
                    py::format_descriptor<char>::format(),
                    1,
                    {500},
                    {sizeof(char)}
                ));
            },
            [](DeviceInfo& info, const py::array_t<char>& arr) {
                auto buf = arr.request();
                if (buf.size != 500)
                    throw std::runtime_error("Invalid array size");
                std::memcpy(info.devicePath, buf.ptr, buf.size * sizeof(char));
            }
        )
        .def_property("serialNo",
            [](const DeviceInfo& info) {
                return py::array(py::buffer_info(
                    const_cast<char*>(info.serialNo),
                    sizeof(char),
                    py::format_descriptor<char>::format(),
                    1,
                    {50},
                    {sizeof(char)}
                ));
            },
            [](DeviceInfo& info, const py::array_t<char>& arr) {
                auto buf = arr.request();
                if (buf.size != 50)
                    throw std::runtime_error("Invalid array size");
               std::memcpy(info.serialNo, buf.ptr, buf.size * sizeof(char));}
);
	}