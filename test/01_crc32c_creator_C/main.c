// a tools to generate CRC-32C code for single file
// for easymake-yaml test:
// + Makefile Generate for Pure C
// + CLI Options --> all
// + different configuration implementation in easymake.yml

// gcc -o debug.exe -g -O3 -std=c11 .\main.c .\crc32\crc32.c -Icrc32

#include <stdio.h>
#include <stdbool.h>
#include "crc32.h"

int main(int argc, char** argv)
{
	if(argv[1] == NULL)
	{
		printf("Error: Please input the filename!\n");

		return  1;
	}

	FILE* f = fopen(argv[1], "rb");

	if(f == NULL)
	{
		printf("Error: the file does not exists!\n");

		return -1;
	}
	
	// get 4kiB data from opened file
	uint8_t buffer[4096] = {0};
	int16_t buffer_real_size = 0;

	uint32_t crc_value = 0;

	while(true)
	{
		buffer_real_size = fread(buffer, sizeof(uint8_t), 4096u, f);

		if(buffer_real_size != 4096u && feof(f) == 0)
		{
			printf("Error: Read file Failed!\n");

			return -2;
		}

		crc_value = crc32c_sw(crc_value, buffer, buffer_real_size);

		if(feof(f) != 0) { break; }
	}

	printf("The crc value of \"%s\" is 0x%x \n", argv[1], crc_value);

	return 0u;
}

// EOF
