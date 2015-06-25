#include <vector>
#include <string>
#include <iostream>

using namespace std;

template <class T>
void printvec(vector<T> &vec){
	typename vector<T>::iterator it;
	cout<<"===vec===:"<<endl;
	for(it=vec.begin(); it!= vec.end(); ++it){
		cout<<*it<<endl;
	}
}


int main(){
	int a[]={2,3,4,5};
	vector<int> vec_int(a,a+4);
	printvec<int>(vec_int);
	return 0;
}

