#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/functional.h>
#include <windows.h>
#include <objbase.h>
#include <dshow.h>
#include <tchar.h>
#include <uuids.h>
#include <WinError.h>
#include <OleAuto.h>

#define	DB_LOW						0x01

namespace py = pybind11;

int32_t indexList = -1;
int internalDeviceCount = 0;

typedef struct
{
    char deviceName[50];
    char vid[5];
    char pid[5];
    char devicePath[500];
    char serialNo[50];
}DeviceInfo;

bool getDeviceCount(pybind11::object& gDeviceCount);
bool getDeviceListInfo(uint32_t deviceCount,DeviceInfo* gDevicesList);
bool getDeviceInfo(uint32_t deviceIndex,DeviceInfo* gDevice) ;
bool initialize();

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
	  initialize();
	  internalDeviceCount = indexList;
		
	  if (internalDeviceCount < 0)
	  {
		  printf("isValidIndex\nis internalDeviceCount <= 0 is failed");
		  return false;
	  }
	  
	  if ((int)deviceIndex > internalDeviceCount || deviceIndex < 0)
	  {
		  printf(" is falsed isvalid index %d\n", (int)deviceIndex);
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
								indexList |= (1 << Count);
								Count++;
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
	  return false;
  	}
	return true;
  }
  
	bool getDeviceCount(pybind11::object& gDeviceCount) 
	{
	  initialize();
	  int list = indexList;
	  internalDeviceCount = 0;
	  gDeviceCount.attr("value") = 0;
	  if (!indexList) 
	  {
		 return false;
	  }
	  while (list)
	  {
		  list &= (list - 1);
		  gDeviceCount.attr("value") = pybind11::int_(gDeviceCount.attr("value").cast<int>() + 1);
		  internalDeviceCount = pybind11::int_(gDeviceCount.attr("value").cast<int>());
	      printf("internalDeviceCount %d\n", internalDeviceCount);
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
			  printf("isValidIndex(deviceIndex) %d\n ", deviceIndex);
			  return false;
			  
		  }
		  getDevNodeNumber(&deviceIndex);
		  hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER,
			  IID_ICreateDevEnum, (void**)&pCreateDevEnum);
		  
		  if (hr != NO_ERROR)
		  {
			  printf("hr != NO_ERROR deviceIndex  %d\n ", deviceIndex);
			  SetLastError(0);
			  return false;
		  }

		  hr = pCreateDevEnum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &pEm, 0);
		  if (hr != NOERROR)
		  {
			  printf(" 2 . hr != NO_ERROR deviceIndex  %d\n ", deviceIndex);
			  return false;
		  }
		  
		  pEm->Reset();

		  while (hr = pEm->Next(1, &pM, &cFetched), hr == S_OK)
		  {
			  			  printf("inside the while -Get Device info deviceIndex  %d\n ", deviceIndex);
			  IPropertyBag* pBag = 0;
			  hr = pM->BindToStorage(0, 0, IID_IPropertyBag, (void**)&pBag);

			  if (SUCCEEDED(hr))
			  {
				  printf("SUCCEEDED(hr)");
				  VARIANT var;
				  var.vt = VT_BSTR;
				  hr = pBag->Read(L"DevicePath", &var, 0);
				  
				  if (hr == S_OK)
				  {
					  printf("if (hr == S_OK)");
					  StringCbPrintf(devicePath, MAX_PATH, L"%s", var.bstrVal);

					  if (devicePath != NULL)
					  {
						  printf("devicePath != NULL");
						  vid_substr = wcsstr(wcsupr(devicePath), TEXT("VID_"));

						  if (vid_substr != NULL)
						  {
							  printf("vid_substr != NULL");
							  wcsncpy_s(extrctd_vid, vid_substr + 4, 4);
							  extrctd_vid[5] = '\0';
						  }

						  pid_substr = wcsstr(wcsupr(devicePath), TEXT("PID_"));

						  if (pid_substr != NULL)
						  {
							  printf("pid_substr != NULL");
							  wcsncpy_s(extrctd_pid, pid_substr + 4, 4);
							  extrctd_pid[5] = '\0';
						  }
							printf("Before Count == deviceIndex");
							printf("Count = %d\n", (int)Count);
						    printf("deviceIndex = %d\n", (int)deviceIndex);
							
							  if (Count == deviceIndex) 
							  {
								  printf("inside a Count == deviceIndex");
								  VARIANT var_FriendlyName;
								  var_FriendlyName.vt = VT_BSTR;
								  hr = pBag->Read(L"FriendlyName", &var_FriendlyName, NULL);
								  if (hr == S_OK)
								  {
									  printf(" Count == deviceIndex hr == S_OK");
									  wcstombs(gDevice->vid, extrctd_vid, wcslen(extrctd_vid) + 1);
									  wcstombs(gDevice->pid, extrctd_pid, wcslen(extrctd_pid) + 1);
									  wcstombs(gDevice->deviceName, var_FriendlyName.bstrVal, wcslen(var_FriendlyName.bstrVal) + 1);
									  wcstombs(gDevice->devicePath, devicePath, wcslen(devicePath) + 1);
									  printf(" completed");
								  }
						  }
						   Count++;
					  }
					  SysFreeString(var.bstrVal);
				  }
				  pM->AddRef();
			  }
			  else
			  {
				  pEm->Release();
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
  
  // Wrap the getDeviceInfo function
	py::tuple getDeviceInfoWrapper(uint32_t deviceIndex) 
	{
		DeviceInfo gDevice;
		bool success = getDeviceInfo(deviceIndex, &gDevice);
		
		// Create a tuple to return the result and device information
		py::tuple result;
		if (success) {
			result = py::make_tuple(success,
				py::reinterpret_borrow<py::str>(PyUnicode_Decode(gDevice.deviceName, strlen(gDevice.deviceName), "utf-8", "replace")),
				py::reinterpret_borrow<py::str>(PyUnicode_Decode(gDevice.vid, strlen(gDevice.vid), "utf-8", "replace")),
				py::reinterpret_borrow<py::str>(PyUnicode_Decode(gDevice.pid, strlen(gDevice.pid), "utf-8", "replace")),
				py::reinterpret_borrow<py::str>(PyUnicode_Decode(gDevice.devicePath, strlen(gDevice.devicePath), "utf-8", "replace")),
				py::reinterpret_borrow<py::str>(PyUnicode_Decode(gDevice.serialNo, strlen(gDevice.serialNo), "utf-8", "replace"))
			);
		} else {
			result = py::make_tuple(success);
		}

		return result;
	}
	
  PYBIND11_MODULE(pyeCam, m)
	{
    	m.def("getDeviceInfo", &getDeviceInfoWrapper, py::arg("deviceIndex"),
          "Get device information");
		m.def("getDeviceListInfo", &getDeviceListInfo, "getDeviceListInfo");
		m.def("getDeviceCount", &getDeviceCount, R"pbdoc(Get device count)pbdoc");
		 
	}