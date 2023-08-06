#include "stringbox.h"
#include <string.h>

namespace lyramilk{ namespace data
{
	stringbox::stringbox()
	{
		
	}

	stringbox::~stringbox()
	{
		
	}

	unsigned long stringbox::alloc(const char* data,unsigned long size)
	{
		unsigned long r = sb.size();
		sb.append((char*)&size,sizeof(size));
		sb.append(data,size);
		sb.push_back(0);
		return r;
	}

	bool stringbox::get(unsigned long dataid,const char** data,unsigned long* size)
	{
		if(dataid + sizeof(unsigned long) >= sb.size()) return false;
		sb.copy((char*)size,sizeof(unsigned long),dataid);
		if(dataid + sizeof(unsigned long) + *size + 1 > sb.size()) return false;
		*data = sb.c_str() + dataid + sizeof(unsigned long);
		return true;
	}

	unsigned long stringbox::size()
	{
		return sb.size();
	}


	void stringbox::read(std::istream &is)
	{
		char buff[4096];
		while(is){
			is.read(buff,sizeof(buff));
			sb.append(buff,is.gcount());
		}
	}

	void stringbox::write(std::ostream &os)
	{
		os.write(sb.c_str(),sb.size());
	}





	stringbox_reader::stringbox_reader(const char* pbase,unsigned long size)
	{
		this->pbase = pbase;
		this->totalsize = size;
	}

	stringbox_reader::~stringbox_reader()
	{
		
	}

	bool stringbox_reader::get(unsigned long dataid,const char** data,unsigned long* size)
	{
		if(dataid + sizeof(unsigned long) >= totalsize) return false;
		memcpy((char*)size,pbase + dataid,sizeof(unsigned long));

		if(dataid + sizeof(unsigned long) + *size + 1 > totalsize) return false;
		*data = pbase + dataid + sizeof(unsigned long);
		return true;
	}

	unsigned long stringbox_reader::size()
	{
		return totalsize;
	}
}}
