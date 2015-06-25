#include <stdio.h>
#include <stdlib.h>

typedef int (*this_is_a_func_pointer)(int x, int y);
typedef int this_is_a_func(int x, int y);


int func1(int a, int b) {
    return a + b;
}
int func2(int a, int b) {
    return a + b;
}
int main(void){
    this_is_a_func_pointer p = func1;
    printf("%d\n", p(1,2));
    this_is_a_func *p2 = func2;
    printf("%d\n", p2(3,4));
    return 1;
}
