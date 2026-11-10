#include <windows.h>
#include <shellapi.h>
#include <wininet.h>
#include <string>
#include <vector>

#pragma comment(lib, "wininet.lib")
#pragma comment(lib, "shell32.lib")

bool CheckHttpEndpoint(const std::wstring& url) {
    HINTERNET hInternet = InternetOpenW(L"ULTRON_Launcher", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    if (!hInternet) return false;
    
    DWORD flags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE | INTERNET_FLAG_NO_AUTO_REDIRECT;
    HINTERNET hConnect = InternetOpenUrlW(hInternet, url.c_str(), NULL, 0, flags, 0);
    bool ok = false;
    if (hConnect) {
        DWORD statusCode = 0;
        DWORD length = sizeof(statusCode);
        if (HttpQueryInfoW(hConnect, HTTP_QUERY_STATUS_CODE | HTTP_QUERY_FLAG_NUMBER, &statusCode, &length, NULL)) {
            if (statusCode == 200) {
                ok = true;
            }
        }
        InternetCloseHandle(hConnect);
    }
    InternetCloseHandle(hInternet);
    return ok;
}

void RunHidden(const std::wstring& cmd, const std::wstring& workingDir) {
    STARTUPINFOW si = { sizeof(si) };
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    PROCESS_INFORMATION pi = { 0 };

    std::vector<wchar_t> cmdBuf(cmd.begin(), cmd.end());
    cmdBuf.push_back(L'\0');

    if (CreateProcessW(NULL, cmdBuf.data(), NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, 
                       workingDir.empty() ? NULL : workingDir.c_str(), &si, &pi)) {
        CloseHandle(pi.hThread);
        CloseHandle(pi.hProcess);
    }
}

std::wstring FindAppBrowser() {
    const wchar_t* candidates[] = {
        L"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
        L"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        L"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        L"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    };
    for (const auto* path : candidates) {
        if (GetFileAttributesW(path) != INVALID_FILE_ATTRIBUTES) {
            return path;
        }
    }
    return L"msedge.exe";
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, PWSTR pCmdLine, int nCmdShow) {
    (void)hInstance;
    (void)hPrevInstance;
    (void)pCmdLine;
    (void)nCmdShow;

    wchar_t exePath[MAX_PATH];
    GetModuleFileNameW(NULL, exePath, MAX_PATH);
    std::wstring exeDir = exePath;
    size_t lastSlash = exeDir.find_last_of(L"\\/");
    if (lastSlash != std::wstring::npos) {
        exeDir = exeDir.substr(0, lastSlash);
    }

    std::wstring projectRoot = L"E:\\personal d\\ULTRON";
    if (GetFileAttributesW((exeDir + L"\\frontend\\flutter_app").c_str()) != INVALID_FILE_ATTRIBUTES) {
        projectRoot = exeDir;
    }

    // 1. Check & start UI server if not running
    if (!CheckHttpEndpoint(L"http://localhost:3000")) {
        std::wstring webServerCmd = L"python -m http.server 3000 --directory \"" + projectRoot + L"\\frontend\\flutter_app\\build\\web\"";
        RunHidden(webServerCmd, projectRoot);
    }

    // 2. Check & start Backend & Bridge if not running
    if (!CheckHttpEndpoint(L"http://127.0.0.1:8000/health")) {
        RunHidden(L"wsl -d Ubuntu-22.04 docker start ultron_mysql ultron_redis ultron_backend ultron_worker ultron_proxy", projectRoot);
        std::wstring bridgeCmd = L"\"" + projectRoot + L"\\backend\\.venv\\Scripts\\python.exe\" \"" + projectRoot + L"\\scripts\\tailscale_bridge.py\" --listen-ip 0.0.0.0 --listen-port 8000";
        RunHidden(bridgeCmd, projectRoot);
    }

    // 3. Wait up to 3 seconds for UI server
    for (int i = 0; i < 15; ++i) {
        if (CheckHttpEndpoint(L"http://localhost:3000")) break;
        Sleep(200);
    }

    // 4. Launch dedicated standalone desktop window
    std::wstring browser = FindAppBrowser();
    wchar_t localAppData[MAX_PATH];
    GetEnvironmentVariableW(L"LOCALAPPDATA", localAppData, MAX_PATH);
    std::wstring profileDir = std::wstring(localAppData) + L"\\ULTRON\\AppProfile";

    std::wstring appArgs = L"--app=http://localhost:3000 --window-size=1440,900 --user-data-dir=\"" + profileDir + L"\" --app-id=ultron-os";

    HINSTANCE res = ShellExecuteW(NULL, L"open", browser.c_str(), appArgs.c_str(), NULL, SW_SHOWNORMAL);
    if ((INT_PTR)res <= 32) {
        ShellExecuteW(NULL, L"open", L"http://localhost:3000", NULL, NULL, SW_SHOWNORMAL);
    }

    return 0;
}
