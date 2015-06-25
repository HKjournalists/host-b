#include <iostream>
#include <string>
#include "ref_ptr.hh"

using namespace std;

class TransactionOperation {
public:
    //默认构造方法
    TransactionOperation():_name("wangbin"),_id(0001){
    }
    void printAttr() const{
        cout << "name:" << _name << endl;
        cout << "code:" << _id << endl;
    }
    string name() const{
        return _name;
    }
private:
    string _name;
    int _id;
};

class TransactionManager {
public:
    typedef ref_ptr<TransactionOperation> Operation;
    //默认构造方法
    TransactionManager(){
    }
    void
    add(const Operation& op){
        _ops.push_back(op);
    }
private:
    list<Operation> _ops;
};

int
main(){
    TransactionOperation t;     //调用默认构造方法
    TransactionManager m;
    TransactionManager::Operation o(new TransactionOperation());
    m.add(o); 
}
