# GridCal
# Copyright (C) 2022 Santiago Peñate Vera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import numpy as np
import pandas as pd
from GridCal.Engine.Simulations.result_types import ResultTypes
from GridCal.Engine.Simulations.results_table import ResultsTable
from GridCal.Engine.Simulations.results_template import ResultsTemplate
# from GridCal.Engine.Core.multi_circuit import MultiCircuit


class NumericPowerFlowResults:

    def __init__(self, V, converged, norm_f, Scalc, ma=None, theta=None, Beq=None, Ybus=None, Yf=None, Yt=None,
                 iterations=0, elapsed=0, method=None):
        """
        Object to store the results returned by a numeric power flow routine
        :param V: Voltage vector
        :param converged: converged?
        :param norm_f: error
        :param Scalc: Calculated power vector
        :param ma: Tap modules vector for all the branches
        :param theta: Tap angles vector for all the branches
        :param Beq: Equivalent susceptance vector for all the branches
        :param Ybus: Admittance matrix
        :param Yf: Admittance matrix of the "from" buses
        :param Yt: Admittance matrix of the "to" buses
        :param iterations: number of iterations
        :param elapsed: time elapsed
        """
        self.V = V
        self.converged = converged
        self.norm_f = norm_f
        self.Scalc = Scalc
        self.ma = ma
        self.theta = theta
        self.Beq = Beq
        self.Ybus = Ybus
        self.Yf = Yf
        self.Yt = Yt
        self.iterations = iterations
        self.elapsed = elapsed
        self.method = None


class PowerFlowResults(ResultsTemplate):

    def __init__(self, n, m, n_tr, n_hvdc, bus_names, branch_names, transformer_names, hvdc_names, bus_types,
                 area_names=None):
        """
        A **PowerFlowResults** object is create as an attribute of the
        :ref:`PowerFlowMP<pf_mp>` (as PowerFlowMP.results) when the power flow is run. It
        provides access to the simulation results through its class attributes.
        :param n:
        :param m:
        :param n_tr:
        :param n_hvdc:
        :param bus_names:
        :param branch_names:
        :param transformer_names:
        :param hvdc_names:
        :param bus_types:
        """

        ResultsTemplate.__init__(self,
                                 name='Power flow',
                                 available_results={ResultTypes.BusResults: [ResultTypes.BusVoltageModule,
                                                                             ResultTypes.BusVoltageAngle,
                                                                             ResultTypes.BusActivePower,
                                                                             ResultTypes.BusReactivePower],

                                                    ResultTypes.BranchResults: [ResultTypes.BranchActivePowerFrom,
                                                                                ResultTypes.BranchReactivePowerFrom,
                                                                                ResultTypes.BranchActivePowerTo,
                                                                                ResultTypes.BranchReactivePowerTo,

                                                                                ResultTypes.BranchActiveCurrentFrom,
                                                                                ResultTypes.BranchReactiveCurrentFrom,
                                                                                ResultTypes.BranchActiveCurrentTo,
                                                                                ResultTypes.BranchReactiveCurrentTo,

                                                                                ResultTypes.BranchTapModule,
                                                                                ResultTypes.BranchTapAngle,
                                                                                ResultTypes.BranchBeq,

                                                                                ResultTypes.BranchLoading,
                                                                                ResultTypes.BranchActiveLosses,
                                                                                ResultTypes.BranchReactiveLosses,
                                                                                ResultTypes.BranchActiveLossesPercentage,
                                                                                ResultTypes.BranchVoltage,
                                                                                ResultTypes.BranchAngles],

                                                    ResultTypes.HvdcResults: [ResultTypes.HvdcLosses,
                                                                              ResultTypes.HvdcPowerFrom,
                                                                              ResultTypes.HvdcPowerTo],

                                                    ResultTypes.AreaResults: [ResultTypes.InterAreaExchange,
                                                                              ResultTypes.ActivePowerFlowPerArea,
                                                                              ResultTypes.LossesPerArea,
                                                                              ResultTypes.LossesPercentPerArea,
                                                                              ResultTypes.LossesPerGenPerArea]},
                                 data_variables=['bus_types',
                                                 'bus_names',
                                                 'branch_names',
                                                 'transformer_names',
                                                 'hvdc_names',
                                                 'Sbus',
                                                 'voltage',
                                                 'Sf',
                                                 'St',
                                                 'If',
                                                 'It',
                                                 'tap_module',
                                                 'theta',
                                                 'Beq',
                                                 'Vbranch',
                                                 'loading',
                                                 'losses',
                                                 'hvdc_losses',
                                                 'hvdc_Pf',
                                                 'hvdc_Pt',
                                                 'hvdc_loading']
                                 )

        self.n = n
        self.m = m
        self.n_tr = n_tr
        self.n_hvdc = n_hvdc

        self.bus_types = bus_types

        self.bus_names = bus_names
        self.branch_names = branch_names
        self.transformer_names = transformer_names
        self.hvdc_names = hvdc_names

        # vars for the inter-area computation
        self.F = None
        self.T = None
        self.hvdc_F = None
        self.hvdc_T = None
        self.bus_area_indices = None
        self.area_names = area_names

        self.Sbus = np.zeros(n, dtype=complex)

        self.voltage = np.zeros(n, dtype=complex)

        self.Sf = np.zeros(m, dtype=complex)
        self.St = np.zeros(m, dtype=complex)

        self.If = np.zeros(m, dtype=complex)
        self.It = np.zeros(m, dtype=complex)

        self.tap_module = np.zeros(m, dtype=float)
        self.theta = np.zeros(m, dtype=float)
        self.Beq = np.zeros(m, dtype=float)

        self.Vbranch = np.zeros(m, dtype=complex)

        self.loading = np.zeros(m, dtype=complex)

        self.losses = np.zeros(m, dtype=complex)

        self.hvdc_losses = np.zeros(self.n_hvdc)

        self.hvdc_Pf = np.zeros(self.n_hvdc)

        self.hvdc_Pt = np.zeros(self.n_hvdc)

        self.hvdc_loading = np.zeros(self.n_hvdc)

        self.plot_bars_limit = 100

        self.convergence_reports = list()

    def apply_new_rates(self, nc: "SnapshotData"):
        rates = nc.Rates
        self.loading = self.Sf / (rates + 1e-9)

    def fill_circuit_info(self, grid: "MultiCircuit"):

        area_dict = {elm: i for i, elm in enumerate(grid.get_areas())}
        bus_dict = grid.get_bus_index_dict()

        self.area_names = [a.name for a in grid.get_areas()]
        self.bus_area_indices = np.array([area_dict[b.area] for b in grid.buses])

        branches = grid.get_branches_wo_hvdc()
        self.F = np.zeros(len(branches), dtype=int)
        self.T = np.zeros(len(branches), dtype=int)
        for k, elm in enumerate(branches):
            self.F[k] = bus_dict[elm.bus_from]
            self.T[k] = bus_dict[elm.bus_to]

        hvdc = grid.get_hvdc()
        self.hvdc_F = np.zeros(len(hvdc), dtype=int)
        self.hvdc_T = np.zeros(len(hvdc), dtype=int)
        for k, elm in enumerate(hvdc):
            self.hvdc_F[k] = bus_dict[elm.bus_from]
            self.hvdc_T[k] = bus_dict[elm.bus_to]

    @property
    def converged(self):
        """
        Check if converged in all modes
        :return: True / False
        """
        val = True
        for conv in self.convergence_reports:
            val *= conv.converged()
        return val

    @property
    def error(self):
        """
        Check if converged in all modes
        :return: True / False
        """
        val = 0.0
        for conv in self.convergence_reports:
            val = max(val, conv.error())
        return val

    @property
    def elapsed(self):
        """
        Check if converged in all modes
        :return: True / False
        """
        val = 0.0
        for conv in self.convergence_reports:
            val = max(val, conv.elapsed())
        return val

    def copy(self):
        """
        Return a copy of this
        @return:
        """
        val = PowerFlowResults(n=self.n, m=self.m, n_tr=self.n_tr, n_hvdc=self.n_hvdc,
                               bus_names=self.bus_names,
                               branch_names=self.branch_names,
                               transformer_names=self.transformer_names,
                               hvdc_names=self.hvdc_names,
                               bus_types=self.bus_types)
        val.Sbus = self.Sbus.copy()
        val.voltage = self.voltage.copy()
        val.Sf = self.Sf.copy()
        val.If = self.If.copy()
        val.Vbranch = self.Vbranch.copy()
        val.loading = self.loading.copy()
        val.losses = self.losses.copy()

        return val

    def apply_from_island(self, results: "PowerFlowResults", b_idx, br_idx, tr_idx):
        """
        Apply results from another island circuit to the circuit results represented
        here.

        Arguments:

            **results**: PowerFlowResults

            **b_idx**: bus original indices

            **elm_idx**: branch original indices
        """
        self.Sbus[b_idx] = results.Sbus

        self.voltage[b_idx] = results.voltage

        self.Sf[br_idx] = results.Sf

        self.St[br_idx] = results.St

        self.If[br_idx] = results.If

        self.Vbranch[br_idx] = results.Vbranch

        self.loading[br_idx] = results.loading

        self.losses[br_idx] = results.losses

        self.convergence_reports += results.convergence_reports

    def get_report_dataframe(self, island_idx=0):
        """
        Get a DataFrame containing the convergence report.

        Arguments:

            **island_idx**: (optional) island index

        Returns:

            DataFrame
        """
        report = self.convergence_reports[island_idx]
        data = {'Method': report.methods_,
                'Converged?': report.converged_,
                'Error': report.error_,
                'Elapsed (s)': report.elapsed_,
                'Iterations': report.iterations_}

        df = pd.DataFrame(data)

        return df



    def mdl(self, result_type: ResultTypes) -> "ResultsTable":
        """

        :param result_type:
        :return:
        """

        columns = [result_type.value[0]]

        if result_type == ResultTypes.BusVoltageModule:
            labels = self.bus_names
            y = np.abs(self.voltage)
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BusVoltageAngle:
            labels = self.bus_names
            y = np.angle(self.voltage, deg=True)
            y_label = '(deg)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BusActivePower:
            labels = self.bus_names
            y = self.Sbus.real
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BusReactivePower:
            labels = self.bus_names
            y = self.Sbus.imag
            y_label = '(MVAr)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BusVoltagePolar:
            labels = self.bus_names
            y = self.voltage
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchPower:
            labels = self.branch_names
            y = self.Sf
            y_label = '(MVA)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActivePowerFrom:
            labels = self.branch_names
            y = self.Sf.real
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchReactivePowerFrom:
            labels = self.branch_names
            y = self.Sf.imag
            y_label = '(MVAr)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActivePowerTo:
            labels = self.branch_names
            y = self.St.real
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchReactivePowerTo:
            labels = self.branch_names
            y = self.St.imag
            y_label = '(MVAr)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchCurrent:
            labels = self.branch_names
            y = self.If
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActiveCurrentFrom:
            labels = self.branch_names
            y = self.If.real
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchReactiveCurrentFrom:
            labels = self.branch_names
            y = self.If.imag
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActiveCurrentTo:
            labels = self.branch_names
            y = self.It.real
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchReactiveCurrentTo:
            labels = self.branch_names
            y = self.It.imag
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchLoading:
            labels = self.branch_names
            y = np.abs(self.loading) * 100
            y_label = '(%)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchLosses:
            labels = self.branch_names
            y = self.losses
            y_label = '(MVA)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActiveLosses:
            labels = self.branch_names
            y = self.losses.real
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchReactiveLosses:
            labels = self.branch_names
            y = self.losses.imag
            y_label = '(MVAr)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchActiveLossesPercentage:
            labels = self.branch_names
            y = np.abs(self.losses.real) / np.abs(self.Sf.real + 1e-20) * 100.0
            y_label = '(%)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchVoltage:
            labels = self.branch_names
            y = np.abs(self.Vbranch)
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchAngles:
            labels = self.branch_names
            y = np.angle(self.Vbranch, deg=True)
            y_label = '(deg)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchTapModule:
            labels = self.branch_names
            y = self.tap_module
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchTapAngle:
            labels = self.branch_names
            y = self.theta
            y_label = '(rad)'
            title = result_type.value[0]

        elif result_type == ResultTypes.BranchBeq:
            labels = self.branch_names
            y = self.Beq
            y_label = '(p.u.)'
            title = result_type.value[0]

        elif result_type == ResultTypes.HvdcLosses:
            labels = self.hvdc_names
            y = self.hvdc_losses
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.HvdcPowerFrom:
            labels = self.hvdc_names
            y = self.hvdc_Pf
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.HvdcPowerTo:
            labels = self.hvdc_names
            y = self.hvdc_Pt
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.InterAreaExchange:
            labels = [a + '->' for a in self.area_names]
            columns = ['->' + a for a in self.area_names]
            y = self.get_inter_area_flows(area_names=self.area_names,
                                          F=self.F,
                                          T=self.T,
                                          Sf=self.Sf,
                                          hvdc_F=self.hvdc_F,
                                          hvdc_T=self.hvdc_T,
                                          hvdc_Pf=self.hvdc_Pf,
                                          bus_area_indices=self.bus_area_indices).real
            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.LossesPercentPerArea:
            labels = [a + '->' for a in self.area_names]
            columns = ['->' + a for a in self.area_names]
            Pf = self.get_branch_values_per_area(np.abs(self.Sf.real), self.area_names, self.bus_area_indices, self.F, self.T)
            Pf += self.get_hvdc_values_per_area(np.abs(self.hvdc_Pf), self.area_names, self.bus_area_indices, self.hvdc_F, self.hvdc_T)
            Pl = self.get_branch_values_per_area(np.abs(self.losses.real), self.area_names, self.bus_area_indices, self.F, self.T)
            Pl += self.get_hvdc_values_per_area(np.abs(self.hvdc_losses), self.area_names, self.bus_area_indices, self.hvdc_F, self.hvdc_T)

            y = Pl / (Pf + 1e-20) * 100.0
            y_label = '(%)'
            title = result_type.value[0]

        elif result_type == ResultTypes.LossesPerGenPerArea:
            labels = [a for a in self.area_names]
            columns = [result_type.value[0]]
            gen_bus = self.Sbus.copy().real
            gen_bus[gen_bus < 0] = 0
            Gf = self.get_bus_values_per_area(gen_bus, self.area_names, self.bus_area_indices)
            Pl = self.get_branch_values_per_area(np.abs(self.losses.real), self.area_names, self.bus_area_indices, self.F, self.T)
            Pl += self.get_hvdc_values_per_area(np.abs(self.hvdc_losses), self.area_names, self.bus_area_indices, self.hvdc_F, self.hvdc_T)

            y = np.zeros(len(self.area_names))
            for i in range(len(self.area_names)):
                y[i] = Pl[i, i] / (Gf[i] + 1e-20) * 100.0

            y_label = '(%)'
            title = result_type.value[0]

        elif result_type == ResultTypes.LossesPerArea:
            labels = [a + '->' for a in self.area_names]
            columns = ['->' + a for a in self.area_names]
            y = self.get_branch_values_per_area(np.abs(self.losses.real), self.area_names, self.bus_area_indices, self.F, self.T)
            y += self.get_hvdc_values_per_area(np.abs(self.hvdc_losses), self.area_names, self.bus_area_indices, self.hvdc_F, self.hvdc_T)

            y_label = '(MW)'
            title = result_type.value[0]

        elif result_type == ResultTypes.ActivePowerFlowPerArea:
            labels = [a + '->' for a in self.area_names]
            columns = ['->' + a for a in self.area_names]
            y = self.get_branch_values_per_area(np.abs(self.Sf.real), self.area_names, self.bus_area_indices, self.F, self.T)
            y += self.get_hvdc_values_per_area(np.abs(self.hvdc_Pf), self.area_names, self.bus_area_indices, self.hvdc_F, self.hvdc_T)

            y_label = '(MW)'
            title = result_type.value[0]

        else:
            raise Exception('Unsupported result type: ' + str(result_type))

        # assemble model
        mdl = ResultsTable(data=y, index=labels, columns=columns,
                           title=title, ylabel=y_label, units=y_label)
        return mdl

    def export_all(self):
        """
        Exports all the results to DataFrames.

        Returns:

            Bus results, Branch reuslts
        """

        # buses results
        vm = np.abs(self.voltage)
        va = np.angle(self.voltage)
        vr = self.voltage.real
        vi = self.voltage.imag
        bus_data = np.c_[vr, vi, vm, va]
        bus_cols = ['Real voltage (p.u.)',
                    'Imag Voltage (p.u.)',
                    'Voltage module (p.u.)',
                    'Voltage angle (rad)']
        df_bus = pd.DataFrame(data=bus_data, columns=bus_cols)

        # branch results
        sr = self.Sf.real
        si = self.Sf.imag
        sm = np.abs(self.Sf)
        ld = np.abs(self.loading)
        la = self.losses.real
        lr = self.losses.imag
        ls = np.abs(self.losses)
        tm = np.ans(self.tap_module)

        branch_data = np.c_[sr, si, sm, ld, la, lr, ls, tm]
        branch_cols = ['Real power (MW)',
                       'Imag power (MVAr)',
                       'Power module (MVA)',
                       'Loading(%)',
                       'Losses (MW)',
                       'Losses (MVAr)',
                       'Losses (MVA)',
                       'Tap module']
        df_branch = pd.DataFrame(data=branch_data, columns=branch_cols)

        return df_bus, df_branch

