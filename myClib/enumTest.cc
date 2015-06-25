#include <iostream>
#include <vector>

using namespace std;

int
main ()
{
    enum {FIRST=0, SECOND=10};
    cout << "FIRST:" << FIRST << "\nSECOND:" << SECOND << endl;
    vector<int> v;
    v.push_back(1);
    v.push_back(2);

    return 0;
}
