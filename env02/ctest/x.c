#include <stdlib.h>
#include <stdio.h>
#include "x.h"

int main()
{
    test t;
    t.id = 123;
    t.str = "asdfasf";
    printf("id=%d\nname=%s\n", t.id, t.str);
    return 0;
}
