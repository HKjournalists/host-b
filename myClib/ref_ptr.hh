
//#ifndef __REF_PTR_HH__
//#define __REF_PTR_HH__

#include <vector>
#include <list>
#include <assert.h>


using namespace std;
/**
 * @short class for maintaining the storage of counters used by ref_ptr.
 *
 * The ref_counter_pool is a singleton class that maintains the counters
 * for all ref_ptr objects.  The counters are maintained in a vector.  This
 * class is used by ref_ptr and not intended any other purpose.
 */
class ref_counter_pool
{
private:
    vector<int> _counters;  //when in use , _counters[i] is the counter, otherwise,  _counters[i] is the next _free_index
    int	    _free_index;  //the index of vector that can be use for counter
    int	    _balance;	//what's the meaning of this variable?

    static const int LAST_FREE = -1;
    static ref_counter_pool _the_instance;

    /**
     * Expand counter storage.
     */
    void grow();

public:
    /**
     * Create a new counter.
     * @return index associated with counter.
     */
    int new_counter();

    /**
     * Increment the count associated with counter by 1.
     * @param index the counter to increment.
     */
    int incr_counter(int index);

    /**
     * Decrement the count associated with counter by 1.
     * @param index the counter to decrement.
     */
    int decr_counter(int index);

    /**
     * Get the count associated with counter.
     * @param index of the counter to query.
     * @return the counter value.
     */
    int count(int index);

    /**
     * Recycle counter.  Places counter on free-list.
     * @param index of the counter to recycle.
     */
    void recycle(int index);

    /**
     * Dumps counter info to stdout.  Debugging function.
     */
    void dump();

    /**
     * Sanity check internal data structure.  Debugging function.
     */
    void check();

    /**
     * Check index is on free list.
     */
    bool on_free_list(int index);

    /**
     * Return number of valid ref pointer entries in pool.
     */
    int balance() const { return _balance; }

    /**
     * @return singleton ref_counter_pool.
     */
    static ref_counter_pool& instance();

    ref_counter_pool();
};

/**
 * @short Reference Counted Pointer Class.
 *
 * The ref_ptr class is a strong reference class.  It maintains a count of
 * how many references to an object exist and releases the memory associated
 * with the object when the reference count reaches zero.  The reference
 * pointer can be dereferenced like an ordinary pointer to call methods
 * on the reference counted object.
 *
 * At the time of writing the only supported memory management is
 * through the new and delete operators.  At a future date, this class
 * should support the STL allocator classes or an equivalent to
 * provide greater flexibility.
 */
template <class _Tp>
class ref_ptr {
public:
    /**
     * Construct a reference pointer for object.
     *
     * @param p pointer to object to be reference counted.  p must be
     * allocated using operator new as it will be destructed using delete
     * when the reference count reaches zero.
     */
    ref_ptr(_Tp* __p = 0)
        : _M_ptr(__p), _M_index(0)
    {
	if (_M_ptr)
	    _M_index = ref_counter_pool::instance().new_counter();
    }

    /**
     * Copy Constructor
     *
     * Constructs a reference pointer for object.  Raises reference count
     * associated with object by 1.
     */
    ref_ptr(const ref_ptr& __r)
        : _M_ptr(0), _M_index(-1) {
        ref(&__r);
    }

    /**
     * Assignment Operator
     *
     * Assigns reference pointer to new object.
     */
    ref_ptr& operator=(const ref_ptr& __r) {
        if (&__r != this) {
            unref();
            ref(&__r);
        }
        return *this;
    }

    /**
     * Destruct reference pointer instance and lower reference count on
     * object being tracked.  The object being tracked will be deleted if
     * the reference count falls to zero because of the destruction of the
     * reference pointer.
     */
    ~ref_ptr() {
        unref();
    }

    /**
     * Dereference reference counted object.
     * @return reference to object.
     */
    _Tp& operator*() const { return *_M_ptr; }

    /**
     * Dereference pointer to reference counted object.
     * @return pointer to object.
     */
    _Tp* operator->() const { return _M_ptr; }

    /**
     * Dereference pointer to reference counted object.
     * @return pointer to object.
     */
    _Tp* get() const { return _M_ptr; }

    /**
     * Equality Operator
     * @return true if reference pointers refer to same object.
     */
    bool operator==(const ref_ptr& rp) const { return _M_ptr == rp._M_ptr; }

    /**
     * Check if reference pointer refers to an object or whether it has
     * been assigned a null object.
     * @return true if reference pointer refers to a null object.
     */
    bool is_empty() const { return _M_ptr == 0; }

    /**
     * @return true if reference pointer represents only reference to object.
     */
    bool is_only() const {
	return ref_counter_pool::instance().count(_M_index) == 1;
    }

    /**
     * @param n minimum count.
     * @return true if there are at least n references to object.
     */
    bool at_least(int n) const {
	return ref_counter_pool::instance().count(_M_index) >= n;
    }

    /**
     * Release reference on object.  The reference pointers underlying
     * object is set to null, and the former object is destructed if
     * necessary.
     */
    void release() const { unref(); }

    ref_ptr(_Tp* data, int index) : _M_ptr(data), _M_index(index)
    {
	ref_counter_pool::instance().incr_counter(_M_index);
    }

protected:

    /**
     * Add reference.
     */
    void ref(const ref_ptr* __r) const {
	_M_ptr = __r->_M_ptr;
	_M_index = __r->_M_index;
	if (_M_ptr) {
	    ref_counter_pool::instance().incr_counter(_M_index);
	}
    }

    /**
     * Remove reference.
     */
    void unref() const {
	if (_M_ptr &&
	    ref_counter_pool::instance().decr_counter(_M_index) == 0) {
	    delete _M_ptr;
	}
	_M_ptr = 0;
    }

    mutable _Tp* _M_ptr;
    mutable int _M_index;	// index in ref_counter_pool
};



//#endif // __REF_PTR_HH__
