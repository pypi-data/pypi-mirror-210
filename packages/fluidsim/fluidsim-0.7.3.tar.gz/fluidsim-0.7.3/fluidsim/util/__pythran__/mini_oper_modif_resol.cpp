#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/complex128.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/complex128.hpp>
#include <pythonic/include/builtins/None.hpp>
#include <pythonic/include/builtins/getattr.hpp>
#include <pythonic/include/builtins/min.hpp>
#include <pythonic/include/builtins/pythran/and_.hpp>
#include <pythonic/include/builtins/range.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/operator_/add.hpp>
#include <pythonic/include/operator_/floordiv.hpp>
#include <pythonic/include/operator_/gt.hpp>
#include <pythonic/include/operator_/lt.hpp>
#include <pythonic/include/operator_/neg.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/None.hpp>
#include <pythonic/builtins/getattr.hpp>
#include <pythonic/builtins/min.hpp>
#include <pythonic/builtins/pythran/and_.hpp>
#include <pythonic/builtins/range.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/operator_/add.hpp>
#include <pythonic/operator_/floordiv.hpp>
#include <pythonic/operator_/gt.hpp>
#include <pythonic/operator_/lt.hpp>
#include <pythonic/operator_/neg.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
  namespace __pythran_mini_oper_modif_resol
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
    struct fill_field_fft_3d
    {
      typedef void callable;
      ;
      template <typename argument_type0 , typename argument_type1 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
        typedef __type0 __type1;
        typedef decltype(pythonic::types::as_const(std::declval<__type1>())) __type2;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type3;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::min{})>::type>::type __type4;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type5;
        typedef __type5 __type6;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type6>())) __type7;
        typedef decltype(pythonic::types::as_const(std::declval<__type7>())) __type8;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type8>::type>::type __type9;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type1>())) __type11;
        typedef decltype(pythonic::types::as_const(std::declval<__type11>())) __type12;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type12>::type>::type __type13;
        typedef decltype(std::declval<__type4>()(std::declval<__type9>(), std::declval<__type13>())) __type14;
        typedef typename pythonic::assignable<__type14>::type __type15;
        typedef __type15 __type16;
        typedef long __type17;
        typedef decltype(pythonic::operator_::functor::floordiv()(std::declval<__type16>(), std::declval<__type17>())) __type18;
        typedef decltype(pythonic::operator_::add(std::declval<__type18>(), std::declval<__type17>())) __type19;
        typedef decltype(std::declval<__type3>()(std::declval<__type19>())) __type20;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type20>::type::iterator>::value_type>::type __type21;
        typedef __type21 __type22;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type8>::type>::type __type23;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type12>::type>::type __type24;
        typedef decltype(std::declval<__type4>()(std::declval<__type23>(), std::declval<__type24>())) __type25;
        typedef typename pythonic::assignable<__type25>::type __type26;
        typedef __type26 __type27;
        typedef decltype(pythonic::operator_::functor::floordiv()(std::declval<__type27>(), std::declval<__type17>())) __type28;
        typedef decltype(pythonic::operator_::add(std::declval<__type28>(), std::declval<__type17>())) __type29;
        typedef decltype(std::declval<__type3>()(std::declval<__type29>())) __type30;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type30>::type::iterator>::value_type>::type __type31;
        typedef __type31 __type32;
        typedef typename std::tuple_element<2,typename std::remove_reference<__type8>::type>::type __type33;
        typedef typename std::tuple_element<2,typename std::remove_reference<__type12>::type>::type __type34;
        typedef decltype(std::declval<__type4>()(std::declval<__type33>(), std::declval<__type34>())) __type35;
        typedef typename pythonic::lazy<__type35>::type __type36;
        typedef __type36 __type37;
        typedef decltype(std::declval<__type3>()(std::declval<__type37>())) __type38;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type38>::type::iterator>::value_type>::type __type39;
        typedef __type39 __type40;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type22>(), std::declval<__type32>(), std::declval<__type40>())) __type41;
        typedef decltype(std::declval<__type2>()[std::declval<__type41>()]) __type42;
        typedef container<typename std::remove_reference<__type42>::type> __type43;
        typedef indexable<__type41> __type48;
        typedef decltype(pythonic::operator_::neg(std::declval<__type22>())) __type52;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type52>(), std::declval<__type32>(), std::declval<__type40>())) __type55;
        typedef decltype(std::declval<__type2>()[std::declval<__type55>()]) __type56;
        typedef container<typename std::remove_reference<__type56>::type> __type57;
        typedef indexable<__type55> __type63;
        typedef decltype(pythonic::operator_::neg(std::declval<__type32>())) __type69;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type52>(), std::declval<__type69>(), std::declval<__type40>())) __type71;
        typedef decltype(std::declval<__type2>()[std::declval<__type71>()]) __type72;
        typedef container<typename std::remove_reference<__type72>::type> __type73;
        typedef indexable<__type71> __type80;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type22>(), std::declval<__type69>(), std::declval<__type40>())) __type87;
        typedef decltype(std::declval<__type2>()[std::declval<__type87>()]) __type88;
        typedef container<typename std::remove_reference<__type88>::type> __type89;
        typedef indexable<__type87> __type95;
        typedef typename __combined<__type5,__type43,__type48,__type57,__type63,__type73,__type80,__type89,__type95>::type __type96;
        typedef __type42 __type97;
        typedef __type41 __type98;
        typedef pythonic::types::none_type __type99;
        typedef typename pythonic::returnable<__type99>::type __type100;
        typedef __type97 __ptype0;
        typedef __type98 __ptype1;
        typedef __type100 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 >
      inline
      typename type<argument_type0, argument_type1>::result_type operator()(argument_type0 field_fft_in, argument_type1 field_fft_out) const
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
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename fill_field_fft_3d::type<argument_type0, argument_type1>::result_type fill_field_fft_3d::operator()(argument_type0 field_fft_in, argument_type1 field_fft_out) const
    {
      typename pythonic::assignable_noescape<decltype(pythonic::builtins::functor::min{}(std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in)))))>::type nk0_min = pythonic::builtins::functor::min{}(std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in))));
      typename pythonic::assignable_noescape<decltype(pythonic::builtins::functor::min{}(std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in)))))>::type nk1_min = pythonic::builtins::functor::min{}(std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in))));
      typename pythonic::lazy<decltype(pythonic::builtins::functor::min{}(std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in)))))>::type nk2_min = pythonic::builtins::functor::min{}(std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_out))), std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_fft_in))));
      {
        long  __target139658370120048 = pythonic::operator_::add(pythonic::operator_::functor::floordiv()(nk0_min, 2L), 1L);
        for (long  ik0=0L; ik0 < __target139658370120048; ik0 += 1L)
        {
          {
            long  __target139658370148528 = pythonic::operator_::add(pythonic::operator_::functor::floordiv()(nk1_min, 2L), 1L);
            for (long  ik1=0L; ik1 < __target139658370148528; ik1 += 1L)
            {
              {
                long  __target139658370146560 = nk2_min;
                for (long  ik2=0L; ik2 < __target139658370146560; ik2 += 1L)
                {
                  field_fft_out[pythonic::types::make_tuple(ik0, ik1, ik2)] = pythonic::types::as_const(field_fft_in)[pythonic::types::make_tuple(ik0, ik1, ik2)];
                  if (pythonic::builtins::pythran::and_([&] () { return pythonic::operator_::gt(ik0, 0L); }, [&] () { return pythonic::operator_::lt(ik0, pythonic::operator_::functor::floordiv()(nk0_min, 2L)); }))
                  {
                    field_fft_out[pythonic::types::make_tuple(pythonic::operator_::neg(ik0), ik1, ik2)] = pythonic::types::as_const(field_fft_in)[pythonic::types::make_tuple(pythonic::operator_::neg(ik0), ik1, ik2)];
                    if (pythonic::builtins::pythran::and_([&] () { return pythonic::operator_::gt(ik1, 0L); }, [&] () { return pythonic::operator_::lt(ik1, pythonic::operator_::functor::floordiv()(nk1_min, 2L)); }))
                    {
                      field_fft_out[pythonic::types::make_tuple(pythonic::operator_::neg(ik0), pythonic::operator_::neg(ik1), ik2)] = pythonic::types::as_const(field_fft_in)[pythonic::types::make_tuple(pythonic::operator_::neg(ik0), pythonic::operator_::neg(ik1), ik2)];
                    }
                  }
                  if (pythonic::builtins::pythran::and_([&] () { return pythonic::operator_::gt(ik1, 0L); }, [&] () { return pythonic::operator_::lt(ik1, pythonic::operator_::functor::floordiv()(nk1_min, 2L)); }))
                  {
                    field_fft_out[pythonic::types::make_tuple(ik0, pythonic::operator_::neg(ik1), ik2)] = pythonic::types::as_const(field_fft_in)[pythonic::types::make_tuple(ik0, pythonic::operator_::neg(ik1), ik2)];
                  }
                }
              }
            }
          }
        }
      }
      return pythonic::builtins::None;
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_mini_oper_modif_resol::__transonic__()());
inline
typename __pythran_mini_oper_modif_resol::fill_field_fft_3d::type<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>::result_type fill_field_fft_3d0(pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>&& field_fft_in, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>&& field_fft_out) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_mini_oper_modif_resol::fill_field_fft_3d()(field_fft_in, field_fft_out);
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
__pythran_wrap_fill_field_fft_3d0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"field_fft_in", "field_fft_out",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[1]))
        return to_python(fill_field_fft_3d0(from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_fill_field_fft_3d(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_fill_field_fft_3d0(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "fill_field_fft_3d", "\n""    - fill_field_fft_3d(complex128[:,:,:], complex128[:,:,:])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "fill_field_fft_3d",
    (PyCFunction)__pythran_wrapall_fill_field_fft_3d,
    METH_VARARGS | METH_KEYWORDS,
    "Fill the values from field_fft_in in field_fft_out\n""\n""    Supported prototypes:\n""\n""    - fill_field_fft_3d(complex128[:,:,:], complex128[:,:,:])\n""\n""    This function is specialized for FFTW3DReal2Complex (no MPI).\n"""},
    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "mini_oper_modif_resol",            /* m_name */
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
PYTHRAN_MODULE_INIT(mini_oper_modif_resol)(void)
#ifndef _WIN32
__attribute__ ((visibility("default")))
#if defined(GNUC) && !defined(__clang__)
__attribute__ ((externally_visible))
#endif
#endif
;
PyMODINIT_FUNC
PYTHRAN_MODULE_INIT(mini_oper_modif_resol)(void) {
    import_array()
    #if PY_MAJOR_VERSION >= 3
    PyObject* theModule = PyModule_Create(&moduledef);
    #else
    PyObject* theModule = Py_InitModule3("mini_oper_modif_resol",
                                         Methods,
                                         ""
    );
    #endif
    if(! theModule)
        PYTHRAN_RETURN;
    PyObject * theDoc = Py_BuildValue("(sss)",
                                      "0.13.1",
                                      "2023-05-24 11:29:43.223275",
                                      "aed0a5a942d86c15c3186b3d60628d3c863c6f411067b70d2262f4d621beab2b");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif