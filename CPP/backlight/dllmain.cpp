#include "pch.h"
#include <iostream>
#include "backlightstr.h"
#include <sstream>
#include <cstdarg>
#include <string>


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
        return static_cast<BacklightString*>(handle)->getContent();
    }

    EXPORT const char* __backlight_number_string(int number) {
        std::ostringstream str1;
        str1 << number;
        std::string result = str1.str();

        char* cstr = (char*)malloc(result.size() + 1);
        
        strcpy_s(cstr, result.size() + 1, result.c_str());
        return cstr;
    }

    EXPORT const char* __backlight_generate_string_array(char chars, ...) {
        va_list args;
        va_start(args, chars);

        std::string result;
        result.reserve(chars);

        for (int i = 0; i < chars; ++i) {
            char c = static_cast<char>(va_arg(args, int));
            result += c;
        }

        va_end(args);

        return _strdup(result.c_str());
    }
    
    EXPORT BacklightStringHandle __backlight_string_format(BacklightStringHandle chars, ...) {
        va_list args;
        va_start(args, chars);

        std::vector<BacklightString*> strings;
        int i = 0;
        while (i < 3) {
            i++;
            BacklightStringHandle arg = va_arg(args, BacklightStringHandle);
            if (arg == nullptr) {
                break;
            }
            strings.push_back(static_cast<BacklightString*>(arg));
        }
        BacklightString str = static_cast<BacklightString*>(chars)->format(strings);
        va_end(args);
        return new BacklightString(str.getContent());
    }

}

