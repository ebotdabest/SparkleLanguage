class BacklightString {
public:
	BacklightString(const char* content);

	const char* content;
	size_t length();
	
	BacklightString* slice(int start, int end);
	void free();
	bool compare(BacklightString* other);
	void append(BacklightString* other);
};