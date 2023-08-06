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

namespace py = pybind11;

class DeviceManager {
	
private:
    int32_t indexList = -1;
    int internalDeviceCount = 0;

    typedef struct {
        char deviceName[50];
        char vid[5];
        char pid[5];
        char devicePath[500];
        char serialNo[50];
    } DeviceInfo;

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
			// Modified by Abishek on 10/04/2023 
			// Reason: To clear the indexList even when no video streaming device is present
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

	bool isValidIndex(uint32_t deviceIndex) 
	{
	    uint32_t device_count;
	  
		if (!getDeviceCount(&device_count)) 
		{
			return false;
		}
	  
		if (deviceIndex > device_count || deviceIndex < 0)
			return false;
		  
		return true;
	}
	
	void getDevNodeNumber(uint32_t *nodeNo) 
	{
	    uint32_t auto_index = 0, count = 0;
	    while (auto_index < 16) 
		{
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
	
public:
    DeviceManager() {}

    bool getDeviceCount(uint32_t *gDeviceCount) 
	{
		initialize();
		int list = indexList;
		*gDeviceCount = 0;
		if (!indexList) {
			return false;
		}
		while (list)
		{
			list &= (list - 1);
			*gDeviceCount += 1;
		}
		
		return true;
	}

	bool getDeviceInfo(uint32_t deviceIndex, DeviceInfo* gDevice)
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

			hr = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER, IID_ICreateDevEnum, (void**)&pCreateDevEnum);

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

							if (Count == deviceIndex)
							{
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
			return false;
		}
	}
   

    py::tuple getDeviceInfoWrapper(uint32_t deviceIndex) {
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
	
	py::tuple getDeviceCountWrapper() 
	{
		uint32_t gDeviceCount = 0;
		bool success = getDeviceCount(&gDeviceCount);
		
		// Create a tuple to return the result and device information
		py::tuple result;
		if (success) {
			result = py::make_tuple(success, gDeviceCount);
		} else {
			result = py::make_tuple(success);
		}

		return result;
	}


};

PYBIND11_MODULE(pyeCam, m) {
    py::class_<DeviceManager>(m, "DeviceManager")
        .def(py::init<>())
        .def("getDeviceCount", &DeviceManager::getDeviceCountWrapper, "Get the device count")
        .def("getDeviceInfo", &DeviceManager::getDeviceInfoWrapper, py::arg("deviceIndex"), "Get device information");
}
