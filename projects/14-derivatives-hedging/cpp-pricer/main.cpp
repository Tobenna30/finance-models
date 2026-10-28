#include "pricer.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using refinery::Model;
int main() {
 try {
    std::cout<<std::setprecision(17);
    std::string op;
    while(std::cin>>op) {
        if(op=="price"||op=="strike") {
            char model;double f,k,v,t,r;int call;
            if(!(std::cin>>model>>f>>k>>v>>t>>r>>call))throw std::invalid_argument("Incomplete quote");
            if(model!='N'&&model!='B')throw std::invalid_argument("Model N or B required");
            Model m=model=='N'?Model::Bachelier:Model::Black76;
            if(op=="strike") {std::cout<<refinery::zero_cost_call(m,f,k,v,t,r)<<'\n';continue;}
            auto q=refinery::quote(m,f,k,v,t,r,call!=0);
            std::cout<<q.price<<' '<<q.delta<<' '<<q.gamma<<' '<<q.vega<<' '<<q.dprice_dt<<' '<<q.rho<<'\n';
        } else if(op=="mc") {
            int n,repeats;double cover,budget;
            if(!(std::cin>>n>>repeats>>cover>>budget)||n<=0||repeats<=0||budget<=0)throw std::invalid_argument("Invalid MC dimensions");
            // Each product: forward, normal vol * sqrt(mean expiry), annual barrels,
            // January put/call. Matches the existing stylised annual Python stress.
            std::array<std::array<double,5>,2> p{};
            for(auto& product:p)for(double& v:product)if(!(std::cin>>v))throw std::invalid_argument("Incomplete product");
            std::vector<std::array<double,2>> shocks(n);
            for(auto& z:shocks)if(!(std::cin>>z[0]>>z[1]))throw std::invalid_argument("Incomplete shocks");
            std::vector<double> timings,u(n),h(n);double um=0,hm=0,up=0,hp=0;
            for(int repeat=0;repeat<repeats;++repeat) {
                auto start=std::chrono::steady_clock::now();
                for(int i=0;i<n;++i) {
                    double unhedged=0,hedged=0;
                    for(int j=0;j<2;++j) {
                        const auto& a=p[j];double x=a[0]+a[1]*shocks[i][j];
                        double payoff=std::max(a[3]-x,0.0)-std::max(x-a[4],0.0);
                        unhedged+=a[2]*x;hedged+=a[2]*x+cover*a[2]*payoff;
                    }
                    u[i]=unhedged/1e6/budget-1;h[i]=hedged/1e6/budget-1;
                }
                std::sort(u.begin(),u.end());std::sort(h.begin(),h.end());
                um=std::accumulate(u.begin(),u.end(),0.0)/n;hm=std::accumulate(h.begin(),h.end(),0.0)/n;
                up=u[static_cast<int>(.05*n)];hp=h[static_cast<int>(.05*n)];
                timings.push_back(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count());
            }
            std::sort(timings.begin(),timings.end());
            std::cout<<um<<' '<<hm<<' '<<up<<' '<<hp<<' '<<timings[timings.size()/2]<<'\n';
        } else throw std::invalid_argument("Unknown command");
    }
 } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 2;}
}
