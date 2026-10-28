#include "pricer.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>
namespace refinery {
namespace {
constexpr double pi=3.14159265358979323846;
double cdf(double x) { return 0.5*(1.0+std::erf(x/std::sqrt(2.0))); }
double pdf(double x) { return std::exp(-0.5*x*x)/std::sqrt(2.0*pi); }
}
Quote quote(Model model,double f,double k,double vol,double t,double r,bool call) {
    if (!std::isfinite(f)||!std::isfinite(k)||!std::isfinite(vol)||!std::isfinite(t)||!std::isfinite(r)||vol<0||t<0)
        throw std::invalid_argument("Finite inputs, non-negative volatility and expiry required");
    if(model==Model::Black76 && (f<=0||k<=0)) throw std::invalid_argument("Black76 requires positive forward and strike");
    const double sign=call?1.0:-1.0, df=std::exp(-r*t);
    if(t==0 || vol==0) {
        const double intrinsic=std::max(sign*(f-k),0.0),p=df*intrinsic;
        const double delta=df*sign*(sign*(f-k)>0?1.0:(f==k?0.5:0.0));
        // Gamma/vega at the expiry kink are undefined. API explicitly uses zero.
        return {p,delta,0,0,-r*p,-t*p};
    }
    const double root=std::sqrt(t),s=vol*root;
    double price,delta,gamma,vega,dtime;
    if(model==Model::Bachelier) {
        const double d=(f-k)/s;
        const double c=df*((f-k)*cdf(d)+s*pdf(d));
        price=call?c:c-df*(f-k); // same parity arithmetic as the Python reference
        delta=df*(cdf(d)-(call?0.0:1.0));gamma=df*pdf(d)/s;
        vega=df*root*pdf(d);dtime=df*vol*pdf(d)/(2*root)-r*price;
    } else {
        const double d1=(std::log(f/k)+s*s/2)/s,d2=d1-s;
        price=call?df*(f*cdf(d1)-k*cdf(d2)):df*(k*cdf(-d2)-f*cdf(-d1));
        delta=df*(cdf(d1)-(call?0.0:1.0));gamma=df*pdf(d1)/(f*s);
        vega=df*f*root*pdf(d1);dtime=df*f*vol*pdf(d1)/(2*root)-r*price;
    }
    return {price,delta,gamma,vega,dtime,-t*price};
}
double zero_cost_call(Model model,double f,double put,double vol,double t,double r) {
    const double target=quote(model,f,put,vol,t,r,false).price;
    double lo=f,hi=f*20+100;
    if(quote(model,f,lo,vol,t,r,true).price<target || quote(model,f,hi,vol,t,r,true).price>target)
        throw std::invalid_argument("No zero-cost call in reference bracket");
    for(int i=0;i<200;++i) {
        double mid=(lo+hi)/2;
        if(quote(model,f,mid,vol,t,r,true).price>target) lo=mid;else hi=mid;
    }
    return (lo+hi)/2;
}
}
