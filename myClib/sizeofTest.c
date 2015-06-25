#include <stdio.h>
#include <stdlib.h>

int main()
{
    short b = 1;
    unsigned short c = 11;
    unsigned short a[2];
    
    printf("short length: %d\n", sizeof(b));
    printf("unsigned short length: %d\n", sizeof(c));
    printf("unsigned short array length: %d\n", sizeof(a));
    return 0;
}
