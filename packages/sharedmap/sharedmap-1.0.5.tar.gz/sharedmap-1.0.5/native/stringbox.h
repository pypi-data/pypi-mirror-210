#ifndef _lyramilk_ctools_stringbox_h_
#define _lyramilk_ctools_stringbox_h_
#include <string>
#include <iostream>

namespace lyramilk{ namespace data
{

	class stringbox_base
	{
	  public:
		virtual bool get(unsigned long dataid,const char** data,unsigned long* size) = 0;
		virtual unsigned long size() = 0;
	};


	class stringbox:public stringbox_base
	{
	  public:
		std::string sb;
		stringbox();
		virtual ~stringbox();

		unsigned long alloc(const char* data,unsigned long size);
		virtual bool get(unsigned long dataid,const char** data,unsigned long* size);
		virtual unsigned long size();

		void read(std::istream &is);
		void write(std::ostream &os);
	};

	class stringbox_reader:public stringbox_base
	{
		const char *pbase;
		unsigned long totalsize;
	  public:
		stringbox_reader(const char* pbase,unsigned long size);
		virtual ~stringbox_reader();
		virtual bool get(unsigned long dataid,const char** data,unsigned long* size);
		virtual unsigned long size();
	};
}}
#endif
