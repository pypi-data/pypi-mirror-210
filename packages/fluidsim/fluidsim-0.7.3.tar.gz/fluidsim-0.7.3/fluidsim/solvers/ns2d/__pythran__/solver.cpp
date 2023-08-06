#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/numpy_texpr.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/numpy_texpr.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/operator_/add.hpp>
#include <pythonic/include/operator_/eq.hpp>
#include <pythonic/include/operator_/mul.hpp>
#include <pythonic/include/operator_/neg.hpp>
#include <pythonic/include/operator_/sub.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/operator_/add.hpp>
#include <pythonic/operator_/eq.hpp>
#include <pythonic/operator_/mul.hpp>
#include <pythonic/operator_/neg.hpp>
#include <pythonic/operator_/sub.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
  namespace __pythran_solver
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
    struct compute_Frot
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 = long>
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
        typedef __type0 __type1;
        typedef decltype(pythonic::operator_::neg(std::declval<__type1>())) __type2;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type3;
        typedef __type3 __type4;
        typedef decltype(pythonic::operator_::mul(std::declval<__type2>(), std::declval<__type4>())) __type5;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type6;
        typedef __type6 __type7;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type8;
        typedef __type8 __type9;
        typedef decltype(pythonic::operator_::mul(std::declval<__type7>(), std::declval<__type9>())) __type10;
        typedef decltype(pythonic::operator_::sub(std::declval<__type5>(), std::declval<__type10>())) __type11;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type18;
        typedef __type18 __type19;
        typedef decltype(pythonic::operator_::add(std::declval<__type9>(), std::declval<__type19>())) __type20;
        typedef decltype(pythonic::operator_::mul(std::declval<__type7>(), std::declval<__type20>())) __type21;
        typedef decltype(pythonic::operator_::sub(std::declval<__type5>(), std::declval<__type21>())) __type22;
        typedef typename __combined<__type11,__type22>::type __type23;
        typedef typename pythonic::returnable<__type23>::type __type24;
        typedef __type24 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 = long>
      inline
      typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type operator()(argument_type0 ux, argument_type1 uy, argument_type2 px_rot, argument_type3 py_rot, argument_type4 beta= 0L) const
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
    typename compute_Frot::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4>::result_type compute_Frot::operator()(argument_type0 ux, argument_type1 uy, argument_type2 px_rot, argument_type3 py_rot, argument_type4 beta) const
    {
      if (pythonic::operator_::eq(beta, 0L))
      {
        return pythonic::operator_::sub(pythonic::operator_::mul(pythonic::operator_::neg(ux), px_rot), pythonic::operator_::mul(uy, py_rot));
      }
      else
      {
        return pythonic::operator_::sub(pythonic::operator_::mul(pythonic::operator_::neg(ux), px_rot), pythonic::operator_::mul(uy, pythonic::operator_::add(py_rot, beta)));
      }
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_solver::__transonic__()());
inline
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot0(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot1(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot2(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot3(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot4(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot5(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot6(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot7(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot8(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot9(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot10(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot11(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot12(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot13(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double>::result_type compute_Frot14(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double>::result_type compute_Frot15(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot, double&& beta) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot, beta);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot16(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot17(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot18(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot19(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot20(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot21(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot22(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot23(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot24(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot25(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot26(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot27(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot28(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot29(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type compute_Frot30(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
typename __pythran_solver::compute_Frot::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type compute_Frot31(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& ux, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& uy, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& px_rot, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& py_rot) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_solver::compute_Frot()(ux, uy, px_rot, py_rot);
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
__pythran_wrap_compute_Frot0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot1(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot2(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot3(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot4(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot4(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot5(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot5(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot6(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot6(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot7(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot7(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot8(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot8(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot9(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot9(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot10(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot10(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot11(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot11(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot12(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot12(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot13(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot13(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot14(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot14(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot15(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[5+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot", "beta",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]) && is_convertible<double>(args_obj[4]))
        return to_python(compute_Frot15(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]), from_python<double>(args_obj[4])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot16(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot16(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot17(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot17(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot18(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot18(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot19(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot19(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot20(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot20(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot21(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot21(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot22(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot22(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot23(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot23(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot24(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot24(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot25(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot25(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot26(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot26(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot27(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot27(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot28(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot28(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot29(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot29(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot30(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3]))
        return to_python(compute_Frot30(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_Frot31(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"ux", "uy", "px_rot", "py_rot",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3]))
        return to_python(compute_Frot31(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[2]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[3])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_compute_Frot(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_compute_Frot0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot3(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot4(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot5(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot6(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot7(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot8(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot9(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot10(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot11(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot12(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot13(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot14(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot15(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot16(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot17(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot18(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot19(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot20(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot21(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot22(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot23(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot24(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot25(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot26(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot27(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot28(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot29(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot30(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_Frot31(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "compute_Frot", "\n""    - compute_Frot(float64[:,:], float64[:,:], float64[:,:], float64[:,:], float64)\n""    - compute_Frot(float64[:,:], float64[:,:], float64[:,:], float64[:,:])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "compute_Frot",
    (PyCFunction)__pythran_wrapall_compute_Frot,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n""\n""    - compute_Frot(float64[:,:], float64[:,:], float64[:,:], float64[:,:], float64)\n""    - compute_Frot(float64[:,:], float64[:,:], float64[:,:], float64[:,:])"},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "solver",            /* m_name */
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
PYTHRAN_MODULE_INIT(solver)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
#if defined(GNUC) && !defined(__clang__)
__attribute__ ((externally_visible))
#endif
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(solver)(void) {
    import_array()
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("solver",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.13.1",
                                      "2023-05-24 11:29:42.367898",
                                      "2a1ac2a4e88e1a9f4787b1559a937c9cadca577f2353acff17b685dc1a078679");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif