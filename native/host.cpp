#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <wincrypt.h>
#include <stdint.h>
#include <stdio.h>
#include <wchar.h>
#include <cstring>
#include <exception>
#include <string>
#include <vector>
#include "profile.h"
#include "protocol.h"

namespace {
constexpr wchar_t kDllName[] = L"uni2-frame-meter.dll";
constexpr DWORD kWaitMs = 30000;
constexpr uint64_t kExpectedBytes = FM_IMAGE_BYTES;

struct Failure { std::wstring text; DWORD error; };
[[noreturn]] void fail(const std::wstring& s, DWORD error = 0) {
    throw Failure{s, error};
}
struct Handle {
    HANDLE value = nullptr;
    explicit Handle(HANDLE h = nullptr) : value(h) {}
    ~Handle() { if (value && value != INVALID_HANDLE_VALUE) CloseHandle(value); }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
};
struct RemoteMemory {
    HANDLE process;
    void* value;
    RemoteMemory(HANDLE p, size_t bytes) : process(p),
        value(VirtualAllocEx(p, nullptr, bytes, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE)) {
        if (!value) fail(L"Cannot allocate native-helper initialization memory.", GetLastError());
    }
    ~RemoteMemory() { if (value) VirtualFreeEx(process, value, 0, MEM_RELEASE); }
    void leave_allocated() { value = nullptr; }
};
struct LocalModule {
    HMODULE value;
    explicit LocalModule(HMODULE m) : value(m) {}
    ~LocalModule() { if (value) FreeLibrary(value); }
};

std::wstring error_text(DWORD error) {
    wchar_t* buffer = nullptr;
    DWORD n = FormatMessageW(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM |
                            FORMAT_MESSAGE_IGNORE_INSERTS, nullptr, error, 0,
                            reinterpret_cast<wchar_t*>(&buffer), 0, nullptr);
    std::wstring result = n && buffer ? std::wstring(buffer, n) : L"Unknown Windows error";
    if (buffer) LocalFree(buffer);
    while (!result.empty() && (result.back() == L'\r' || result.back() == L'\n')) result.pop_back();
    return result + L" (" + std::to_wstring(error) + L")";
}
std::wstring basename(const std::wstring& path) {
    auto last = path.find_last_of(L"/\\");
    return last == std::wstring::npos ? path : path.substr(last + 1);
}
std::wstring exe_path() {
    std::vector<wchar_t> path(32768);
    DWORD n = GetModuleFileNameW(nullptr, path.data(), static_cast<DWORD>(path.size()));
    if (!n || n >= path.size()) fail(L"Cannot locate the native helper executable.", GetLastError());
    return std::wstring(path.data(), n);
}
std::wstring process_path(HANDLE process) {
    std::vector<wchar_t> path(32768);
    DWORD n = static_cast<DWORD>(path.size());
    if (!QueryFullProcessImageNameW(process, 0, path.data(), &n))
        fail(L"Cannot read the target executable path.", GetLastError());
    return std::wstring(path.data(), n);
}
void read_exact(HANDLE file, uint64_t offset, void* data, DWORD bytes) {
    LARGE_INTEGER position; position.QuadPart = static_cast<LONGLONG>(offset);
    if (!SetFilePointerEx(file, position, nullptr, FILE_BEGIN)) fail(L"Cannot seek within the executable file.", GetLastError());
    DWORD read = 0;
    if (!ReadFile(file, data, bytes, &read, nullptr) || read != bytes)
        fail(L"Executable file read was incomplete.", GetLastError());
}
void verify_pe32_file(HANDLE file, uint64_t length) {
    IMAGE_DOS_HEADER dos{};
    read_exact(file, 0, &dos, sizeof(dos));
    if (dos.e_magic != IMAGE_DOS_SIGNATURE || dos.e_lfanew < static_cast<LONG>(sizeof(dos)) ||
        static_cast<uint64_t>(dos.e_lfanew) > length ||
        sizeof(IMAGE_NT_HEADERS32) > length - static_cast<uint64_t>(dos.e_lfanew))
        fail(L"Target is not a valid PE32 image. Injection was refused.");
    IMAGE_NT_HEADERS32 nt{};
    read_exact(file, static_cast<uint64_t>(dos.e_lfanew), &nt, sizeof(nt));
    if (nt.Signature != IMAGE_NT_SIGNATURE || nt.FileHeader.Machine != IMAGE_FILE_MACHINE_I386 ||
        nt.FileHeader.SizeOfOptionalHeader < sizeof(IMAGE_OPTIONAL_HEADER32) ||
        nt.OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC)
        fail(L"Only the supported PE32 UNI2 image may be injected.");
}
std::vector<MODULEENTRY32W> modules(DWORD pid) {
    HANDLE snapshot = INVALID_HANDLE_VALUE;
    for (unsigned attempt = 0; attempt < 8; ++attempt) {
        snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid);
        if (snapshot != INVALID_HANDLE_VALUE) break;
        if (GetLastError() != ERROR_BAD_LENGTH) break;
        Sleep(10);
    }
    Handle owner(snapshot);
    if (snapshot == INVALID_HANDLE_VALUE) fail(L"Cannot enumerate the target PE32 module list.", GetLastError());
    MODULEENTRY32W entry{}; entry.dwSize = sizeof(entry);
    std::vector<MODULEENTRY32W> result;
    if (!Module32FirstW(snapshot, &entry)) fail(L"The target process module list is empty.", GetLastError());
    do { result.push_back(entry); } while (Module32NextW(snapshot, &entry));
    if (GetLastError() != ERROR_NO_MORE_FILES) fail(L"Target module enumeration was incomplete.", GetLastError());
    return result;
}
const MODULEENTRY32W* find_module(const std::vector<MODULEENTRY32W>& items, const std::wstring& name) {
    const MODULEENTRY32W* result = nullptr;
    for (const auto& item : items) {
        if (_wcsicmp(item.szModule, name.c_str()) == 0) {
            if (result) fail(L"Duplicate module names make the remote call address ambiguous.");
            result = &item;
        }
    }
    return result;
}
void verify_remote_pe(HANDLE process, const MODULEENTRY32W& module) {
    IMAGE_DOS_HEADER dos{}; SIZE_T read = 0;
    if (!ReadProcessMemory(process, module.modBaseAddr, &dos, sizeof(dos), &read) || read != sizeof(dos))
        fail(L"Cannot verify the running target image.", GetLastError());
    if (dos.e_magic != IMAGE_DOS_SIGNATURE || dos.e_lfanew < static_cast<LONG>(sizeof(dos)) ||
        static_cast<uint64_t>(dos.e_lfanew) + sizeof(IMAGE_NT_HEADERS32) > module.modBaseSize)
        fail(L"Running target image headers are invalid. Injection was refused.");
    IMAGE_NT_HEADERS32 nt{};
    if (!ReadProcessMemory(process, module.modBaseAddr + dos.e_lfanew, &nt, sizeof(nt), &read) || read != sizeof(nt))
        fail(L"Cannot read the running PE32 headers.", GetLastError());
    if (nt.Signature != IMAGE_NT_SIGNATURE || nt.FileHeader.Machine != IMAGE_FILE_MACHINE_I386 ||
        nt.OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC ||
        nt.OptionalHeader.SizeOfImage != module.modBaseSize)
        fail(L"Running target is not the expected PE32 image. Injection was refused.");
}
uintptr_t remote_system_function(DWORD pid, const char* name) {
    HMODULE kernel32 = GetModuleHandleW(L"kernel32.dll");
    FARPROC function = kernel32 ? GetProcAddress(kernel32, name) : nullptr;
    if (!function) fail(L"Cannot locate the Windows loader function.", GetLastError());
    HMODULE owner = nullptr;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                          reinterpret_cast<LPCWSTR>(function), &owner))
        fail(L"Cannot identify the real owner module of the Windows loader function.", GetLastError());
    std::vector<wchar_t> owner_path(32768);
    DWORD n = GetModuleFileNameW(owner, owner_path.data(), static_cast<DWORD>(owner_path.size()));
    if (!n || n >= owner_path.size()) fail(L"Cannot read the path of the loader owner module.", GetLastError());
    uintptr_t rva = reinterpret_cast<uintptr_t>(function) - reinterpret_cast<uintptr_t>(owner);
    auto items = modules(pid);
    const auto* remote_owner = find_module(items, basename(std::wstring(owner_path.data(), n)));
    if (!remote_owner || rva >= remote_owner->modBaseSize)
        fail(L"The target loader owner module is absent or the loader RVA is out of bounds.");
    // No kernel32 base-address equality is assumed. The owner image is
    // independently checked before the remote call.
    return reinterpret_cast<uintptr_t>(remote_owner->modBaseAddr) + rva;
}
void verify_system_function(HANDLE process, uintptr_t remote) {
    FARPROC local = GetProcAddress(GetModuleHandleW(L"kernel32.dll"), "LoadLibraryW");
    HMODULE owner = nullptr;
    if (!local || !GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                    reinterpret_cast<LPCWSTR>(local), &owner))
        fail(L"Cannot verify the local loader owner module.", GetLastError());
    const auto* base = reinterpret_cast<const unsigned char*>(owner);
    IMAGE_DOS_HEADER dos{}; IMAGE_NT_HEADERS32 local_nt{}; SIZE_T read = 0;
    if (!ReadProcessMemory(GetCurrentProcess(), base, &dos, sizeof(dos), &read) || read != sizeof(dos) ||
        dos.e_magic != IMAGE_DOS_SIGNATURE || dos.e_lfanew < static_cast<LONG>(sizeof(dos)) || dos.e_lfanew > 1024 * 1024)
        fail(L"The loader owner module has invalid DOS headers.");
    if (!ReadProcessMemory(GetCurrentProcess(), base + dos.e_lfanew, &local_nt, sizeof(local_nt), &read) || read != sizeof(local_nt) ||
        local_nt.Signature != IMAGE_NT_SIGNATURE || local_nt.OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC ||
        local_nt.FileHeader.Machine != IMAGE_FILE_MACHINE_I386)
        fail(L"The loader owner module has invalid PE32 headers.");
    uintptr_t rva = reinterpret_cast<uintptr_t>(local) - reinterpret_cast<uintptr_t>(owner);
    if (rva >= local_nt.OptionalHeader.SizeOfImage || remote < rva)
        fail(L"The loader owner function RVA is out of bounds.");
    const auto* remote_base = reinterpret_cast<const unsigned char*>(remote - rva);
    IMAGE_DOS_HEADER remote_dos{}; IMAGE_NT_HEADERS32 remote_nt{};
    if (!ReadProcessMemory(process, remote_base, &remote_dos, sizeof(remote_dos), &read) || read != sizeof(remote_dos) ||
        remote_dos.e_magic != IMAGE_DOS_SIGNATURE || remote_dos.e_lfanew != dos.e_lfanew)
        fail(L"The target loader DOS headers do not match this process.");
    if (!ReadProcessMemory(process, remote_base + remote_dos.e_lfanew, &remote_nt, sizeof(remote_nt), &read) || read != sizeof(remote_nt))
        fail(L"Cannot read target loader PE32 headers.", GetLastError());
    // Headers retain the preferred ImageBase after normal relocation. This
    // comparison permits different runtime bases, and avoids touching discarded
    // relocation pages or comparing instructions containing absolute addresses.
    if (memcmp(&local_nt, &remote_nt, sizeof(local_nt)) != 0)
        fail(L"Target and local loader owners are different PE32 images; borrowing their RVA was refused.");
    unsigned char readable = 0;
    if (!ReadProcessMemory(process, reinterpret_cast<const void*>(remote), &readable, 1, &read) || read != 1)
        fail(L"The target loader function address is unreadable.", GetLastError());
}
void write_remote(HANDLE process, void* target, const void* data, SIZE_T bytes) {
    SIZE_T written = 0;
    if (!WriteProcessMemory(process, target, data, bytes, &written) || written != bytes)
        fail(L"Cannot write native-helper initialization parameters.", GetLastError());
}
DWORD call_remote(HANDLE process, uintptr_t function, RemoteMemory& argument) {
    Handle thread(CreateRemoteThread(process, nullptr, 0,
        reinterpret_cast<LPTHREAD_START_ROUTINE>(function), argument.value, 0, nullptr));
    if (!thread.value) fail(L"Cannot create the native-helper initialization thread.", GetLastError());
    DWORD wait = WaitForSingleObject(thread.value, kWaitMs);
    if (wait != WAIT_OBJECT_0) {
        // A timed-out thread may still access the parameter. Deliberately retain
        // its tiny allocation, rather than causing a use-after-free in the game.
        argument.leave_allocated();
        if (wait == WAIT_TIMEOUT)
            fail(L"Initialization exceeded 30 seconds and may still be running. Its parameter memory was retained. Restart the game before retrying.");
        fail(L"Initialization wait failed; memory still possibly used by that thread was retained.", GetLastError());
    }
    DWORD result = 0;
    if (!GetExitCodeThread(thread.value, &result)) fail(L"Cannot read the initialization thread result.", GetLastError());
    return result;
}
uintptr_t export_rva(const std::wstring& dll, const char* name, IMAGE_NT_HEADERS32& identity) {
    LocalModule local(LoadLibraryExW(dll.c_str(), nullptr, DONT_RESOLVE_DLL_REFERENCES));
    if (!local.value) fail(L"Cannot parse the companion DLL. Keep the helper executable and DLL in the same directory.", GetLastError());
    const uintptr_t base=reinterpret_cast<uintptr_t>(local.value);
    IMAGE_DOS_HEADER dos{}; IMAGE_NT_HEADERS32 nt{};
    if (!FmRead(GetCurrentProcess(),base,&dos,sizeof(dos)) || dos.e_magic!=IMAGE_DOS_SIGNATURE ||
        dos.e_lfanew<static_cast<LONG>(sizeof(dos)) || dos.e_lfanew>1024*1024 ||
        !FmRead(GetCurrentProcess(),base+static_cast<uint32_t>(dos.e_lfanew),&nt,sizeof(nt)) ||
        nt.Signature!=IMAGE_NT_SIGNATURE || nt.OptionalHeader.Magic!=IMAGE_NT_OPTIONAL_HDR32_MAGIC ||
        nt.FileHeader.Machine!=IMAGE_FILE_MACHINE_I386 ||
        nt.FileHeader.SizeOfOptionalHeader!=sizeof(IMAGE_OPTIONAL_HEADER32))
        fail(L"The companion DLL is not a PE32 frame-meter module.");
    FARPROC function = GetProcAddress(local.value, name);
    if (!function) fail(L"The companion DLL lacks the required frame-meter export.", GetLastError());
    uintptr_t ptr = reinterpret_cast<uintptr_t>(function), start = base;
    if (ptr < start || ptr - start >= nt.OptionalHeader.SizeOfImage)
        fail(L"The companion DLL export is forwarded and cannot be called safely.");
    identity = nt;
    return ptr - start;
}
void verify_loaded_dll(HANDLE process, const MODULEENTRY32W& module, const IMAGE_NT_HEADERS32& identity) {
    verify_remote_pe(process, module);
    IMAGE_DOS_HEADER dos{}; IMAGE_NT_HEADERS32 loaded{}; SIZE_T read = 0;
    if (!ReadProcessMemory(process, module.modBaseAddr, &dos, sizeof(dos), &read) || read != sizeof(dos) ||
        !ReadProcessMemory(process, module.modBaseAddr + dos.e_lfanew, &loaded, sizeof(loaded), &read) || read != sizeof(loaded))
        fail(L"Cannot verify the loaded frame-meter DLL version.", GetLastError());
    if (memcmp(&loaded, &identity, sizeof(identity)) != 0)
        fail(L"The game retains an older frame-meter DLL. Restart the game before attaching this package.");
}
}

namespace {
void output(const std::wstring& value,bool error=false) {
    const HANDLE handle=GetStdHandle(error?STD_ERROR_HANDLE:STD_OUTPUT_HANDLE);
    const int bytes=WideCharToMultiByte(CP_UTF8,0,value.data(),static_cast<int>(value.size()),nullptr,0,nullptr,nullptr);
    if (bytes<=0) return;
    std::string utf8(static_cast<size_t>(bytes),'\0');
    WideCharToMultiByte(CP_UTF8,0,value.data(),static_cast<int>(value.size()),utf8.data(),bytes,nullptr,nullptr);
    DWORD done=0; WriteFile(handle,utf8.data(),static_cast<DWORD>(utf8.size()),&done,nullptr);
}
std::wstring companion() {
    const auto path=exe_path(); const auto slash=path.find_last_of(L"/\\");
    if (slash==std::wstring::npos) fail(L"Cannot locate the native helper directory.");
    return path.substr(0,slash+1)+kDllName;
}
uintptr_t attach(DWORD pid) {
    static_assert(sizeof(void*)==4,"PE32 injector only");
    Handle process(OpenProcess(PROCESS_CREATE_THREAD|PROCESS_QUERY_INFORMATION|PROCESS_VM_OPERATION|
        PROCESS_VM_WRITE|PROCESS_VM_READ|SYNCHRONIZE,FALSE,pid));
    if (!process.value) fail(L"Cannot open game process. Run the overlay with the same user and privilege level as the game.",GetLastError());
    const auto path=process_path(process.value);
    if (_wcsicmp(basename(path).c_str(),L"uni2.exe")) fail(L"Selected process is not uni2.exe.");
    Handle file(CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr));
    if (file.value==INVALID_HANDLE_VALUE) fail(L"Cannot lock the game executable for version verification.",GetLastError());
    LARGE_INTEGER size{};
    if (!GetFileSizeEx(file.value,&size) || size.QuadPart!=static_cast<LONGLONG>(kExpectedBytes))
        fail(L"Unsupported game update: executable file size differs. No hook was installed.");
    verify_pe32_file(file.value,kExpectedBytes);
    std::string hash;
    if (!FmSha256(file.value,hash)) fail(L"Cannot compute executable SHA-256.",GetLastError());
    if (hash!=FM_GAME_SHA256) fail(L"Unsupported game update (SHA-256 "+std::wstring(hash.begin(),hash.end())+L"). No hook was installed.");
    const auto initial=modules(pid); const auto* game=find_module(initial,L"uni2.exe");
    if (!game || _wcsicmp(game->szExePath,path.c_str())) fail(L"Loaded executable does not match the verified file.");
    verify_remote_pe(process.value,*game);
    const uintptr_t base=reinterpret_cast<uintptr_t>(game->modBaseAddr);
    if (!FmGameImage(process.value,base)) fail(L"Loaded executable PE identity does not match this profile.");
    const auto dll=companion(); IMAGE_NT_HEADERS32 identity{};
    const uintptr_t rva=export_rva(dll,"FrameMeterStart",identity);
    const auto* previous=find_module(initial,kDllName);
    if (previous && _wcsicmp(previous->szExePath,dll.c_str()))
        fail(L"The game retains a frame-meter DLL from another directory. Restart the game before attaching this package.");
    if (!previous) {
        if (!FmHookSignature(process.value,base))
            fail(L"Native frame entry does not match its audited signature, or another tool already hooks it. No hook was installed.");
        const uintptr_t load=remote_system_function(pid,"LoadLibraryW");
        verify_system_function(process.value,load);
        RemoteMemory argument(process.value,(dll.size()+1)*sizeof(wchar_t));
        write_remote(process.value,argument.value,dll.c_str(),(dll.size()+1)*sizeof(wchar_t));
        if (!call_remote(process.value,load,argument)) fail(L"The game could not load the native frame-meter DLL.");
    }
    const auto loaded=modules(pid); const auto* mod=find_module(loaded,kDllName);
    if (!mod || _wcsicmp(mod->szExePath,dll.c_str()) || rva>=mod->modBaseSize)
        fail(L"Loaded native frame-meter DLL identity is inconsistent.");
    verify_loaded_dll(process.value,*mod,identity);
    // The start export accepts nullptr or an unused pointer. An owned buffer
    // follows the same retained-on-timeout rule as the LoadLibrary path.
    RemoteMemory argument(process.value,4); const uint32_t zero=0;
    write_remote(process.value,argument.value,&zero,sizeof(zero));
    const DWORD result=call_remote(process.value,reinterpret_cast<uintptr_t>(mod->modBaseAddr)+rva,argument);
    if (result) fail(L"Native frame-meter initialization was rejected (code "+std::to_wstring(result)+L"). Restart the game before retrying.");
    return base;
}
}
int wmain(int argc,wchar_t** argv) {
    try {
        if (argc==2 && (!std::wcscmp(argv[1],L"--help") || !std::wcscmp(argv[1],L"-h"))) {
            output(L"UNI2 Frame Meter native host\nUsage: uni2-frame-meter-host.exe --attach PID\n       uni2-frame-meter-host.exe --self-check\n"); return 0;
        }
        if (argc==2 && !std::wcscmp(argv[1],L"--self-check")) {
            IMAGE_NT_HEADERS32 identity{};
            export_rva(companion(),"FrameMeterStart",identity);
            output(L"{\"abi\":1,\"bits\":32,\"header_bytes\":256,\"slot_bytes\":614400,\"capacity\":64,\"game_sha256\":\""
                +std::wstring(FM_GAME_SHA256,FM_GAME_SHA256+64)+L"\"}\n"); return 0;
        }
        if (argc!=3 || std::wcscmp(argv[1],L"--attach")) fail(L"Use --attach PID, --self-check, or --help.");
        const wchar_t* number=argv[2];
        if (!*number) fail(L"PID must be a nonzero decimal process identifier.");
        uint64_t value=0;
        for (const wchar_t* p=number;*p;++p) {
            if (*p<L'0' || *p>L'9') fail(L"PID must contain decimal digits only.");
            value=value*10+static_cast<uint64_t>(*p-L'0');
            if (value>UINT32_MAX) fail(L"PID is outside the DWORD range.");
        }
        if (!value) fail(L"PID must be nonzero.");
        const DWORD pid=static_cast<DWORD>(value); const auto base=attach(pid);
        output(L"{\"mapping\":\"Local\\\\UNI2FrameMeter-v1-"+std::to_wstring(pid)+L"\",\"pid\":"+
            std::to_wstring(pid)+L",\"image_base\":"+std::to_wstring(base)+L"}\n"); return 0;
    } catch (const Failure& failure) {
        auto text=failure.text;
        if (failure.error) text+=L"\n"+error_text(failure.error);
        output(text+L"\n",true); return 1;
    } catch (const std::exception&) {
        output(L"Native helper failed while preparing a bounded injection request. No further action was attempted.\n",true); return 1;
    }
}
