#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float32.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/float64.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/float32.hpp>
#include <pythonic/include/builtins/ValueError.hpp>
#include <pythonic/include/builtins/enumerate.hpp>
#include <pythonic/include/builtins/len.hpp>
#include <pythonic/include/builtins/print.hpp>
#include <pythonic/include/builtins/str/__mod__.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/numpy/arange.hpp>
#include <pythonic/include/operator_/ge.hpp>
#include <pythonic/include/operator_/gt.hpp>
#include <pythonic/include/operator_/le.hpp>
#include <pythonic/include/operator_/lt.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/ValueError.hpp>
#include <pythonic/builtins/enumerate.hpp>
#include <pythonic/builtins/len.hpp>
#include <pythonic/builtins/print.hpp>
#include <pythonic/builtins/str/__mod__.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/numpy/arange.hpp>
#include <pythonic/operator_/ge.hpp>
#include <pythonic/operator_/gt.hpp>
#include <pythonic/operator_/le.hpp>
#include <pythonic/operator_/lt.hpp>
#include <pythonic/types/str.hpp>
namespace __pythran_spatiotemporal_spectra
{
  struct __transonic__
  {
    typedef void callable;
    typedef void pure;
    struct type
    {
      typedef pythonic::types::str __type0;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type0>())) __type1;
      typedef typename pythonic::returnable<__type1>::type __type2;
      typedef __type2 result_type;
    }  ;
    inline
    typename type::result_type operator()() const;
    ;
  }  ;
  struct find_index_first_l
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::enumerate{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
      typedef __type1 __type2;
      typedef decltype(std::declval<__type0>()(std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type3>::type::iterator>::value_type>::type __type4;
      typedef __type4 __type5;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type5>::type>::type __type6;
      typedef typename pythonic::returnable<__type6>::type __type7;
      typedef __type7 result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& arr, argument_type1&& value) const
    ;
  }  ;
  struct find_index_first_g
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::enumerate{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
      typedef __type1 __type2;
      typedef decltype(std::declval<__type0>()(std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type3>::type::iterator>::value_type>::type __type4;
      typedef __type4 __type5;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type5>::type>::type __type6;
      typedef typename pythonic::returnable<__type6>::type __type7;
      typedef __type7 result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& arr, argument_type1&& value) const
    ;
  }  ;
  struct find_index_first_geq
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::enumerate{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type1;
      typedef __type1 __type2;
      typedef decltype(std::declval<__type0>()(std::declval<__type2>())) __type3;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type3>::type::iterator>::value_type>::type __type4;
      typedef __type4 __type5;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type5>::type>::type __type6;
      typedef typename pythonic::returnable<__type6>::type __type7;
      typedef __type7 result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename type<argument_type0, argument_type1>::result_type operator()(argument_type0&& arr, argument_type1&& value) const
    ;
  }  ;
  struct get_arange_minmax
  {
    typedef void callable;
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    struct type
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::arange{})>::type>::type __type0;
      typedef long __type1;
      typedef typename pythonic::assignable<__type1>::type __type2;
      typedef find_index_first_geq __type3;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type4;
      typedef __type4 __type5;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type6;
      typedef __type6 __type7;
      typedef decltype(std::declval<__type3>()(std::declval<__type5>(), std::declval<__type7>())) __type8;
      typedef typename pythonic::assignable<__type8>::type __type9;
      typedef typename __combined<__type2,__type9>::type __type10;
      typedef __type10 __type11;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type12;
      typedef decltype(std::declval<__type12>()(std::declval<__type5>())) __type14;
      typedef typename pythonic::assignable<__type14>::type __type15;
      typedef find_index_first_g __type16;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type18;
      typedef __type18 __type19;
      typedef decltype(std::declval<__type16>()(std::declval<__type5>(), std::declval<__type19>())) __type20;
      typedef typename pythonic::assignable<__type20>::type __type21;
      typedef typename __combined<__type15,__type21>::type __type22;
      typedef __type22 __type23;
      typedef decltype(std::declval<__type0>()(std::declval<__type11>(), std::declval<__type23>())) __type24;
      typedef typename pythonic::returnable<__type24>::type __type25;
      typedef __type25 result_type;
    }  
    ;
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    inline
    typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0&& times, argument_type1&& tmin, argument_type2&& tmax) const
    ;
  }  ;
  inline
  typename __transonic__::type::result_type __transonic__::operator()() const
  {
    {
      static typename __transonic__::type::result_type tmp_global = pythonic::types::make_tuple(pythonic::types::str("0.5.1"));
      return tmp_global;
    }
  }
  template <typename argument_type0 , typename argument_type1 >
  inline
  typename find_index_first_l::type<argument_type0, argument_type1>::result_type find_index_first_l::operator()(argument_type0&& arr, argument_type1&& value) const
  {
    {
      for (auto&& __tuple0: pythonic::builtins::functor::enumerate{}(arr))
      {
        if (pythonic::operator_::lt(std::get<1>(__tuple0), value))
        {
          return std::get<0>(__tuple0);
        }
      }
    }
    pythonic::builtins::functor::print{}(pythonic::types::str("arr"), arr);
    throw pythonic::builtins::functor::ValueError{}(pythonic::builtins::str::functor::__mod__{}(pythonic::types::str("No index such that `arr[index] >= value (=%.8g)`"), pythonic::types::make_tuple(value)));
  }
  template <typename argument_type0 , typename argument_type1 >
  inline
  typename find_index_first_g::type<argument_type0, argument_type1>::result_type find_index_first_g::operator()(argument_type0&& arr, argument_type1&& value) const
  {
    {
      for (auto&& __tuple0: pythonic::builtins::functor::enumerate{}(arr))
      {
        if (pythonic::operator_::gt(std::get<1>(__tuple0), value))
        {
          return std::get<0>(__tuple0);
        }
      }
    }
    pythonic::builtins::functor::print{}(pythonic::types::str("arr"), arr);
    throw pythonic::builtins::functor::ValueError{}(pythonic::builtins::str::functor::__mod__{}(pythonic::types::str("No index such that `arr[index] >= value (=%.8g)`"), pythonic::types::make_tuple(value)));
  }
  template <typename argument_type0 , typename argument_type1 >
  inline
  typename find_index_first_geq::type<argument_type0, argument_type1>::result_type find_index_first_geq::operator()(argument_type0&& arr, argument_type1&& value) const
  {
    {
      for (auto&& __tuple0: pythonic::builtins::functor::enumerate{}(arr))
      {
        if (pythonic::operator_::ge(std::get<1>(__tuple0), value))
        {
          return std::get<0>(__tuple0);
        }
      }
    }
    pythonic::builtins::functor::print{}(pythonic::types::str("arr"), arr);
    throw pythonic::builtins::functor::ValueError{}(pythonic::builtins::str::functor::__mod__{}(pythonic::types::str("No index such that `arr[index] >= value (=%.8g)`"), pythonic::types::make_tuple(value)));
  }
  template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
  inline
  typename get_arange_minmax::type<argument_type0, argument_type1, argument_type2>::result_type get_arange_minmax::operator()(argument_type0&& times, argument_type1&& tmin, argument_type2&& tmax) const
  {
    typedef long __type0;
    typedef typename pythonic::assignable<__type0>::type __type1;
    typedef find_index_first_geq __type2;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type3;
    typedef __type3 __type4;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
    typedef __type5 __type6;
    typedef decltype(std::declval<__type2>()(std::declval<__type4>(), std::declval<__type6>())) __type7;
    typedef typename pythonic::assignable<__type7>::type __type8;
    typedef typename __combined<__type1,__type8>::type __type9;
    typedef typename pythonic::assignable<__type9>::type __type10;
    typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type11;
    typedef decltype(std::declval<__type11>()(std::declval<__type4>())) __type13;
    typedef typename pythonic::assignable<__type13>::type __type14;
    typedef find_index_first_g __type15;
    typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type17;
    typedef __type17 __type18;
    typedef decltype(std::declval<__type15>()(std::declval<__type4>(), std::declval<__type18>())) __type19;
    typedef typename pythonic::assignable<__type19>::type __type20;
    typedef typename __combined<__type14,__type20>::type __type21;
    typedef typename pythonic::assignable<__type21>::type __type22;
    __type10 start;
    __type22 stop;
    if (pythonic::operator_::le(tmin, std::get<0>(times)))
    {
      start = 0L;
    }
    else
    {
      start = find_index_first_geq()(times, tmin);
    }
    if (pythonic::operator_::ge(tmax, times[-1L]))
    {
      stop = pythonic::builtins::functor::len{}(times);
    }
    else
    {
      stop = find_index_first_g()(times, tmax);
    }
    return pythonic::numpy::functor::arange{}(start, stop);
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_spatiotemporal_spectra::__transonic__()());
inline
typename __pythran_spatiotemporal_spectra::get_arange_minmax::type<pythonic::types::ndarray<double,pythonic::types::pshape<long>>, double, double>::result_type get_arange_minmax0(pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& times, double&& tmin, double&& tmax) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::get_arange_minmax()(times, tmin, tmax);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::get_arange_minmax::type<pythonic::types::ndarray<float,pythonic::types::pshape<long>>, float, float>::result_type get_arange_minmax1(pythonic::types::ndarray<float,pythonic::types::pshape<long>>&& times, float&& tmin, float&& tmax) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::get_arange_minmax()(times, tmin, tmax);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_l::type<pythonic::types::ndarray<double,pythonic::types::pshape<long>>, double>::result_type find_index_first_l0(pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& arr, double&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_l()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_l::type<pythonic::types::ndarray<float,pythonic::types::pshape<long>>, float>::result_type find_index_first_l1(pythonic::types::ndarray<float,pythonic::types::pshape<long>>&& arr, float&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_l()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_g::type<pythonic::types::ndarray<double,pythonic::types::pshape<long>>, double>::result_type find_index_first_g0(pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& arr, double&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_g()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_g::type<pythonic::types::ndarray<float,pythonic::types::pshape<long>>, float>::result_type find_index_first_g1(pythonic::types::ndarray<float,pythonic::types::pshape<long>>&& arr, float&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_g()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_geq::type<pythonic::types::ndarray<double,pythonic::types::pshape<long>>, double>::result_type find_index_first_geq0(pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& arr, double&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_geq()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
inline
typename __pythran_spatiotemporal_spectra::find_index_first_geq::type<pythonic::types::ndarray<float,pythonic::types::pshape<long>>, float>::result_type find_index_first_geq1(pythonic::types::ndarray<float,pythonic::types::pshape<long>>&& arr, float&& value) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::find_index_first_geq()(arr, value);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}

static PyObject *
__pythran_wrap_get_arange_minmax0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"times", "tmin", "tmax",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<double>(args_obj[1]) && is_convertible<double>(args_obj[2]))
        return to_python(get_arange_minmax0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]), from_python<double>(args_obj[1]), from_python<double>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_get_arange_minmax1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"times", "tmin", "tmax",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<float>(args_obj[1]) && is_convertible<float>(args_obj[2]))
        return to_python(get_arange_minmax1(from_python<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]), from_python<float>(args_obj[1]), from_python<float>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_l0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<double>(args_obj[1]))
        return to_python(find_index_first_l0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]), from_python<double>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_l1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<float>(args_obj[1]))
        return to_python(find_index_first_l1(from_python<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]), from_python<float>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_g0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<double>(args_obj[1]))
        return to_python(find_index_first_g0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]), from_python<double>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_g1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<float>(args_obj[1]))
        return to_python(find_index_first_g1(from_python<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]), from_python<float>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_geq0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<double>(args_obj[1]))
        return to_python(find_index_first_geq0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[0]), from_python<double>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_find_index_first_geq1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"arr", "value",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<float>(args_obj[1]))
        return to_python(find_index_first_geq1(from_python<pythonic::types::ndarray<float,pythonic::types::pshape<long>>>(args_obj[0]), from_python<float>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_get_arange_minmax(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_get_arange_minmax0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_get_arange_minmax1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "get_arange_minmax", "\n""    - get_arange_minmax(float64[:], float64, float64)\n""    - get_arange_minmax(float32[:], float32, float32)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_find_index_first_l(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_find_index_first_l0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_find_index_first_l1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "find_index_first_l", "\n""    - find_index_first_l(float64[:], float64)\n""    - find_index_first_l(float32[:], float32)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_find_index_first_g(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_find_index_first_g0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_find_index_first_g1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "find_index_first_g", "\n""    - find_index_first_g(float64[:], float64)\n""    - find_index_first_g(float32[:], float32)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_find_index_first_geq(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_find_index_first_geq0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_find_index_first_geq1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "find_index_first_geq", "\n""    - find_index_first_geq(float64[:], float64)\n""    - find_index_first_geq(float32[:], float32)", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "get_arange_minmax",
    (PyCFunction)__pythran_wrapall_get_arange_minmax,
    METH_VARARGS | METH_KEYWORDS,
    "get a range of index for which `tmin <= times[i] <= tmax`\n""\n""    Supported prototypes:\n""\n""    - get_arange_minmax(float64[:], float64, float64)\n""    - get_arange_minmax(float32[:], float32, float32)\n""\n""    This assumes that `times` is sorted.\n""\n"""},{
    "find_index_first_l",
    (PyCFunction)__pythran_wrapall_find_index_first_l,
    METH_VARARGS | METH_KEYWORDS,
    "find the first index such that `arr[index] < value`\n""\n""    Supported prototypes:\n""\n""    - find_index_first_l(float64[:], float64)\n""    - find_index_first_l(float32[:], float32)"},{
    "find_index_first_g",
    (PyCFunction)__pythran_wrapall_find_index_first_g,
    METH_VARARGS | METH_KEYWORDS,
    "find the first index such that `arr[index] > value`\n""\n""    Supported prototypes:\n""\n""    - find_index_first_g(float64[:], float64)\n""    - find_index_first_g(float32[:], float32)"},{
    "find_index_first_geq",
    (PyCFunction)__pythran_wrapall_find_index_first_geq,
    METH_VARARGS | METH_KEYWORDS,
    "find the first index such that `arr[index] >= value`\n""\n""    Supported prototypes:\n""\n""    - find_index_first_geq(float64[:], float64)\n""    - find_index_first_geq(float32[:], float32)"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "spatiotemporal_spectra",            /* m_name */
    "",         /* m_doc */
    -1,                  /* m_size */
    Methods,             /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#define PYTHRAN_RETURN return theModule
#define PYTHRAN_MODULE_INIT(s) PyInit_##s
#else
#define PYTHRAN_RETURN return
#define PYTHRAN_MODULE_INIT(s) init##s
#endif
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(spatiotemporal_spectra)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
#if defined(GNUC) && !defined(__clang__)
__attribute__ ((externally_visible))
#endif
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(spatiotemporal_spectra)(void) {
    import_array()
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("spatiotemporal_spectra",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.12.0",
                                      "2022-11-30 15:27:57.545072",
                                      "71c4583a576e4b24f7e61ffcddbbc62d4d9c4bea9965d1a05aa42fd10e38f89a");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif