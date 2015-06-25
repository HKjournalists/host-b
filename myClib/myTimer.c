#include <stdio.h>  
#include <stdlib.h>  
#include <time.h> 

int main(void)  
{  
    long i = 100000000L;  
    clock_t start, finish;  
    time_t t;
    double duration;  
    time(&t);
    printf("time: %ld\n", t);

    /* 测量一个事件持续的时间*/  
    printf( "Time to do %ld empty loops is :", i );  
    start = clock();  
    while( i-- ) ;  
    finish = clock();  
    duration = (double)(finish - start) / CLOCKS_PER_SEC;  
    printf( "%f seconds\n", duration );  
} 
