#include <stdio.h>
#include <stdlib.h>

int
main(void){
    //struct array init
    struct {
        int nu;
        char *str;
    }s[5] = {
        [2]={1, "abcd"},
        [3]={2, "fghj"}
    };


    //struct init1
    struct test_struct1 {
        int number;
        char *str;
    };

    struct test_struct1 t1 = {12345, "abcde"};
    printf("%d, %s\n", t1.number, t1.str);

    //struct init2
    struct test_struct1 t2 = {
        .str = "t2t2t2t2",
        .number = 23456,
    };
    printf("%d, %s\n", t2.number, t2.str);

    printf("struct member: %d, %s\n", s[2].nu, s[2].str);
    return 1;
}
