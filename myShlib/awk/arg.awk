#!/bin/awk -f
BEGIN {
    printf("A=%d, B=%d\n", A, B);
    for (i = 0; i < ARGC; i++){
        printf("\tARGV[%d] = %s\n", i, ARGV[i]);
    }
}
END { 
    printf("A=%d, B=%d\n", A, B); 
}
