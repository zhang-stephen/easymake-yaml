/**
 * the CRC-32C Algorithm header
 */

#ifndef __CRC32_H
#define __CRC32_H

#include <stdint.h>

uint32_t crc32c_sw(uint32_t crc32c, uint8_t* buffer, uint32_t len);

#endif //__CRC32_H

// EOF
