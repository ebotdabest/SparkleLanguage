#include "pch.h"
#include "backlightstr.h"
#include <cstring>
#include "iostream"


size_t BacklightString::length() {
	return std::strlen(this->content);
}

BacklightString::BacklightString(const char* content) {
	this->content = content;
}