#include <stdio.h>
#include <utmp.h>

int main()
{
    struct utmp *p = getutent();
    while(p)
    {
        printf("untent: %d\n", p->ut_pid);
        p = getutent();
    }
    return 1;
}
