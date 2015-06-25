
#include <assert.h>
#include <iostream>

#include "ref_ptr.hh"

using namespace std;

///////////////////////////////////////////////////////////////////////////////
//
// ref_counter_pool implementation
//

ref_counter_pool ref_counter_pool::_the_instance;

ref_counter_pool&
ref_counter_pool::instance()
{
    return ref_counter_pool::_the_instance;
}

void
ref_counter_pool::grow()
{
    size_t old_size = _counters.size();
    _counters.resize(old_size + old_size / 8 + 1);

    for (size_t i = old_size; i < _counters.size(); i++) {
    	_counters[i] = _free_index;
    	_free_index = i;
    }
}

void
ref_counter_pool::check()
{
    int i = _free_index;
    size_t n = 0;
    while (_counters[i] != LAST_FREE) {
    	i = _counters[i];
    	n++;
    	if (n == _counters.size()) {
    	    dump();
    	    //abort();
    	}
    }
}

bool
ref_counter_pool::on_free_list(int index)
{
    int i = _free_index;
    size_t n = 0;
    while (_counters[i] != LAST_FREE) {
    	if (i == index) {
    	    return true;
    	}
    	i = _counters[i];
    	n++;

    	if (n == _counters.size()) {
    	    dump();
    	    //abort();
    	}
    }
    return false;
}

void
ref_counter_pool::dump()
{
    for (size_t i = 0; i < _counters.size(); i++) {
	   cout << i << " " << _counters[i] << endl;
    }
    cout << "Free index: " << _free_index << endl;
    cout << "Balance: " << _balance << endl;
}

ref_counter_pool::ref_counter_pool()
{
    const size_t n = 1;
    _counters.resize(n);
    //wbnote20150518: only _countoers[0] == LAST_FREE ?
    //because the index is used from the last to the first
    _counters[n - 1] = LAST_FREE;     
    _free_index = 0;

    grow();
    grow();
}

int
ref_counter_pool::new_counter()
{
    if (_counters[_free_index] == LAST_FREE) {
	   grow();
    }
    int new_counter = _free_index;
    _free_index = _counters[_free_index];
    _counters[new_counter] = 1;
    ++_balance;
    return new_counter;
}

int
ref_counter_pool::incr_counter(int index)
{
    assert((size_t)index < _counters.size());
    ++_counters[index];
    ++_balance;
    return _counters[index];
}

int
ref_counter_pool::decr_counter(int index)
{
    int c = --_counters[index];
    --_balance;
    if (c == 0) {
    	/* recycle */
    	_counters[index] = _free_index;
    	_free_index = index;
    }
    assert(c >= 0);
    return c;
}

int
ref_counter_pool::count(int index)
{
    return _counters[index];
}