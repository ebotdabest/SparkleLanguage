#include "pch.h"
#include "backlightstr.h"
#include <cstring>
#include <iostream>
#include <vector>
#include <sstream>

size_t BacklightString::length() {
	return std::strlen(this->content);
}

BacklightString::BacklightString(const char* content) {
	this->content = _strdup(content);
}

BacklightString::~BacklightString() {
	free(this->content); 
}

BacklightString BacklightString::format(std::vector<BacklightString*> am) {
	std::ostringstream str;
	str << this->content;
	std::string content_string = str.str();

	size_t pos = 0;

	for (BacklightString* t : am) {
		pos = content_string.find("{}", pos);
		content_string.replace(pos, 2, t->content);
		pos += t->length();
	}
	BacklightString bstr(content_string.c_str());
	return bstr;
}

bool BacklightString::operator==(const BacklightString& other) const {
	return this->content == other.content;
}