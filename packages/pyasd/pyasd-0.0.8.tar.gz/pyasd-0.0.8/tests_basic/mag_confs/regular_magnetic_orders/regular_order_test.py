#!/usr/bin/env python

import numpy as np
from asd.core.geometry import build_latt
from asd.core.spin_configurations import *
from asd.core.topological_charge import calc_topo_chg
from asd.utility.spin_visualize_tools import *
from asd.utility.Swq import *
import itertools

lat_type = 'triangular'
lat_type = 'honeycomb'

conf_name = 'FM'
conf_name = 'Tetrahedra'
conf_name = 'Cubic'
#conf_name = 'super-Neel'

nx=40
ny=40
latt,sites = build_latt(lat_type,nx,ny,1,return_neigh=False)
nat = sites.shape[2]
sites_cart = np.dot(sites,latt)
quiver_kws = dict(scale=1.2,units='x',pivot='mid')
 
spin_plot_kws=dict(
scatter_size=20,
show=False,
quiver_kws=quiver_kws,
colorful_quiver=True,
#colorful_quiver=False,
superlatt=np.dot(np.diag([nx,ny]),latt),
colorbar_axes_position=[0.75,0.5,0.02,0.25],
colorbar_orientation='vertical',
#colorbar_shrink=0.5,
)

if conf_name=='super-Neel':  spin_plot_kws.update(colorful_quiver=False)



if __name__=='__main__':
    for conf_name in ['Tetrahedra','Cubic']:
        sp_lat_uc = regular_order(lat_type,conf_name)
        sp_lat = np.zeros((nx,ny,nat,3))

        rx=range(0,nx,2)
        ry=range(0,ny,2)
        for i,j in itertools.product(rx,ry):
            sp_lat[i:i+2,j:j+2] = sp_lat_uc

        Q=calc_topo_chg(sp_lat,sites_cart)
        title = '{} order, Q = {:10.5f}'.format(conf_name, Q)
        spin_plot_kws.update(title=title)

        plot_spin_2d(sites_cart,sp_lat,**spin_plot_kws)

    plt.show()

    exit()
    spins = sp_lat.reshape(-1,3)
    nqx=100
    nqy=100
    qpt_cart = gen_uniform_qmesh(nqx,nqy,bound=4)
    S_vector = calc_static_structure_factor(spins,sites_cart.reshape(-1,2),qpt_cart)
    plot_struct_factor(qpt_cart,S_vector,scatter_size=2,nqx=nqx,nqy=nqy)
