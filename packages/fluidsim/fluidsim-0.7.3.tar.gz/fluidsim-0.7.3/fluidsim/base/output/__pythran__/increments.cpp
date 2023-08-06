#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/int32.hpp>
#include <pythonic/include/types/bool.hpp>
#include <pythonic/include/types/numpy_texpr.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/numpy_texpr.hpp>
#include <pythonic/types/int32.hpp>
#include <pythonic/include/builtins/abs.hpp>
#include <pythonic/include/builtins/getattr.hpp>
#include <pythonic/include/builtins/range.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/numpy/empty.hpp>
#include <pythonic/include/numpy/sum.hpp>
#include <pythonic/include/operator_/mul.hpp>
#include <pythonic/include/operator_/pow.hpp>
#include <pythonic/include/operator_/sub.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/abs.hpp>
#include <pythonic/builtins/getattr.hpp>
#include <pythonic/builtins/range.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/numpy/empty.hpp>
#include <pythonic/numpy/sum.hpp>
#include <pythonic/operator_/mul.hpp>
#include <pythonic/operator_/pow.hpp>
#include <pythonic/operator_/sub.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
  namespace __pythran_increments
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
    struct strfunc_from_pdf
    {
      typedef void callable;
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 = bool>
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type0;
        typedef __type0 __type1;
        typedef __type1 __type2;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::empty{})>::type>::type __type3;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type4;
        typedef __type4 __type5;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type5>())) __type6;
        typedef decltype(std::declval<__type3>()(std::declval<__type6>())) __type7;
        typedef typename pythonic::assignable<__type7>::type __type8;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type9;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SIZE{}, std::declval<__type5>())) __type11;
        typedef decltype(std::declval<__type9>()(std::declval<__type11>())) __type12;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type12>::type::iterator>::value_type>::type __type13;
        typedef __type13 __type14;
        typedef indexable<__type14> __type15;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::abs{})>::type>::type __type16;
        typedef typename pythonic::assignable<__type1>::type __type17;
        typedef __type17 __type18;
        typedef decltype(std::declval<__type16>()(std::declval<__type18>())) __type19;
        typedef typename pythonic::assignable<__type19>::type __type20;
        typedef typename __combined<__type17,__type20>::type __type21;
        typedef __type21 __type22;
        typedef decltype(pythonic::types::as_const(std::declval<__type22>())) __type23;
        typedef long __type25;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type14>(), std::declval<__type25>())) __type26;
        typedef decltype(std::declval<__type23>()[std::declval<__type26>()]) __type27;
        typedef decltype(pythonic::operator_::sub(std::declval<__type27>(), std::declval<__type27>())) __type33;
        typedef decltype(std::declval<__type16>()(std::declval<__type33>())) __type34;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::sum{})>::type>::type __type35;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type36;
        typedef __type36 __type37;
        typedef decltype(pythonic::types::as_const(std::declval<__type37>())) __type38;
        typedef decltype(std::declval<__type38>()[std::declval<__type14>()]) __type40;
        typedef decltype(std::declval<__type23>()[std::declval<__type14>()]) __type44;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type45;
        typedef __type45 __type46;
        typedef decltype(pythonic::builtins::pow(std::declval<__type44>(), std::declval<__type46>())) __type47;
        typedef decltype(pythonic::operator_::mul(std::declval<__type40>(), std::declval<__type47>())) __type48;
        typedef decltype(std::declval<__type35>()(std::declval<__type48>())) __type49;
        typedef decltype(pythonic::operator_::mul(std::declval<__type34>(), std::declval<__type49>())) __type50;
        typedef container<typename std::remove_reference<__type50>::type> __type51;
        typedef typename __combined<__type8,__type15,__type51>::type __type52;
        typedef __type52 __type53;
        typedef typename pythonic::returnable<__type53>::type __type54;
        typedef __type2 __ptype0;
        typedef __type54 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 = bool>
      inline
      typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type operator()(argument_type0 rxs, argument_type1 pdf, argument_type2 values, argument_type3 order, argument_type4 absolute= false) const
      ;
    }  ;
    inline
    typename __transonic__::type::result_type __transonic__::operator()() const
    {
      {
        static typename __transonic__::type::result_type tmp_global = pythonic::types::make_tuple(pythonic::types::str("0.5.2.post0"));
        return tmp_global;
      }
    }
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 >
    inline
    typename strfunc_from_pdf::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type strfunc_from_pdf::operator()(argument_type0 rxs, argument_type1 pdf, argument_type2 values, argument_type3 order, argument_type4 absolute) const
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type0;
      typedef __type0 __type1;
      typedef typename pythonic::assignable<__type1>::type __type2;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::abs{})>::type>::type __type3;
      typedef __type2 __type4;
      typedef decltype(std::declval<__type3>()(std::declval<__type4>())) __type5;
      typedef typename pythonic::assignable<__type5>::type __type6;
      typedef typename __combined<__type2,__type6>::type __type7;
      typedef typename pythonic::assignable<__type7>::type __type8;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::empty{})>::type>::type __type9;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type10;
      typedef __type10 __type11;
      typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type11>())) __type12;
      typedef decltype(std::declval<__type9>()(std::declval<__type12>())) __type13;
      typedef typename pythonic::assignable<__type13>::type __type14;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type15;
      typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SIZE{}, std::declval<__type11>())) __type17;
      typedef decltype(std::declval<__type15>()(std::declval<__type17>())) __type18;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type18>::type::iterator>::value_type>::type __type19;
      typedef __type19 __type20;
      typedef indexable<__type20> __type21;
      typedef __type7 __type22;
      typedef decltype(pythonic::types::as_const(std::declval<__type22>())) __type23;
      typedef long __type25;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type20>(), std::declval<__type25>())) __type26;
      typedef decltype(std::declval<__type23>()[std::declval<__type26>()]) __type27;
      typedef decltype(pythonic::operator_::sub(std::declval<__type27>(), std::declval<__type27>())) __type33;
      typedef decltype(std::declval<__type3>()(std::declval<__type33>())) __type34;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::sum{})>::type>::type __type35;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type36;
      typedef __type36 __type37;
      typedef decltype(pythonic::types::as_const(std::declval<__type37>())) __type38;
      typedef decltype(std::declval<__type38>()[std::declval<__type20>()]) __type40;
      typedef decltype(std::declval<__type23>()[std::declval<__type20>()]) __type44;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type45;
      typedef __type45 __type46;
      typedef decltype(pythonic::builtins::pow(std::declval<__type44>(), std::declval<__type46>())) __type47;
      typedef decltype(pythonic::operator_::mul(std::declval<__type40>(), std::declval<__type47>())) __type48;
      typedef decltype(std::declval<__type35>()(std::declval<__type48>())) __type49;
      typedef decltype(pythonic::operator_::mul(std::declval<__type34>(), std::declval<__type49>())) __type50;
      typedef container<typename std::remove_reference<__type50>::type> __type51;
      typedef typename __combined<__type14,__type21,__type51>::type __type52;
      typedef typename pythonic::assignable<__type52>::type __type53;
      __type8 values_ = values;
      __type53 S_order = pythonic::numpy::functor::empty{}(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, rxs));
      if (absolute)
      {
        values_ = pythonic::builtins::functor::abs{}(values_);
      }
      {
        long  __target139658376662224 = pythonic::builtins::getattr(pythonic::types::attr::SIZE{}, rxs);
        for (long  irx=0L; irx < __target139658376662224; irx += 1L)
        {
          S_order.fast(irx) = pythonic::operator_::mul(pythonic::builtins::functor::abs{}(pythonic::operator_::sub(pythonic::types::as_const(values_).fast(pythonic::types::make_tuple(irx, 1L)), pythonic::types::as_const(values_).fast(pythonic::types::make_tuple(irx, 0L)))), pythonic::numpy::functor::sum{}(pythonic::operator_::mul(pythonic::types::as_const(pdf).fast(irx), pythonic::builtins::pow(pythonic::types::as_const(values_).fast(irx), order))));
        }
      }
      return S_order;
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_increments::__transonic__()());
inline
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double, bool>::result_type strfunc_from_pdf0(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& pdf, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& values, double&& order, bool&& absolute) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order, absolute);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double, bool>::result_type strfunc_from_pdf1(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& pdf, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& values, double&& order, bool&& absolute) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order, absolute);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double, bool>::result_type strfunc_from_pdf2(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& pdf, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& values, double&& order, bool&& absolute) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order, absolute);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double, bool>::result_type strfunc_from_pdf3(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& pdf, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& values, double&& order, bool&& absolute) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order, absolute);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type strfunc_from_pdf4(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& pdf, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& values, double&& order) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type strfunc_from_pdf5(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& pdf, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& values, double&& order) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type strfunc_from_pdf6(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& pdf, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& values, double&& order) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order);
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
typename __pythran_increments::strfunc_from_pdf::type<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type strfunc_from_pdf7(pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>&& rxs, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& pdf, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& values, double&& order) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_increments::strfunc_from_pdf()(rxs, pdf, values, order);
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
__pythran_wrap_strfunc_from_pdf0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order", "absolute",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<double>(args_obj[3]) && is_convertible<bool>(args_obj[4]))
        return to_python(strfunc_from_pdf0(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<double>(args_obj[3]), from_python<bool>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order", "absolute",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<double>(args_obj[3]) && is_convertible<bool>(args_obj[4]))
        return to_python(strfunc_from_pdf1(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<double>(args_obj[3]), from_python<bool>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order", "absolute",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<double>(args_obj[3]) && is_convertible<bool>(args_obj[4]))
        return to_python(strfunc_from_pdf2(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<double>(args_obj[3]), from_python<bool>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order", "absolute",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<double>(args_obj[3]) && is_convertible<bool>(args_obj[4]))
        return to_python(strfunc_from_pdf3(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<double>(args_obj[3]), from_python<bool>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(strfunc_from_pdf4(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(strfunc_from_pdf5(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(strfunc_from_pdf6(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_strfunc_from_pdf7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"rxs", "pdf", "values", "order",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(strfunc_from_pdf7(from_python<pythonic::types::ndarray<npy_int32,pythonic::types::pshape<long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_strfunc_from_pdf(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_strfunc_from_pdf0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_strfunc_from_pdf7(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "strfunc_from_pdf", "\n""    - strfunc_from_pdf(int32[:], float64[:,:], float64[:,:], float64, bool)\n""    - strfunc_from_pdf(int32[:], float64[:,:], float64[:,:], float64)", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "strfunc_from_pdf",
    (PyCFunction)__pythran_wrapall_strfunc_from_pdf,
    METH_VARARGS | METH_KEYWORDS,
    "Compute structure function of specified order from pdf\n""\n""    Supported prototypes:\n""\n""    - strfunc_from_pdf(int32[:], float64[:,:], float64[:,:], float64, bool)\n""    - strfunc_from_pdf(int32[:], float64[:,:], float64[:,:], float64)"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "increments",            /* m_name */
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
PYTHRAN_MODULE_INIT(increments)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
#if defined(GNUC) && !defined(__clang__)
__attribute__ ((externally_visible))
#endif
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(increments)(void) {
    import_array()
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("increments",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.13.1",
                                      "2023-05-24 11:29:39.298951",
                                      "73194a1181a3d795a9e99319b62f4bb2efdd40dc09f9ed476112ee2672957415");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif