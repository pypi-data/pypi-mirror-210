#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/uint8.hpp>
#include <pythonic/include/types/bool.hpp>
#include <pythonic/include/types/numpy_texpr.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/include/types/complex128.hpp>
#include <pythonic/include/types/int.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/types/int.hpp>
#include <pythonic/types/numpy_texpr.hpp>
#include <pythonic/types/complex128.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/uint8.hpp>
#include <pythonic/include/builtins/None.hpp>
#include <pythonic/include/builtins/getattr.hpp>
#include <pythonic/include/builtins/map.hpp>
#include <pythonic/include/builtins/range.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/operator_/add.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/operator_/eq.hpp>
#include <pythonic/include/operator_/lt.hpp>
#include <pythonic/include/operator_/mul.hpp>
#include <pythonic/include/operator_/sub.hpp>
#include <pythonic/include/random/uniform.hpp>
#include <pythonic/include/types/slice.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/None.hpp>
#include <pythonic/builtins/getattr.hpp>
#include <pythonic/builtins/map.hpp>
#include <pythonic/builtins/range.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/operator_/add.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/operator_/eq.hpp>
#include <pythonic/operator_/lt.hpp>
#include <pythonic/operator_/mul.hpp>
#include <pythonic/operator_/sub.hpp>
#include <pythonic/random/uniform.hpp>
#include <pythonic/types/slice.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
  namespace __pythran_operators2d
  {
    struct __for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0
    {
      typedef void callable;
      ;
      template <typename argument_type0 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::random::functor::uniform{})>::type>::type __type0;
        typedef double __type1;
        typedef decltype(std::declval<__type0>()(std::declval<__type1>(), std::declval<__type1>())) __type2;
        typedef typename pythonic::returnable<__type2>::type __type3;
        typedef __type3 result_type;
      }  
      ;
      template <typename argument_type0 >
      inline
      typename type<argument_type0>::result_type operator()(argument_type0 _) const
      ;
    }  ;
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
    struct __code_new_method__OperatorsPseudoSpectral2D__get_phases_random
    {
      typedef void callable;
      typedef void pure;
      struct type
      {
        typedef pythonic::types::str __type0;
        typedef typename pythonic::returnable<__type0>::type __type1;
        typedef __type1 result_type;
      }  ;
      inline
      typename type::result_type operator()() const;
      ;
    }  ;
    struct __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar
    {
      typedef void callable;
      typedef void pure;
      struct type
      {
        typedef pythonic::types::str __type0;
        typedef typename pythonic::returnable<__type0>::type __type1;
        typedef __type1 result_type;
      }  ;
      inline
      typename type::result_type operator()() const;
      ;
    }  ;
    struct __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar
    {
      typedef void callable;
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
      struct type
      {
        typedef double __type0;
        typedef __type0 __type1;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type2;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type3;
        typedef container<typename std::remove_reference<__type0>::type> __type4;
        typedef __type3 __type5;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type5>())) __type6;
        typedef decltype(pythonic::types::as_const(std::declval<__type6>())) __type7;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type7>::type>::type __type8;
        typedef typename pythonic::lazy<__type8>::type __type9;
        typedef __type9 __type10;
        typedef decltype(std::declval<__type2>()(std::declval<__type10>())) __type11;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type11>::type::iterator>::value_type>::type __type12;
        typedef __type12 __type13;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type7>::type>::type __type14;
        typedef typename pythonic::lazy<__type14>::type __type15;
        typedef __type15 __type16;
        typedef decltype(std::declval<__type2>()(std::declval<__type16>())) __type17;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type17>::type::iterator>::value_type>::type __type18;
        typedef __type18 __type19;
        typedef typename std::tuple_element<2,typename std::remove_reference<__type7>::type>::type __type20;
        typedef typename pythonic::lazy<__type20>::type __type21;
        typedef __type21 __type22;
        typedef decltype(std::declval<__type2>()(std::declval<__type22>())) __type23;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type23>::type::iterator>::value_type>::type __type24;
        typedef __type24 __type25;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type13>(), std::declval<__type19>(), std::declval<__type25>())) __type26;
        typedef indexable<__type26> __type27;
        typedef typename __combined<__type3,__type4,__type27>::type __type28;
        typedef __type26 __type29;
        typedef pythonic::types::none_type __type30;
        typedef typename pythonic::returnable<__type30>::type __type31;
        typedef __type1 __ptype0;
        typedef __type29 __ptype1;
        typedef __type31 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
      inline
      typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0 self__has_to_dealiase, argument_type1 self_where_dealiased, argument_type2 sov) const
      ;
    }  ;
    struct compute_increments_dim1
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
        typedef __type0 __type1;
        typedef decltype(pythonic::types::as_const(std::declval<__type1>())) __type2;
        typedef pythonic::types::contiguous_slice __type3;
        typedef decltype(std::declval<__type2>()(std::declval<__type3>(), std::declval<__type3>())) __type4;
        typedef decltype(pythonic::operator_::sub(std::declval<__type4>(), std::declval<__type4>())) __type8;
        typedef typename pythonic::returnable<__type8>::type __type9;
        typedef __type9 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 >
      inline
      typename type<argument_type0, argument_type1>::result_type operator()(argument_type0 var, argument_type1 irx) const
      ;
    }  ;
    struct invlaplacian_fft
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
        typedef __type0 __type1;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
        typedef __type2 __type3;
        typedef decltype(pythonic::operator_::div(std::declval<__type1>(), std::declval<__type3>())) __type4;
        typedef typename pythonic::assignable<__type4>::type __type5;
        typedef long __type6;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type6>(), std::declval<__type6>())) __type7;
        typedef indexable<__type7> __type8;
        typedef double __type9;
        typedef container<typename std::remove_reference<__type9>::type> __type10;
        typedef typename __combined<__type5,__type8,__type10>::type __type11;
        typedef __type11 __type12;
        typedef typename pythonic::returnable<__type12>::type __type13;
        typedef __type13 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
      inline
      typename type<argument_type0, argument_type1, argument_type2>::result_type operator()(argument_type0 a_fft, argument_type1 Kn_not0, argument_type2 rank) const
      ;
    }  ;
    struct laplacian_fft
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
        typedef __type0 __type1;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
        typedef __type2 __type3;
        typedef decltype(pythonic::operator_::mul(std::declval<__type1>(), std::declval<__type3>())) __type4;
        typedef typename pythonic::returnable<__type4>::type __type5;
        typedef __type5 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 >
      inline
      typename type<argument_type0, argument_type1>::result_type operator()(argument_type0 a_fft, argument_type1 Kn) const
      ;
    }  ;
    struct __for_method__OperatorsPseudoSpectral2D__get_phases_random
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::tuple{})>::type>::type __type0;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::map{})>::type>::type __type1;
        typedef __for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0 __type2;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type3;
        typedef long __type4;
        typedef decltype(std::declval<__type3>()(std::declval<__type4>())) __type5;
        typedef decltype(std::declval<__type1>()(std::declval<__type2>(), std::declval<__type5>())) __type6;
        typedef decltype(std::declval<__type0>()(std::declval<__type6>())) __type7;
        typedef typename pythonic::assignable<__type7>::type __type8;
        typedef __type8 __type9;
        typedef decltype(pythonic::types::as_const(std::declval<__type9>())) __type10;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type10>::type>::type __type11;
        typedef typename pythonic::assignable<__type11>::type __type12;
        typedef __type12 __type13;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type14;
        typedef __type14 __type15;
        typedef decltype(pythonic::operator_::mul(std::declval<__type13>(), std::declval<__type15>())) __type16;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type17;
        typedef __type17 __type18;
        typedef decltype(pythonic::operator_::mul(std::declval<__type16>(), std::declval<__type18>())) __type19;
        typedef std::integral_constant<long,0> __type20;
        typedef indexable_container<__type20, typename std::remove_reference<__type11>::type> __type21;
        typedef typename __combined<__type8,__type21>::type __type22;
        typedef __type22 __type23;
        typedef decltype(pythonic::types::as_const(std::declval<__type23>())) __type24;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type24>::type>::type __type25;
        typedef typename pythonic::assignable<__type25>::type __type26;
        typedef __type26 __type27;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type3>::type>::type __type28;
        typedef __type28 __type29;
        typedef decltype(pythonic::operator_::mul(std::declval<__type27>(), std::declval<__type29>())) __type30;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type31;
        typedef __type31 __type32;
        typedef decltype(pythonic::operator_::mul(std::declval<__type30>(), std::declval<__type32>())) __type33;
        typedef decltype(pythonic::operator_::add(std::declval<__type19>(), std::declval<__type33>())) __type34;
        typedef double __type36;
        typedef decltype(pythonic::operator_::add(std::declval<__type13>(), std::declval<__type36>())) __type37;
        typedef decltype(pythonic::operator_::sub(std::declval<__type13>(), std::declval<__type36>())) __type39;
        typedef typename __combined<__type37,__type39>::type __type40;
        typedef decltype(pythonic::operator_::mul(std::declval<__type40>(), std::declval<__type15>())) __type42;
        typedef decltype(pythonic::operator_::mul(std::declval<__type42>(), std::declval<__type18>())) __type44;
        typedef decltype(pythonic::operator_::add(std::declval<__type27>(), std::declval<__type36>())) __type46;
        typedef decltype(pythonic::operator_::sub(std::declval<__type27>(), std::declval<__type36>())) __type48;
        typedef typename __combined<__type46,__type48>::type __type49;
        typedef decltype(pythonic::operator_::mul(std::declval<__type49>(), std::declval<__type29>())) __type51;
        typedef decltype(pythonic::operator_::mul(std::declval<__type51>(), std::declval<__type32>())) __type53;
        typedef decltype(pythonic::operator_::add(std::declval<__type44>(), std::declval<__type53>())) __type54;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type34>(), std::declval<__type54>())) __type55;
        typedef typename pythonic::returnable<__type55>::type __type56;
        typedef __type56 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
      inline
      typename type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type operator()(argument_type0 self_KX, argument_type1 self_KY, argument_type2 self_deltax, argument_type3 self_deltay) const
      ;
    }  ;
    template <typename argument_type0 >
    inline
    typename __for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0::type<argument_type0>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0::operator()(argument_type0 _) const
    {
      return pythonic::random::functor::uniform{}(-0.5, 0.5);
    }
    inline
    typename __transonic__::type::result_type __transonic__::operator()() const
    {
      {
        static typename __transonic__::type::result_type tmp_global = pythonic::types::make_tuple(pythonic::types::str("0.5.2.post0"));
        return tmp_global;
      }
    }
    inline
    typename __code_new_method__OperatorsPseudoSpectral2D__get_phases_random::type::result_type __code_new_method__OperatorsPseudoSpectral2D__get_phases_random::operator()() const
    {
      {
        static typename __code_new_method__OperatorsPseudoSpectral2D__get_phases_random::type::result_type tmp_global = pythonic::types::str("\n\ndef new_method(self, ):\n    return backend_func(self.KX, self.KY, self.deltax, self.deltay, )\n\n");
        return tmp_global;
      }
    }
    inline
    typename __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::type::result_type __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::operator()() const
    {
      {
        static typename __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::type::result_type tmp_global = pythonic::types::str("\n\ndef new_method(self, sov):\n    return backend_func(self._has_to_dealiase, self.where_dealiased, sov)\n\n");
        return tmp_global;
      }
    }
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    inline
    typename __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::type<argument_type0, argument_type1, argument_type2>::result_type __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::operator()(argument_type0 self__has_to_dealiase, argument_type1 self_where_dealiased, argument_type2 sov) const
    {
      if (self__has_to_dealiase)
      {
        typename pythonic::lazy<decltype(std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov))))>::type nk = std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov)));
        typename pythonic::lazy<decltype(std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov))))>::type n0 = std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov)));
        typename pythonic::lazy<decltype(std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov))))>::type n1 = std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, sov)));
        {
          long  __target139658368690352 = n0;
          for (long  i0=0L; i0 < __target139658368690352; i0 += 1L)
          {
            {
              long  __target139658368688864 = n1;
              for (long  i1=0L; i1 < __target139658368688864; i1 += 1L)
              {
                if (pythonic::types::as_const(self_where_dealiased)[pythonic::types::make_tuple(i0, i1)])
                {
                  {
                    long  __target139658368385328 = nk;
                    for (long  ik=0L; ik < __target139658368385328; ik += 1L)
                    {
                      sov[pythonic::types::make_tuple(ik, i0, i1)] = 0.0;
                    }
                  }
                }
              }
            }
          }
        }
      }
      return pythonic::builtins::None;
    }
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename compute_increments_dim1::type<argument_type0, argument_type1>::result_type compute_increments_dim1::operator()(argument_type0 var, argument_type1 irx) const
    {
      typename pythonic::assignable_noescape<decltype(std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, var))))>::type n1 = std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, var)));
      return pythonic::operator_::sub(pythonic::types::as_const(var)(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(irx,n1)), pythonic::types::as_const(var)(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(0L,pythonic::operator_::sub(n1, irx))));
    }
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 >
    inline
    typename invlaplacian_fft::type<argument_type0, argument_type1, argument_type2>::result_type invlaplacian_fft::operator()(argument_type0 a_fft, argument_type1 Kn_not0, argument_type2 rank) const
    {
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type0;
      typedef __type0 __type1;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type2;
      typedef __type2 __type3;
      typedef decltype(pythonic::operator_::div(std::declval<__type1>(), std::declval<__type3>())) __type4;
      typedef typename pythonic::assignable<__type4>::type __type5;
      typedef long __type6;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type6>(), std::declval<__type6>())) __type7;
      typedef indexable<__type7> __type8;
      typedef double __type9;
      typedef container<typename std::remove_reference<__type9>::type> __type10;
      typedef typename __combined<__type5,__type8,__type10>::type __type11;
      typedef typename pythonic::assignable<__type11>::type __type12;
      __type12 invlap_afft = pythonic::operator_::div(a_fft, Kn_not0);
      if (pythonic::operator_::eq(rank, 0L))
      {
        invlap_afft.fast(pythonic::types::make_tuple(0L, 0L)) = 0.0;
      }
      return invlap_afft;
    }
    template <typename argument_type0 , typename argument_type1 >
    inline
    typename laplacian_fft::type<argument_type0, argument_type1>::result_type laplacian_fft::operator()(argument_type0 a_fft, argument_type1 Kn) const
    {
      return pythonic::operator_::mul(a_fft, Kn);
    }
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 >
    inline
    typename __for_method__OperatorsPseudoSpectral2D__get_phases_random::type<argument_type0, argument_type1, argument_type2, argument_type3>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random::operator()(argument_type0 self_KX, argument_type1 self_KY, argument_type2 self_deltax, argument_type3 self_deltay) const
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::tuple{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::map{})>::type>::type __type1;
      typedef __for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0 __type2;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type3;
      typedef long __type4;
      typedef decltype(std::declval<__type3>()(std::declval<__type4>())) __type5;
      typedef decltype(std::declval<__type1>()(std::declval<__type2>(), std::declval<__type5>())) __type6;
      typedef decltype(std::declval<__type0>()(std::declval<__type6>())) __type7;
      typedef typename pythonic::assignable<__type7>::type __type8;
      typedef std::integral_constant<long,0> __type9;
      typedef __type8 __type10;
      typedef decltype(pythonic::types::as_const(std::declval<__type10>())) __type11;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type11>::type>::type __type12;
      typedef indexable_container<__type9, typename std::remove_reference<__type12>::type> __type13;
      typedef std::integral_constant<long,1> __type14;
      typedef typename __combined<__type8,__type13>::type __type15;
      typedef __type15 __type16;
      typedef decltype(pythonic::types::as_const(std::declval<__type16>())) __type17;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type17>::type>::type __type18;
      typedef indexable_container<__type14, typename std::remove_reference<__type18>::type> __type19;
      typedef typename __combined<__type8,__type13,__type19>::type __type20;
      typedef typename pythonic::assignable<__type20>::type __type21;
      __type21 __tuple0 = pythonic::builtins::functor::tuple{}(pythonic::builtins::functor::map{}(__for_method__OperatorsPseudoSpectral2D__get_phases_random_lambda0(), pythonic::builtins::functor::range{}(2L)));
      typename pythonic::assignable_noescape<decltype(std::get<0>(pythonic::types::as_const(__tuple0)))>::type alpha_x = std::get<0>(pythonic::types::as_const(__tuple0));
      typename pythonic::assignable_noescape<decltype(std::get<1>(pythonic::types::as_const(__tuple0)))>::type alpha_y = std::get<1>(pythonic::types::as_const(__tuple0));
      return pythonic::types::make_tuple(pythonic::operator_::add(pythonic::operator_::mul(pythonic::operator_::mul(alpha_x, self_deltax), self_KX), pythonic::operator_::mul(pythonic::operator_::mul(alpha_y, self_deltay), self_KY)), pythonic::operator_::add(pythonic::operator_::mul(pythonic::operator_::mul((((bool)pythonic::operator_::lt(alpha_x, 0L)) ? typename __combined<decltype(pythonic::operator_::add(alpha_x, 0.5)), decltype(pythonic::operator_::sub(alpha_x, 0.5))>::type(pythonic::operator_::add(alpha_x, 0.5)) : typename __combined<decltype(pythonic::operator_::add(alpha_x, 0.5)), decltype(pythonic::operator_::sub(alpha_x, 0.5))>::type(pythonic::operator_::sub(alpha_x, 0.5))), self_deltax), self_KX), pythonic::operator_::mul(pythonic::operator_::mul((((bool)pythonic::operator_::lt(alpha_y, 0L)) ? typename __combined<decltype(pythonic::operator_::add(alpha_y, 0.5)), decltype(pythonic::operator_::sub(alpha_y, 0.5))>::type(pythonic::operator_::add(alpha_y, 0.5)) : typename __combined<decltype(pythonic::operator_::add(alpha_y, 0.5)), decltype(pythonic::operator_::sub(alpha_y, 0.5))>::type(pythonic::operator_::sub(alpha_y, 0.5))), self_deltay), self_KY)));
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_operators2d::__transonic__()());
static PyObject* __code_new_method__OperatorsPseudoSpectral2D__get_phases_random = to_python(__pythran_operators2d::__code_new_method__OperatorsPseudoSpectral2D__get_phases_random()());
inline
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double, double>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random0(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& self_KX, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& self_KY, double&& self_deltax, double&& self_deltay) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random()(self_KX, self_KY, self_deltax, self_deltay);
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
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double, double>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random1(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& self_KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& self_KY, double&& self_deltax, double&& self_deltay) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random()(self_KX, self_KY, self_deltax, self_deltay);
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
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, double, double>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random2(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& self_KX, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& self_KY, double&& self_deltax, double&& self_deltay) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random()(self_KX, self_KY, self_deltax, self_deltay);
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
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, double, double>::result_type __for_method__OperatorsPseudoSpectral2D__get_phases_random3(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& self_KX, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& self_KY, double&& self_deltax, double&& self_deltay) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__get_phases_random()(self_KX, self_KY, self_deltax, self_deltay);
                                PyEval_RestoreThread(_save);
                                return res;
                            }
                            catch(...) {
                                PyEval_RestoreThread(_save);
                                throw;
                            }
                            ;
}
static PyObject* __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar = to_python(__pythran_operators2d::__code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar()());
inline
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::type<bool, pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>::result_type __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar0(bool&& self__has_to_dealiase, pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>&& self_where_dealiased, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>&& sov) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar()(self__has_to_dealiase, self_where_dealiased, sov);
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
typename __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar::type<bool, pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>::result_type __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar1(bool&& self__has_to_dealiase, pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>&& self_where_dealiased, pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>&& sov) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar()(self__has_to_dealiase, self_where_dealiased, sov);
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
typename __pythran_operators2d::compute_increments_dim1::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, long>::result_type compute_increments_dim10(pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& var, long&& irx) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::compute_increments_dim1()(var, irx);
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
typename __pythran_operators2d::compute_increments_dim1::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, long>::result_type compute_increments_dim11(pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& var, long&& irx) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::compute_increments_dim1()(var, irx);
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
typename __pythran_operators2d::invlaplacian_fft::type<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, long>::result_type invlaplacian_fft0(pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>&& a_fft, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& Kn_not0, long&& rank) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::invlaplacian_fft()(a_fft, Kn_not0, rank);
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
typename __pythran_operators2d::invlaplacian_fft::type<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, long>::result_type invlaplacian_fft1(pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>&& a_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& Kn_not0, long&& rank) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::invlaplacian_fft()(a_fft, Kn_not0, rank);
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
typename __pythran_operators2d::invlaplacian_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>, long>::result_type invlaplacian_fft2(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>&& a_fft, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& Kn_not0, long&& rank) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::invlaplacian_fft()(a_fft, Kn_not0, rank);
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
typename __pythran_operators2d::invlaplacian_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>, long>::result_type invlaplacian_fft3(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>&& a_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& Kn_not0, long&& rank) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::invlaplacian_fft()(a_fft, Kn_not0, rank);
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
typename __pythran_operators2d::laplacian_fft::type<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type laplacian_fft0(pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>&& a_fft, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& Kn) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::laplacian_fft()(a_fft, Kn);
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
typename __pythran_operators2d::laplacian_fft::type<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type laplacian_fft1(pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>&& a_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& Kn) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::laplacian_fft()(a_fft, Kn);
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
typename __pythran_operators2d::laplacian_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>::result_type laplacian_fft2(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>&& a_fft, pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>&& Kn) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::laplacian_fft()(a_fft, Kn);
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
typename __pythran_operators2d::laplacian_fft::type<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>::result_type laplacian_fft3(pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>&& a_fft, pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>&& Kn) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_operators2d::laplacian_fft()(a_fft, Kn);
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
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"self_KX", "self_KY", "self_deltax", "self_deltay",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<double>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__get_phases_random0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<double>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"self_KX", "self_KY", "self_deltax", "self_deltay",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<double>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__get_phases_random1(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<double>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"self_KX", "self_KY", "self_deltax", "self_deltay",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<double>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__get_phases_random2(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<double>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[4+1];
    
    char const* keywords[] = {"self_KX", "self_KY", "self_deltax", "self_deltay",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<double>(args_obj[2]) && is_convertible<double>(args_obj[3]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__get_phases_random3(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<double>(args_obj[2]), from_python<double>(args_obj[3])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"self__has_to_dealiase", "self_where_dealiased", "sov",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<bool>(args_obj[0]) && is_convertible<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[2]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar0(from_python<bool>(args_obj[0]), from_python<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"self__has_to_dealiase", "self_where_dealiased", "sov",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<bool>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[2]))
        return to_python(__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar1(from_python<bool>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<npy_uint8,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long,long>>>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_increments_dim10(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"var", "irx",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<long>(args_obj[1]))
        return to_python(compute_increments_dim10(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<long>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_increments_dim11(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"var", "irx",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<long>(args_obj[1]))
        return to_python(compute_increments_dim11(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<long>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_invlaplacian_fft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"a_fft", "Kn_not0", "rank",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<long>(args_obj[2]))
        return to_python(invlaplacian_fft0(from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<long>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_invlaplacian_fft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"a_fft", "Kn_not0", "rank",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<long>(args_obj[2]))
        return to_python(invlaplacian_fft1(from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<long>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_invlaplacian_fft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"a_fft", "Kn_not0", "rank",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]) && is_convertible<long>(args_obj[2]))
        return to_python(invlaplacian_fft2(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]), from_python<long>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_invlaplacian_fft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[3+1];
    
    char const* keywords[] = {"a_fft", "Kn_not0", "rank",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]) && is_convertible<long>(args_obj[2]))
        return to_python(invlaplacian_fft3(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]), from_python<long>(args_obj[2])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_laplacian_fft0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"a_fft", "Kn",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]))
        return to_python(laplacian_fft0(from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_laplacian_fft1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"a_fft", "Kn",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]))
        return to_python(laplacian_fft1(from_python<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_laplacian_fft2(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"a_fft", "Kn",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1]))
        return to_python(laplacian_fft2(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>(args_obj[1])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_laplacian_fft3(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[2+1];
    
    char const* keywords[] = {"a_fft", "Kn",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OO",
                                     (char**)keywords , &args_obj[0], &args_obj[1]))
        return nullptr;
    if(is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]) && is_convertible<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1]))
        return to_python(laplacian_fft3(from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<std::complex<double>,pythonic::types::pshape<long,long>>>>(args_obj[0]), from_python<pythonic::types::numpy_texpr<pythonic::types::ndarray<double,pythonic::types::pshape<long,long>>>>(args_obj[1])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall___for_method__OperatorsPseudoSpectral2D__get_phases_random(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__get_phases_random3(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "__for_method__OperatorsPseudoSpectral2D__get_phases_random", "\n""    - __for_method__OperatorsPseudoSpectral2D__get_phases_random(float64[:,:], float64[:,:], float64, float64)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar", "\n""    - __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar(bool, uint8[:,:], complex128[:,:,:])", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_compute_increments_dim1(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_compute_increments_dim10(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_increments_dim11(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "compute_increments_dim1", "\n""    - compute_increments_dim1(float64[:,:], int)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_invlaplacian_fft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_invlaplacian_fft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_invlaplacian_fft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_invlaplacian_fft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_invlaplacian_fft3(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "invlaplacian_fft", "\n""    - invlaplacian_fft(complex128[:,:], float64[:,:], int)", args, kw);
                });
            }


            static PyObject *
            __pythran_wrapall_laplacian_fft(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_laplacian_fft0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_laplacian_fft1(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_laplacian_fft2(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_laplacian_fft3(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "laplacian_fft", "\n""    - laplacian_fft(complex128[:,:], float64[:,:])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "__for_method__OperatorsPseudoSpectral2D__get_phases_random",
    (PyCFunction)__pythran_wrapall___for_method__OperatorsPseudoSpectral2D__get_phases_random,
    METH_VARARGS | METH_KEYWORDS,
    "Supported prototypes:\n""\n""    - __for_method__OperatorsPseudoSpectral2D__get_phases_random(float64[:,:], float64[:,:], float64, float64)"},{
    "__for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar",
    (PyCFunction)__pythran_wrapall___for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar,
    METH_VARARGS | METH_KEYWORDS,
    "Dealiasing of a setofvar arrays.\n""\n""    Supported prototypes:\n""\n""    - __for_method__OperatorsPseudoSpectral2D__dealiasing_setofvar(bool, uint8[:,:], complex128[:,:,:])"},{
    "compute_increments_dim1",
    (PyCFunction)__pythran_wrapall_compute_increments_dim1,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the increments of var over the dim 1.\n""\n""    Supported prototypes:\n""\n""    - compute_increments_dim1(float64[:,:], int)"},{
    "invlaplacian_fft",
    (PyCFunction)__pythran_wrapall_invlaplacian_fft,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the n-th order inverse Laplacian.\n""\n""    Supported prototypes:\n""\n""    - invlaplacian_fft(complex128[:,:], float64[:,:], int)"},{
    "laplacian_fft",
    (PyCFunction)__pythran_wrapall_laplacian_fft,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the n-th order Laplacian.\n""\n""    Supported prototypes:\n""\n""    - laplacian_fft(complex128[:,:], float64[:,:])"},
    {NULL, NULL, 0, NULL}
};


            #if PY_MAJOR_VERSION >= 3
              static struct PyModuleDef moduledef = {
                PyModuleDef_HEAD_INIT,
                "operators2d",            /* m_name */
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
            PYTHRAN_MODULE_INIT(operators2d)(void)
            #ifndef _WIN32
            __attribute__ ((visibility("default")))
            #if defined(GNUC) && !defined(__clang__)
            __attribute__ ((externally_visible))
            #endif
            #endif
            ;
            PyMODINIT_FUNC
            PYTHRAN_MODULE_INIT(operators2d)(void) {
                import_array()
                #if PY_MAJOR_VERSION >= 3
                PyObject* theModule = PyModule_Create(&moduledef);
                #else
                PyObject* theModule = Py_InitModule3("operators2d",
                                                     Methods,
                                                     ""
                );
                #endif
                if(! theModule)
                    PYTHRAN_RETURN;
                PyObject * theDoc = Py_BuildValue("(sss)",
                                                  "0.13.1",
                                                  "2023-05-24 11:29:39.975885",
                                                  "6836ea80017072922f20c1f41ddb3ae52d9106d3b02323070cf65af78d5f0adb");
                if(! theDoc)
                    PYTHRAN_RETURN;
                PyModule_AddObject(theModule,
                                   "__pythran__",
                                   theDoc);

                PyModule_AddObject(theModule, "__transonic__", __transonic__);
PyModule_AddObject(theModule, "__code_new_method__OperatorsPseudoSpectral2D__get_phases_random", __code_new_method__OperatorsPseudoSpectral2D__get_phases_random);
PyModule_AddObject(theModule, "__code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar", __code_new_method__OperatorsPseudoSpectral2D__dealiasing_setofvar);
                PYTHRAN_RETURN;
            }

#endif