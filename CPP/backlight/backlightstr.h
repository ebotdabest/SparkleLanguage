#include <vector>

class BacklightString {
private:
	char* content;

public:
	BacklightString(const char* content);
	~BacklightString();

	char* getContent() const { return this->content; };
	size_t length();
	
	BacklightString* slice(int start, int end);
	bool compare(BacklightString* other);
	void append(BacklightString* other);
	BacklightString format(std::vector<BacklightString*> am);

	bool operator==(const BacklightString& other) const;
};