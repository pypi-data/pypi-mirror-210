#include <pythonic/core.hpp>
#include <pythonic/python/core.hpp>
#include <pythonic/types/bool.hpp>
#include <pythonic/types/int.hpp>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <pythonic/include/types/float64.hpp>
#include <pythonic/include/types/float32.hpp>
#include <pythonic/include/types/ndarray.hpp>
#include <pythonic/types/float64.hpp>
#include <pythonic/types/float32.hpp>
#include <pythonic/types/ndarray.hpp>
#include <pythonic/include/builtins/abs.hpp>
#include <pythonic/include/builtins/enumerate.hpp>
#include <pythonic/include/builtins/getattr.hpp>
#include <pythonic/include/builtins/int_.hpp>
#include <pythonic/include/builtins/len.hpp>
#include <pythonic/include/builtins/pythran/make_shape.hpp>
#include <pythonic/include/builtins/range.hpp>
#include <pythonic/include/builtins/round.hpp>
#include <pythonic/include/builtins/tuple.hpp>
#include <pythonic/include/numpy/zeros.hpp>
#include <pythonic/include/operator_/add.hpp>
#include <pythonic/include/operator_/div.hpp>
#include <pythonic/include/operator_/floordiv.hpp>
#include <pythonic/include/operator_/ge.hpp>
#include <pythonic/include/operator_/iadd.hpp>
#include <pythonic/include/operator_/mul.hpp>
#include <pythonic/include/operator_/ne.hpp>
#include <pythonic/include/operator_/neg.hpp>
#include <pythonic/include/operator_/sub.hpp>
#include <pythonic/include/types/slice.hpp>
#include <pythonic/include/types/str.hpp>
#include <pythonic/builtins/abs.hpp>
#include <pythonic/builtins/enumerate.hpp>
#include <pythonic/builtins/getattr.hpp>
#include <pythonic/builtins/int_.hpp>
#include <pythonic/builtins/len.hpp>
#include <pythonic/builtins/pythran/make_shape.hpp>
#include <pythonic/builtins/range.hpp>
#include <pythonic/builtins/round.hpp>
#include <pythonic/builtins/tuple.hpp>
#include <pythonic/numpy/zeros.hpp>
#include <pythonic/operator_/add.hpp>
#include <pythonic/operator_/div.hpp>
#include <pythonic/operator_/floordiv.hpp>
#include <pythonic/operator_/ge.hpp>
#include <pythonic/operator_/iadd.hpp>
#include <pythonic/operator_/mul.hpp>
#include <pythonic/operator_/ne.hpp>
#include <pythonic/operator_/neg.hpp>
#include <pythonic/operator_/sub.hpp>
#include <pythonic/types/slice.hpp>
#include <pythonic/types/str.hpp>
namespace 
{
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
    struct compute_spectrum_kzkhomega
    {
      typedef void callable;
      typedef void pure;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
      struct type
      {
        typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type0;
        typedef __type0 __type1;
        typedef decltype(pythonic::types::as_const(std::declval<__type1>())) __type2;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type2>::type>::type __type3;
        typedef __type3 __type4;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type5;
        typedef __type5 __type6;
        typedef decltype(pythonic::types::as_const(std::declval<__type6>())) __type7;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type7>::type>::type __type8;
        typedef __type8 __type9;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type10;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::pythran::functor::make_shape{})>::type>::type __type11;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type12;
        typedef std::integral_constant<long,1> __type13;
        typedef indexable_container<__type13, typename std::remove_reference<__type8>::type> __type14;
        typedef typename __combined<__type5,__type14>::type __type15;
        typedef __type15 __type16;
        typedef decltype(std::declval<__type12>()(std::declval<__type16>())) __type17;
        typedef typename pythonic::assignable<__type17>::type __type18;
        typedef __type18 __type19;
        typedef indexable_container<__type13, typename std::remove_reference<__type3>::type> __type20;
        typedef typename __combined<__type0,__type20>::type __type21;
        typedef __type21 __type22;
        typedef decltype(std::declval<__type12>()(std::declval<__type22>())) __type23;
        typedef typename pythonic::assignable<__type23>::type __type24;
        typedef __type24 __type25;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type26;
        typedef __type26 __type27;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type27>())) __type28;
        typedef decltype(pythonic::types::as_const(std::declval<__type28>())) __type29;
        typedef typename std::tuple_element<3,typename std::remove_reference<__type29>::type>::type __type30;
        typedef typename pythonic::assignable<__type30>::type __type31;
        typedef __type31 __type32;
        typedef long __type33;
        typedef decltype(pythonic::operator_::add(std::declval<__type32>(), std::declval<__type33>())) __type34;
        typedef decltype(pythonic::operator_::functor::floordiv()(std::declval<__type34>(), std::declval<__type33>())) __type35;
        typedef typename pythonic::assignable<__type35>::type __type36;
        typedef __type36 __type37;
        typedef decltype(std::declval<__type11>()(std::declval<__type19>(), std::declval<__type25>(), std::declval<__type37>())) __type38;
        typedef decltype(std::declval<__type10>()(std::declval<__type38>())) __type39;
        typedef typename pythonic::assignable<__type39>::type __type40;
        typedef decltype(std::declval<__type11>()(std::declval<__type19>(), std::declval<__type25>(), std::declval<__type32>())) __type44;
        typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::DTYPE{}, std::declval<__type27>())) __type46;
        typedef decltype(std::declval<__type10>()(std::declval<__type44>(), std::declval<__type46>())) __type47;
        typedef typename pythonic::assignable<__type47>::type __type48;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::int_{})>::type>::type __type49;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::round{})>::type>::type __type50;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::abs{})>::type>::type __type51;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type52;
        typedef __type52 __type53;
        typedef decltype(pythonic::types::as_const(std::declval<__type53>())) __type54;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type55;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type29>::type>::type __type56;
        typedef typename pythonic::lazy<__type56>::type __type57;
        typedef __type57 __type58;
        typedef decltype(std::declval<__type55>()(std::declval<__type58>())) __type59;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type59>::type::iterator>::value_type>::type __type60;
        typedef __type60 __type61;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type29>::type>::type __type62;
        typedef typename pythonic::lazy<__type62>::type __type63;
        typedef __type63 __type64;
        typedef decltype(std::declval<__type55>()(std::declval<__type64>())) __type65;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type65>::type::iterator>::value_type>::type __type66;
        typedef __type66 __type67;
        typedef typename std::tuple_element<2,typename std::remove_reference<__type29>::type>::type __type68;
        typedef typename pythonic::lazy<__type68>::type __type69;
        typedef __type69 __type70;
        typedef decltype(std::declval<__type55>()(std::declval<__type70>())) __type71;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type71>::type::iterator>::value_type>::type __type72;
        typedef __type72 __type73;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type61>(), std::declval<__type67>(), std::declval<__type73>())) __type74;
        typedef decltype(std::declval<__type54>()[std::declval<__type74>()]) __type75;
        typedef decltype(std::declval<__type51>()(std::declval<__type75>())) __type76;
        typedef typename pythonic::assignable<__type8>::type __type77;
        typedef __type77 __type78;
        typedef decltype(pythonic::operator_::div(std::declval<__type76>(), std::declval<__type78>())) __type79;
        typedef decltype(std::declval<__type50>()(std::declval<__type79>())) __type80;
        typedef decltype(std::declval<__type49>()(std::declval<__type80>())) __type81;
        typedef typename pythonic::lazy<__type81>::type __type82;
        typedef decltype(pythonic::operator_::sub(std::declval<__type19>(), std::declval<__type33>())) __type84;
        typedef typename pythonic::lazy<__type84>::type __type85;
        typedef typename __combined<__type82,__type85>::type __type86;
        typedef __type86 __type87;
        typedef decltype(pythonic::operator_::sub(std::declval<__type25>(), std::declval<__type33>())) __type89;
        typedef typename pythonic::lazy<__type89>::type __type90;
        typedef __type90 __type91;
        typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::enumerate{})>::type>::type __type92;
        typedef decltype(pythonic::types::as_const(std::declval<__type27>())) __type94;
        typedef pythonic::types::contiguous_slice __type98;
        typedef decltype(std::declval<__type94>()(std::declval<__type61>(), std::declval<__type67>(), std::declval<__type73>(), std::declval<__type98>())) __type99;
        typedef typename pythonic::lazy<__type99>::type __type100;
        typedef __type100 __type101;
        typedef decltype(pythonic::operator_::mul(std::declval<__type33>(), std::declval<__type101>())) __type102;
        typedef typename pythonic::lazy<__type102>::type __type103;
        typedef typename __combined<__type100,__type103>::type __type104;
        typedef __type104 __type105;
        typedef decltype(std::declval<__type92>()(std::declval<__type105>())) __type106;
        typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type106>::type::iterator>::value_type>::type __type107;
        typedef __type107 __type108;
        typedef decltype(pythonic::types::as_const(std::declval<__type108>())) __type109;
        typedef typename std::tuple_element<0,typename std::remove_reference<__type109>::type>::type __type110;
        typedef typename pythonic::lazy<__type110>::type __type111;
        typedef __type111 __type112;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type87>(), std::declval<__type91>(), std::declval<__type112>())) __type113;
        typedef indexable<__type113> __type114;
        typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type116;
        typedef __type116 __type117;
        typedef decltype(pythonic::types::as_const(std::declval<__type117>())) __type118;
        typedef decltype(std::declval<__type118>()[std::declval<__type74>()]) __type123;
        typedef typename pythonic::assignable<__type123>::type __type124;
        typedef __type124 __type125;
        typedef typename pythonic::assignable<__type3>::type __type126;
        typedef __type126 __type127;
        typedef decltype(pythonic::operator_::div(std::declval<__type125>(), std::declval<__type127>())) __type128;
        typedef decltype(std::declval<__type49>()(std::declval<__type128>())) __type129;
        typedef typename pythonic::assignable<__type129>::type __type130;
        typedef __type130 __type131;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type87>(), std::declval<__type131>(), std::declval<__type112>())) __type140;
        typedef indexable<__type140> __type141;
        typedef decltype(pythonic::operator_::add(std::declval<__type131>(), std::declval<__type33>())) __type144;
        typedef decltype(pythonic::types::make_tuple(std::declval<__type87>(), std::declval<__type144>(), std::declval<__type112>())) __type146;
        typedef indexable<__type146> __type147;
        typedef typename std::tuple_element<1,typename std::remove_reference<__type109>::type>::type __type150;
        typedef typename pythonic::lazy<__type150>::type __type151;
        typedef __type151 __type152;
        typedef container<typename std::remove_reference<__type152>::type> __type153;
        typedef decltype(pythonic::types::as_const(std::declval<__type22>())) __type156;
        typedef decltype(std::declval<__type156>()[std::declval<__type131>()]) __type158;
        typedef decltype(pythonic::operator_::sub(std::declval<__type125>(), std::declval<__type158>())) __type159;
        typedef decltype(pythonic::operator_::div(std::declval<__type159>(), std::declval<__type127>())) __type161;
        typedef typename pythonic::assignable<__type161>::type __type162;
        typedef __type162 __type163;
        typedef decltype(pythonic::operator_::sub(std::declval<__type33>(), std::declval<__type163>())) __type164;
        typedef typename pythonic::assignable<__type150>::type __type168;
        typedef __type168 __type169;
        typedef decltype(pythonic::operator_::mul(std::declval<__type164>(), std::declval<__type169>())) __type170;
        typedef container<typename std::remove_reference<__type170>::type> __type171;
        typedef decltype(pythonic::operator_::mul(std::declval<__type163>(), std::declval<__type169>())) __type174;
        typedef container<typename std::remove_reference<__type174>::type> __type175;
        typedef typename __combined<__type48,__type114,__type141,__type147,__type153,__type171,__type175>::type __type176;
        typedef __type176 __type177;
        typedef decltype(pythonic::types::as_const(std::declval<__type177>())) __type178;
        typedef decltype(std::declval<__type178>()(std::declval<__type98>(), std::declval<__type98>(), std::declval<__type33>())) __type179;
        typedef container<typename std::remove_reference<__type179>::type> __type180;
        typedef decltype(std::declval<__type178>()(std::declval<__type98>(), std::declval<__type98>(), std::declval<__type98>())) __type183;
        typedef pythonic::types::slice __type186;
        typedef decltype(std::declval<__type178>()(std::declval<__type98>(), std::declval<__type98>(), std::declval<__type186>())) __type187;
        typedef decltype(pythonic::operator_::add(std::declval<__type183>(), std::declval<__type187>())) __type188;
        typedef container<typename std::remove_reference<__type188>::type> __type189;
        typedef typename __combined<__type40,__type180,__type189>::type __type190;
        typedef __type190 __type191;
        typedef decltype(pythonic::operator_::mul(std::declval<__type78>(), std::declval<__type127>())) __type194;
        typedef decltype(pythonic::operator_::div(std::declval<__type191>(), std::declval<__type194>())) __type195;
        typedef typename pythonic::returnable<__type195>::type __type196;
        typedef __type4 __ptype0;
        typedef __type9 __ptype1;
        typedef __type196 result_type;
      }  
      ;
      template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
      inline
      typename type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type operator()(argument_type0 field_k0k1k2omega, argument_type1 khs, argument_type2 kzs, argument_type3 KX, argument_type4 KZ, argument_type5 KH) const
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
    template <typename argument_type0 , typename argument_type1 , typename argument_type2 , typename argument_type3 , typename argument_type4 , typename argument_type5 >
    inline
    typename compute_spectrum_kzkhomega::type<argument_type0, argument_type1, argument_type2, argument_type3, argument_type4, argument_type5>::result_type compute_spectrum_kzkhomega::operator()(argument_type0 field_k0k1k2omega, argument_type1 khs, argument_type2 kzs, argument_type3 KX, argument_type4 KZ, argument_type5 KH) const
    {
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::numpy::functor::zeros{})>::type>::type __type0;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::pythran::functor::make_shape{})>::type>::type __type1;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::len{})>::type>::type __type2;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type2>::type>::type __type3;
      typedef std::integral_constant<long,1> __type4;
      typedef __type3 __type5;
      typedef decltype(pythonic::types::as_const(std::declval<__type5>())) __type6;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type6>::type>::type __type7;
      typedef indexable_container<__type4, typename std::remove_reference<__type7>::type> __type8;
      typedef typename __combined<__type3,__type8>::type __type9;
      typedef __type9 __type10;
      typedef decltype(std::declval<__type2>()(std::declval<__type10>())) __type11;
      typedef typename pythonic::assignable<__type11>::type __type12;
      typedef __type12 __type13;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type1>::type>::type __type14;
      typedef __type14 __type15;
      typedef decltype(pythonic::types::as_const(std::declval<__type15>())) __type16;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type16>::type>::type __type17;
      typedef indexable_container<__type4, typename std::remove_reference<__type17>::type> __type18;
      typedef typename __combined<__type14,__type18>::type __type19;
      typedef __type19 __type20;
      typedef decltype(std::declval<__type2>()(std::declval<__type20>())) __type21;
      typedef typename pythonic::assignable<__type21>::type __type22;
      typedef __type22 __type23;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type0>::type>::type __type24;
      typedef __type24 __type25;
      typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, std::declval<__type25>())) __type26;
      typedef decltype(pythonic::types::as_const(std::declval<__type26>())) __type27;
      typedef typename std::tuple_element<3,typename std::remove_reference<__type27>::type>::type __type28;
      typedef typename pythonic::assignable<__type28>::type __type29;
      typedef __type29 __type30;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>(), std::declval<__type23>(), std::declval<__type30>())) __type31;
      typedef decltype(pythonic::builtins::getattr(pythonic::types::attr::DTYPE{}, std::declval<__type25>())) __type33;
      typedef decltype(std::declval<__type0>()(std::declval<__type31>(), std::declval<__type33>())) __type34;
      typedef typename pythonic::assignable<__type34>::type __type35;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::int_{})>::type>::type __type36;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::round{})>::type>::type __type37;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::abs{})>::type>::type __type38;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type4>::type>::type __type39;
      typedef __type39 __type40;
      typedef decltype(pythonic::types::as_const(std::declval<__type40>())) __type41;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::range{})>::type>::type __type42;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type27>::type>::type __type43;
      typedef typename pythonic::lazy<__type43>::type __type44;
      typedef __type44 __type45;
      typedef decltype(std::declval<__type42>()(std::declval<__type45>())) __type46;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type46>::type::iterator>::value_type>::type __type47;
      typedef __type47 __type48;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type27>::type>::type __type49;
      typedef typename pythonic::lazy<__type49>::type __type50;
      typedef __type50 __type51;
      typedef decltype(std::declval<__type42>()(std::declval<__type51>())) __type52;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type52>::type::iterator>::value_type>::type __type53;
      typedef __type53 __type54;
      typedef typename std::tuple_element<2,typename std::remove_reference<__type27>::type>::type __type55;
      typedef typename pythonic::lazy<__type55>::type __type56;
      typedef __type56 __type57;
      typedef decltype(std::declval<__type42>()(std::declval<__type57>())) __type58;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type58>::type::iterator>::value_type>::type __type59;
      typedef __type59 __type60;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type48>(), std::declval<__type54>(), std::declval<__type60>())) __type61;
      typedef decltype(std::declval<__type41>()[std::declval<__type61>()]) __type62;
      typedef decltype(std::declval<__type38>()(std::declval<__type62>())) __type63;
      typedef typename pythonic::assignable<__type7>::type __type64;
      typedef __type64 __type65;
      typedef decltype(pythonic::operator_::div(std::declval<__type63>(), std::declval<__type65>())) __type66;
      typedef decltype(std::declval<__type37>()(std::declval<__type66>())) __type67;
      typedef decltype(std::declval<__type36>()(std::declval<__type67>())) __type68;
      typedef typename pythonic::lazy<__type68>::type __type69;
      typedef long __type71;
      typedef decltype(pythonic::operator_::sub(std::declval<__type13>(), std::declval<__type71>())) __type72;
      typedef typename pythonic::lazy<__type72>::type __type73;
      typedef typename __combined<__type69,__type73>::type __type74;
      typedef __type74 __type75;
      typedef decltype(pythonic::operator_::sub(std::declval<__type23>(), std::declval<__type71>())) __type77;
      typedef typename pythonic::lazy<__type77>::type __type78;
      typedef __type78 __type79;
      typedef typename std::remove_cv<typename std::remove_reference<decltype(pythonic::builtins::functor::enumerate{})>::type>::type __type80;
      typedef decltype(pythonic::types::as_const(std::declval<__type25>())) __type82;
      typedef pythonic::types::contiguous_slice __type86;
      typedef decltype(std::declval<__type82>()(std::declval<__type48>(), std::declval<__type54>(), std::declval<__type60>(), std::declval<__type86>())) __type87;
      typedef typename pythonic::lazy<__type87>::type __type88;
      typedef __type88 __type89;
      typedef decltype(pythonic::operator_::mul(std::declval<__type71>(), std::declval<__type89>())) __type90;
      typedef typename pythonic::lazy<__type90>::type __type91;
      typedef typename __combined<__type88,__type91>::type __type92;
      typedef __type92 __type93;
      typedef decltype(std::declval<__type80>()(std::declval<__type93>())) __type94;
      typedef typename std::remove_cv<typename std::iterator_traits<typename std::remove_reference<__type94>::type::iterator>::value_type>::type __type95;
      typedef __type95 __type96;
      typedef decltype(pythonic::types::as_const(std::declval<__type96>())) __type97;
      typedef typename std::tuple_element<0,typename std::remove_reference<__type97>::type>::type __type98;
      typedef typename pythonic::lazy<__type98>::type __type99;
      typedef __type99 __type100;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type75>(), std::declval<__type79>(), std::declval<__type100>())) __type101;
      typedef indexable<__type101> __type102;
      typedef typename std::remove_cv<typename std::remove_reference<argument_type5>::type>::type __type104;
      typedef __type104 __type105;
      typedef decltype(pythonic::types::as_const(std::declval<__type105>())) __type106;
      typedef decltype(std::declval<__type106>()[std::declval<__type61>()]) __type111;
      typedef typename pythonic::assignable<__type111>::type __type112;
      typedef __type112 __type113;
      typedef typename pythonic::assignable<__type17>::type __type114;
      typedef __type114 __type115;
      typedef decltype(pythonic::operator_::div(std::declval<__type113>(), std::declval<__type115>())) __type116;
      typedef decltype(std::declval<__type36>()(std::declval<__type116>())) __type117;
      typedef typename pythonic::assignable<__type117>::type __type118;
      typedef __type118 __type119;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type75>(), std::declval<__type119>(), std::declval<__type100>())) __type128;
      typedef indexable<__type128> __type129;
      typedef decltype(pythonic::operator_::add(std::declval<__type119>(), std::declval<__type71>())) __type132;
      typedef decltype(pythonic::types::make_tuple(std::declval<__type75>(), std::declval<__type132>(), std::declval<__type100>())) __type134;
      typedef indexable<__type134> __type135;
      typedef typename std::tuple_element<1,typename std::remove_reference<__type97>::type>::type __type138;
      typedef typename pythonic::lazy<__type138>::type __type139;
      typedef __type139 __type140;
      typedef container<typename std::remove_reference<__type140>::type> __type141;
      typedef decltype(pythonic::types::as_const(std::declval<__type20>())) __type144;
      typedef decltype(std::declval<__type144>()[std::declval<__type119>()]) __type146;
      typedef decltype(pythonic::operator_::sub(std::declval<__type113>(), std::declval<__type146>())) __type147;
      typedef decltype(pythonic::operator_::div(std::declval<__type147>(), std::declval<__type115>())) __type149;
      typedef typename pythonic::assignable<__type149>::type __type150;
      typedef __type150 __type151;
      typedef decltype(pythonic::operator_::sub(std::declval<__type71>(), std::declval<__type151>())) __type152;
      typedef typename pythonic::assignable<__type138>::type __type156;
      typedef __type156 __type157;
      typedef decltype(pythonic::operator_::mul(std::declval<__type152>(), std::declval<__type157>())) __type158;
      typedef container<typename std::remove_reference<__type158>::type> __type159;
      typedef decltype(pythonic::operator_::mul(std::declval<__type151>(), std::declval<__type157>())) __type162;
      typedef container<typename std::remove_reference<__type162>::type> __type163;
      typedef typename __combined<__type35,__type102,__type129,__type135,__type141,__type159,__type163>::type __type164;
      typedef typename pythonic::assignable<__type164>::type __type165;
      typedef typename pythonic::lazy<__type92>::type __type166;
      typedef typename pythonic::lazy<__type74>::type __type167;
      typedef typename pythonic::assignable<__type150>::type __type168;
      typedef decltype(pythonic::operator_::add(std::declval<__type30>(), std::declval<__type71>())) __type172;
      typedef decltype(pythonic::operator_::functor::floordiv()(std::declval<__type172>(), std::declval<__type71>())) __type173;
      typedef typename pythonic::assignable<__type173>::type __type174;
      typedef __type174 __type175;
      typedef decltype(std::declval<__type1>()(std::declval<__type13>(), std::declval<__type23>(), std::declval<__type175>())) __type176;
      typedef decltype(std::declval<__type0>()(std::declval<__type176>())) __type177;
      typedef typename pythonic::assignable<__type177>::type __type178;
      typedef __type164 __type179;
      typedef decltype(pythonic::types::as_const(std::declval<__type179>())) __type180;
      typedef decltype(std::declval<__type180>()(std::declval<__type86>(), std::declval<__type86>(), std::declval<__type71>())) __type181;
      typedef container<typename std::remove_reference<__type181>::type> __type182;
      typedef decltype(std::declval<__type180>()(std::declval<__type86>(), std::declval<__type86>(), std::declval<__type86>())) __type185;
      typedef pythonic::types::slice __type188;
      typedef decltype(std::declval<__type180>()(std::declval<__type86>(), std::declval<__type86>(), std::declval<__type188>())) __type189;
      typedef decltype(pythonic::operator_::add(std::declval<__type185>(), std::declval<__type189>())) __type190;
      typedef container<typename std::remove_reference<__type190>::type> __type191;
      typedef typename __combined<__type178,__type182,__type191>::type __type192;
      typedef typename pythonic::assignable<__type192>::type __type193;
      typename pythonic::assignable_noescape<decltype(std::get<1>(pythonic::types::as_const(khs)))>::type deltakh = std::get<1>(pythonic::types::as_const(khs));
      typename pythonic::assignable_noescape<decltype(std::get<1>(pythonic::types::as_const(kzs)))>::type deltakz = std::get<1>(pythonic::types::as_const(kzs));
      typename pythonic::assignable_noescape<decltype(pythonic::builtins::functor::len{}(khs))>::type nkh = pythonic::builtins::functor::len{}(khs);
      typename pythonic::assignable_noescape<decltype(pythonic::builtins::functor::len{}(kzs))>::type nkz = pythonic::builtins::functor::len{}(kzs);
      typename pythonic::lazy<decltype(std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega))))>::type nk0 = std::get<0>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega)));
      typename pythonic::lazy<decltype(std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega))))>::type nk1 = std::get<1>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega)));
      typename pythonic::lazy<decltype(std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega))))>::type nk2 = std::get<2>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega)));
      typename pythonic::assignable_noescape<decltype(std::get<3>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega))))>::type nomega = std::get<3>(pythonic::types::as_const(pythonic::builtins::getattr(pythonic::types::attr::SHAPE{}, field_k0k1k2omega)));
      __type165 spectrum_kzkhomega = pythonic::numpy::functor::zeros{}(pythonic::builtins::pythran::functor::make_shape{}(nkz, nkh, nomega), pythonic::builtins::getattr(pythonic::types::attr::DTYPE{}, field_k0k1k2omega));
      {
        long  __target139658372192720 = nk0;
        for (long  ik0=0L; ik0 < __target139658372192720; ik0 += 1L)
        {
          {
            long  __target139658367696512 = nk1;
            for (long  ik1=0L; ik1 < __target139658367696512; ik1 += 1L)
            {
              {
                long  __target139658368382672 = nk2;
                for (long  ik2=0L; ik2 < __target139658368382672; ik2 += 1L)
                {
                  __type166 values = pythonic::types::as_const(field_k0k1k2omega)(ik0,ik1,ik2,pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None));
                  if (pythonic::operator_::ne(pythonic::types::as_const(KX)[pythonic::types::make_tuple(ik0, ik1, ik2)], 0.0))
                  {
                    values = pythonic::operator_::mul(2L, values);
                  }
                  typename pythonic::assignable_noescape<decltype(pythonic::types::as_const(KH)[pythonic::types::make_tuple(ik0, ik1, ik2)])>::type kappa = pythonic::types::as_const(KH)[pythonic::types::make_tuple(ik0, ik1, ik2)];
                  typename pythonic::assignable_noescape<decltype(pythonic::builtins::functor::int_{}(pythonic::operator_::div(kappa, deltakh)))>::type ikh = pythonic::builtins::functor::int_{}(pythonic::operator_::div(kappa, deltakh));
                  __type167 ikz = pythonic::builtins::functor::int_{}(pythonic::builtins::functor::round{}(pythonic::operator_::div(pythonic::builtins::functor::abs{}(pythonic::types::as_const(KZ)[pythonic::types::make_tuple(ik0, ik1, ik2)]), deltakz)));
                  if (pythonic::operator_::ge(ikz, pythonic::operator_::sub(nkz, 1L)))
                  {
                    ikz = pythonic::operator_::sub(nkz, 1L);
                  }
                  {
                    __type168 coef_share;
                    if (pythonic::operator_::ge(ikh, pythonic::operator_::sub(nkh, 1L)))
                    {
                      typename pythonic::lazy<decltype(pythonic::operator_::sub(nkh, 1L))>::type ikh_ = pythonic::operator_::sub(nkh, 1L);
                      {
                        for (auto&& __tuple0: pythonic::builtins::functor::enumerate{}(values))
                        {
                          typename pythonic::lazy<decltype(std::get<1>(pythonic::types::as_const(__tuple0)))>::type value = std::get<1>(pythonic::types::as_const(__tuple0));
                          typename pythonic::lazy<decltype(std::get<0>(pythonic::types::as_const(__tuple0)))>::type i = std::get<0>(pythonic::types::as_const(__tuple0));
                          pythonic::types::as_const(spectrum_kzkhomega)[pythonic::types::make_tuple(ikz, ikh_, i)] += value;
                        }
                      }
                    }
                    else
                    {
                      coef_share = pythonic::operator_::div(pythonic::operator_::sub(kappa, pythonic::types::as_const(khs)[ikh]), deltakh);
                      {
                        for (auto&& __tuple1: pythonic::builtins::functor::enumerate{}(values))
                        {
                          typename pythonic::assignable_noescape<decltype(std::get<1>(pythonic::types::as_const(__tuple1)))>::type value_ = std::get<1>(pythonic::types::as_const(__tuple1));
                          typename pythonic::lazy<decltype(std::get<0>(pythonic::types::as_const(__tuple1)))>::type i_ = std::get<0>(pythonic::types::as_const(__tuple1));
                          pythonic::types::as_const(spectrum_kzkhomega)[pythonic::types::make_tuple(ikz, ikh, i_)] += pythonic::operator_::mul(pythonic::operator_::sub(1L, coef_share), value_);
                          pythonic::types::as_const(spectrum_kzkhomega)[pythonic::types::make_tuple(ikz, pythonic::operator_::add(ikh, 1L), i_)] += pythonic::operator_::mul(coef_share, value_);
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
      typename pythonic::assignable_noescape<decltype(pythonic::operator_::functor::floordiv()(pythonic::operator_::add(nomega, 1L), 2L))>::type nomega_ = pythonic::operator_::functor::floordiv()(pythonic::operator_::add(nomega, 1L), 2L);
      __type193 spectrum_onesided = pythonic::numpy::functor::zeros{}(pythonic::builtins::pythran::functor::make_shape{}(nkz, nkh, nomega_));
      spectrum_onesided(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),0L) = pythonic::types::as_const(spectrum_kzkhomega)(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),0L);
      spectrum_onesided(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(1L,pythonic::builtins::None)) = pythonic::operator_::add(pythonic::types::as_const(spectrum_kzkhomega)(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(1L,nomega_)), pythonic::types::as_const(spectrum_kzkhomega)(pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::contiguous_slice(pythonic::builtins::None,pythonic::builtins::None),pythonic::types::slice(-1L,pythonic::operator_::neg(nomega_),-1L)));
      return pythonic::operator_::div(spectrum_onesided, pythonic::operator_::mul(deltakz, deltakh));
    }
  }
}
#include <pythonic/python/exception_handler.hpp>
#ifdef ENABLE_PYTHON_MODULE
static PyObject* __transonic__ = to_python(__pythran_spatiotemporal_spectra::__transonic__()());
inline
typename __pythran_spatiotemporal_spectra::compute_spectrum_kzkhomega::type<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>::result_type compute_spectrum_kzkhomega0(pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long,long>>&& field_k0k1k2omega, pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& khs, pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& kzs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KX, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KZ, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KH) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::compute_spectrum_kzkhomega()(field_k0k1k2omega, khs, kzs, KX, KZ, KH);
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
typename __pythran_spatiotemporal_spectra::compute_spectrum_kzkhomega::type<pythonic::types::ndarray<float,pythonic::types::pshape<long,long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>::result_type compute_spectrum_kzkhomega1(pythonic::types::ndarray<float,pythonic::types::pshape<long,long,long,long>>&& field_k0k1k2omega, pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& khs, pythonic::types::ndarray<double,pythonic::types::pshape<long>>&& kzs, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KX, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KZ, pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>&& KH) 
{
  
                            PyThreadState *_save = PyEval_SaveThread();
                            try {
                                auto res = __pythran_spatiotemporal_spectra::compute_spectrum_kzkhomega()(field_k0k1k2omega, khs, kzs, KX, KZ, KH);
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
__pythran_wrap_compute_spectrum_kzkhomega0(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[6+1];
    
    char const* keywords[] = {"field_k0k1k2omega", "khs", "kzs", "KX", "KZ", "KH",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[5]))
        return to_python(compute_spectrum_kzkhomega0(from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[3]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[4]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[5])));
    else {
        return nullptr;
    }
}

static PyObject *
__pythran_wrap_compute_spectrum_kzkhomega1(PyObject *self, PyObject *args, PyObject *kw)
{
    PyObject* args_obj[6+1];
    
    char const* keywords[] = {"field_k0k1k2omega", "khs", "kzs", "KX", "KZ", "KH",  nullptr};
    if(! PyArg_ParseTupleAndKeywords(args, kw, "OOOOOO",
                                     (char**)keywords , &args_obj[0], &args_obj[1], &args_obj[2], &args_obj[3], &args_obj[4], &args_obj[5]))
        return nullptr;
    if(is_convertible<pythonic::types::ndarray<float,pythonic::types::pshape<long,long,long,long>>>(args_obj[0]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[1]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[2]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[3]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[4]) && is_convertible<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[5]))
        return to_python(compute_spectrum_kzkhomega1(from_python<pythonic::types::ndarray<float,pythonic::types::pshape<long,long,long,long>>>(args_obj[0]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[1]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long>>>(args_obj[2]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[3]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[4]), from_python<pythonic::types::ndarray<double,pythonic::types::pshape<long,long,long>>>(args_obj[5])));
    else {
        return nullptr;
    }
}

            static PyObject *
            __pythran_wrapall_compute_spectrum_kzkhomega(PyObject *self, PyObject *args, PyObject *kw)
            {
                return pythonic::handle_python_exception([self, args, kw]()
                -> PyObject* {

if(PyObject* obj = __pythran_wrap_compute_spectrum_kzkhomega0(self, args, kw))
    return obj;
PyErr_Clear();


if(PyObject* obj = __pythran_wrap_compute_spectrum_kzkhomega1(self, args, kw))
    return obj;
PyErr_Clear();

                return pythonic::python::raise_invalid_argument(
                               "compute_spectrum_kzkhomega", "\n""    - compute_spectrum_kzkhomega(float64[:,:,:,:], float64[:], float64[:], float64[:,:,:], float64[:,:,:], float64[:,:,:])\n""    - compute_spectrum_kzkhomega(float32[:,:,:,:], float64[:], float64[:], float64[:,:,:], float64[:,:,:], float64[:,:,:])", args, kw);
                });
            }


static PyMethodDef Methods[] = {
    {
    "compute_spectrum_kzkhomega",
    (PyCFunction)__pythran_wrapall_compute_spectrum_kzkhomega,
    METH_VARARGS | METH_KEYWORDS,
    "Compute the kz-kh-omega spectrum.\n""\n""    Supported prototypes:\n""\n""    - compute_spectrum_kzkhomega(float64[:,:,:,:], float64[:], float64[:], float64[:,:,:], float64[:,:,:], float64[:,:,:])\n""    - compute_spectrum_kzkhomega(float32[:,:,:,:], float64[:], float64[:], float64[:,:,:], float64[:,:,:], float64[:,:,:])"},
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
                                      "0.13.1",
                                      "2023-05-24 11:29:42.784068",
                                      "042f493953b15f89acbd2c492e2acc0015a0f87c0eea68ae05a7ad60dc111af2");
    if(! theDoc)
        PYTHRAN_RETURN;
    PyModule_AddObject(theModule,
                       "__pythran__",
                       theDoc);

    PyModule_AddObject(theModule, "__transonic__", __transonic__);
    PYTHRAN_RETURN;
}

#endif