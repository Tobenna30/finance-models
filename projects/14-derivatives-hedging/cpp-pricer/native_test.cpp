#include "pricer.hpp"
#include <cmath>
#include <stdexcept>
#include <iostream>
int main() {
 int checks=0;
 for(auto m:{refinery::Model::Bachelier,refinery::Model::Black76}) {
    auto c=refinery::quote(m,40,38,.4,1,.04,true);
    auto p=refinery::quote(m,40,38,.4,1,.04,false);
    if(std::abs(c.price-p.price-2*std::exp(-.04))>1e-12)return 1;++checks;
    if(c.gamma<0||c.vega<0)return 2;++checks;
    if(refinery::quote(m,40,38,.4,0,.04,true).price!=2)return 3;++checks;
 }
 try {refinery::quote(refinery::Model::Black76,-1,1,.4,1,0,true);return 4;}catch(const std::invalid_argument&){++checks;}
 try {refinery::quote(refinery::Model::Bachelier,1,1,-.4,1,0,true);return 5;}catch(const std::invalid_argument&){++checks;}
 std::cout<<checks<<" native assertions passed\n";
}
