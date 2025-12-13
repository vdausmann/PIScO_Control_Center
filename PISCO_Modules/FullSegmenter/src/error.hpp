#pragma once
#include <string>

extern bool e_warningsAsError;

std::string makeRed(std::string str);
std::string makeYellow(std::string str);
std::string makeBlue(std::string str);

// Error struct. Predefined errors are available. An error code of 0 means
// Success, negative values correspond to errors and positve values to warnings.
// Additionaly, messages can be defined which makes debugging easier. Errors
// print warnings when the destructor is called before checking the error.
struct [[nodiscard]] Error {
	private:
		const std::string m_name;
		std::string m_message;
		const int m_errorCode;
		bool m_checked;

	public:
		// constructor from error code with optional error name 
		Error(int errorCode, std::string name = "")
			: m_name(name), m_errorCode(errorCode), m_checked(false) {};

		// constructor from existing error
		Error(const Error& error)
			: m_name(error.m_name), m_message(error.m_message),
				m_errorCode(error.m_errorCode), m_checked(false) {};

		Error operator=(Error& other);
		bool operator==(const Error& other);

		static const Error Success;  // id 0

		// Errors:
		static const Error RuntimeError;  // id -1
		static const Error ConversionError;  // id -2, for parser errors

		// Warnings:
		static const Error EmptyImage;  // id 1
		static const Error CorruptedImage;  // id 2

		bool check(std::string message = "");
		void addMessage(std::string message);
};
