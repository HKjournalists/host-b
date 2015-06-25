#include <iostream>

using namespace std;

/*实验：const& 形参对实参进行隐式转换后是值传递还是引用传递
* 结论：值传递，需要进行隐式转换时，调用实参的构造函数parm([形参])，再将创建出的临时对象传给形参
*/

class TestClass{
public:
	TestClass(float f = 0):_value(f){}
	void
	printValue() const{
		cout << "in TestClass::printValue()\n_value: " << _value << endl;
	}
private:
	float _value;
};


void 
func(const float& f){
	cout << "形参地址：" <<&f << endl; //打印参数地址
}

void 
func2(const TestClass& tc){	
	cout << "形参地址：" <<&tc << endl; //打印参数地址
	tc.printValue();
}

int
main() {
	double d = 2.0;
	float f = 2.0f;
	
	cout << "未进行隐式转换\n" << "实参地址：" << &f << endl;
	func(f); //未进行隐式转换，直接传递实参的引用给形参，实参形参地址相同
	
	cout << "进行隐式转换\n" << "实参地址：" << &f << endl;
	func(d); //进行隐式转换，实参形参地址不同

	cout << "-------------隐式转换为自定义类型----------------\n\n" << endl;
	/*func2需要一个const TestClass& tc，
	*当传入float类型实参时，实际调用了TestClass(f)进行了隐式类型转换*/
	cout << "实参地址：" << &f << endl;
	func2(f);	
	return 0;
}