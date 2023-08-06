#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2021-2023 Hao Zhang<zh970205@mail.ustc.edu.cn>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import TAT
import tetragono as tet
from tetragono.common_tensor.tensor_toolkit import half_reverse


def abstract_state(L1, L2, t, J, mu, side=1):
    """
    Create density matrix of tJ model state.

    Parameters
    ----------
    L1, L2 : int
        The lattice size.
    T : int
        The half particle number.
    t, J : float
        tJ model parameters.
    mu : float
        The chemical potential.
    side : 1 | 2, default=1
        The Hamiltonian should apply to single side or both side of density matrix.
    """
    if side not in [1, 2]:
        raise RuntimeError("side should be either 1 or 2")
    state = tet.AbstractState(TAT.FermiU1.D.Tensor, L1, L2)
    state.total_symmetry = (0, 0)
    for l1 in range(L1):
        for l2 in range(L2):
            state.physics_edges[(l1, l2, 0)] = tet.common_tensor.FermiU1_tJ.EF[0]
            state.physics_edges[(l1, l2, 1)] = tet.common_tensor.FermiU1_tJ.ET[0]
    CC = tet.common_tensor.FermiU1_tJ.CC.to(float)
    SS = tet.common_tensor.FermiU1_tJ.SS.to(float)
    nn = tet.common_tensor.FermiU1_tJ.nn.to(float)
    n = tet.common_tensor.FermiU1_tJ.n.to(float)
    H = (-t) * CC + (J / 2) * (SS - nn / 4)
    single_site = -mu * n
    H_double_side = [H, half_reverse(H.conjugate())]
    single_site_double_side = [single_site, half_reverse(single_site.conjugate())]
    for layer in range(side):
        # The hamiltonian in second layer is conjugate and half reverse of the first layer.
        for l1 in range(L1):
            for l2 in range(L2):
                state.hamiltonians[
                    (l1, l2, layer),
                ] = single_site_double_side[layer]
                if l1 != 0:
                    state.hamiltonians[(l1 - 1, l2, layer), (l1, l2, layer)] = H_double_side[layer]
                if l2 != 0:
                    state.hamiltonians[(l1, l2 - 1, layer), (l1, l2, layer)] = H_double_side[layer]
    return state


def abstract_lattice(L1, L2, t, J, mu, side=1):
    """
    Create density matrix of tJ model lattice.

    Parameters
    ----------
    L1, L2 : int
        The lattice size.
    t, J : float
        tJ model parameters.
    mu : float
        The chemical potential.
    side : 1 | 2, default=1
        The Hamiltonian should apply to single side or both side of density matrix.
    """
    state = tet.AbstractLattice(abstract_state(L1, L2, t, J, mu, side=side))
    state.virtual_bond["R"] = state.virtual_bond["D"] = [((0, 0), 1)]
    return state
