#include "pch.h"
#include <iostream>
#include "backlightstr.h"
#include <sstream>

#define EXPORT __declspec(dllexport)

typedef void* BacklightStringHandle;

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved) {
    switch (ul_reason_for_call) {
    case DLL_PROCESS_ATTACH:
        break;
    case DLL_THREAD_ATTACH:
        break;
    case DLL_THREAD_DETACH:
        break;
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

extern "C" {
    EXPORT void __backlight_print(char* content, char* separator) {
        std::cout << content << "\n";
    }
    
    EXPORT BacklightStringHandle __backlight_string_create(char* content) {
        return new BacklightString(content);
    }
    
    EXPORT size_t __backlight_string_length(BacklightStringHandle handle) {
        return static_cast<BacklightString*>(handle)->length();
    }

    EXPORT const char* __backlight_string_content(BacklightStringHandle handle) {
        return static_cast<BacklightString*>(handle)->content;
    }

    EXPORT const char* __backlight_number_string(int number) {
        std::ostringstream str1;
        str1 << number;
        std::string result = str1.str();

        char* cstr = (char*)malloc(result.size() + 1);
        
        strcpy_s(cstr, sizeof(result.c_str()), result.c_str());
        return cstr;
    }


}

