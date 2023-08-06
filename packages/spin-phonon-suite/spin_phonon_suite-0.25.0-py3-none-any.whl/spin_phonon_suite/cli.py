#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError, \
                     RawDescriptionHelpFormatter, BooleanOptionalAction
import sys
import os
import re
import pickle
from operator import add
from functools import reduce
from itertools import product
import h5py
import numpy as np
import matplotlib.pyplot as plt

import gaussian_suite.gen_input as gsgi
import xyz_py as xyzp
from xyz_py import atomic
from molcas_suite.cli import ParseExtra
import gaussian_suite.cd_extractor as gscd
import hpc_suite as hpc
from hpc_suite.action import ParseKwargs, OrderedSelectionAction
from hpc_suite import make_parse_dict, SecondaryHelp
import angmom_suite
from angmom_suite import crystal
from angmom_suite.basis import Level
from angmom_suite.multi_electron import Ion
import molvis.core as mvis
from pymatgen.core.structure import Molecule, Structure
from pymatgen.transformations.site_transformations import TranslateSitesTransformation

from .coordinates import CoordinateInfo
from .derivative import print_tau_style, read_tau_style
from .lvc import LVC, generate_lvc_input, make_lvc_evaluator, ANG2BOHR, \
    LVCModelHamiltonian, LVCAdiabaticEnergies, LVCDiabaticHamiltonian
from .vibrations import Harmonic
from . import cells

plt.rcParams['font.family'] = "Arial"

HARTREE2INVCM = 219474.63 


# Action for secondary function help message
class FunctionHelp(SecondaryHelp):
    def __call__(self, parser, namespace, values, option_string=None):

        if namespace.function == 'cfp':
            angmom_suite.read_args(['cfp', '--help'])
        else:
            raise ValueError("Supply valid option to function argument.")


def str_int(x):
    try:
        return int(x)
    except ValueError:
        return str(x)


def coords_func(args):
    sp_data = CoordinateInfo.from_args(args)
    sp_data.to_file(args.distortion_info)

    return


def lvc_func(args):

    if args.add is not None:
        def join(a, b):
            return a.join(b, xyzp.load_xyz(args.reference_xyz)[1] * ANG2BOHR)
        lvc = reduce(join, (LVC.from_file(f_lvc) for f_lvc in args.add))

    elif args.efld is not None:
        charge_list = [np.loadtxt(f_chrg) for f_chrg in args.charge]
        xyz_list = [xyzp.load_xyz(f_xyz)[1] * ANG2BOHR for f_xyz in args.xyz]
        lvc = LVC.from_molcas_frozen_density(
            args.rassi, args.efld, charge_list, xyz_list)

    elif args.grad is not None:
        lvc = LVC.from_molcas(args.rassi, args.grad)

    else:
        raise ValueError("LVC gradient information supplied!")

    if args.active_atoms is not None:
        idc = [idx - 1 for idc in args.active_atoms for idx in idc]
        lvc = lvc.subset_atoms(active_atom_idc=idc)

    elif args.ref_coordinates is not None:
        _, coords = xyzp.load_xyz(args.ref_coordinates)
        lvc = lvc.subset_atoms(ref_coords=coords * ANG2BOHR)

    lvc.to_file(args.lvc_data, verbose=args.verbose)

    return


def eval_func(args, unknown_args):

    try:
        selected = args._selection
    except AttributeError:
        sys.exit("No quantity selected for evaluation!")

    # Resolve coordinates
    if args.vibration_info is not None:
        ho = Harmonic.from_file(args.vibration_info)
        coords = ho.mass_freq_weighted_coordinates * ANG2BOHR
    else:
        coords = None

    store_args = hpc.read_args(['store'] + unknown_args)

    eval_args = (store_args, make_lvc_evaluator, selected)
    eval_kwargs = {"order": args.order, "coords": coords,
                   "truncate": args.truncate, "align": args.align}

    if args.geom is None:
        hpc.store_func(*eval_args, geom=None, **eval_kwargs)
    else:
        for geom in map(lambda file: xyzp.load_xyz(file)[1], args.geom):
            hpc.store_func(*eval_args, geom=geom * ANG2BOHR, **eval_kwargs)


def vib_func(args):

    if args.gaussian_log:

        if args.mass:
            raise ValueError("The --mass argument is not available with freq "
                             "data read from Gaussian text output use *.fchk!")

        ho = Harmonic.from_gaussian_log(args.gaussian_log)

    elif args.gaussian_fchk:
        ho = Harmonic.from_gaussian_fchk(
            args.gaussian_fchk,
            ext_masses=args.mass,
            rot=args.rot,
            trans=args.trans
        )

    elif args.force_sets:

        ho = Harmonic.from_vasp_phonopy(
            args.poscar,
            args.force_sets,
            ext_masses=args.mass,
            trans=args.trans,
            distortion_expansion=args.distortion_expansion,
            distortion_cutoff=args.distortion_cutoff,
            central_index=args.central_index,
            force_expansion=args.force_expansion,
            q_mesh=args.q_mesh,
            gamma_center=args.gamma_center
        )

    elif args.phonopy_hdf5:

        if args.mass:
            raise ValueError("The --mass argument is not available with phonon"
                             " data read from phonopy hdf5 database, use "
                             "FORCE_SETS instead!")

        ho = Harmonic.from_phonopy_hdf5(
            args.poscar,
            args.phonopy_hdf5,
            trans=args.trans,
            distortion_expansion=args.distortion_expansion,
            distortion_cutoff=args.distortion_cutoff,
            central_index=args.central_index
        )

    if args.active_atoms is not None:
        idc = [idx - 1 for idc in args.active_atoms for idx in idc]
        ho = ho.subset_atoms(active_atom_idc=idc)

    elif args.ref_coordinates is not None:
        _, coords = xyzp.load_xyz(args.ref_coordinates)
        ho = ho.subset_atoms(ref_coords=coords)

    ho.to_file(args.vibration_info, store_vecs=args.store_vecs)

    if args.save_pyvibms is not None:
        ho.to_pyvibms(args.save_pyvibms)

    return


def prepare_func(args):

    if args.program == 'tau':
        # CFP args
        proj_kwargs = {
            'model_space': args.ground_level,
            'quax': args.quax,
            'terms': {"cf": [('J',)]},
            'k_max': args.k_max,
            'theta': True,
            'ion': args.ion
        }

        # EQ_CFPs.dat
        cfp_eq = LVCModelHamiltonian(LVC.from_file(args.lvc_data), 0,
                                     **proj_kwargs)[("cf", "J")]

        cfp_data = np.column_stack(
            (np.ones(27), list(cfp_eq.keys()), list(cfp_eq.values())))

        np.savetxt('EQ_CFPs.dat', cfp_data,
                   fmt=['%2d', '%2d', '% 2d', '%16.8f'])

        # mode_energies.dat
        ho = Harmonic.from_file(args.vibration_info)
        np.savetxt('mode_energies.dat', ho.freqs, fmt='%16.8f',
                   header="Frequency (cm-1)", comments='')

        cfp_dq = LVCModelHamiltonian(
            LVC.from_file(args.lvc_data), 1,
            coords=ho.mass_freq_weighted_coordinates * ANG2BOHR,
            **proj_kwargs
        )

        print_tau_style(filter(lambda pars: pars[0][1] == 'cf', iter(cfp_dq)),
                        ho.freqs, 'CFP_polynomials.dat')

    elif args.program == 'tau_direct':

        ho = Harmonic.from_file(args.vibration_info)
        np.savetxt('mode_energies.dat', ho.freqs, fmt='%16.8f',
                   header="Frequency (cm-1)", comments='')

        lvc = LVC.from_file(args.lvc_data)

        ener = LVCAdiabaticEnergies(lvc, 0, soc=True,
                                    truncate=args.truncate)[()]

        nstates = args.truncate or ener.size

        couplings = LVCDiabaticHamiltonian(lvc, 1, 
            coords=ho.mass_freq_weighted_coordinates * ANG2BOHR,
            soc=True, truncate=nstates)

        with h5py.File('tau.hdf5', 'w') as h, open('coupling_strength.dat', 'w') as f:

            h.create_dataset('energies', data=(ener - ener[0]) * HARTREE2INVCM)

            grp = h.create_group("couplings")

            for modes, lin in iter(couplings):

                cplg = lin * HARTREE2INVCM

                if args.trace_less:
                    cplg -= np.identity(nstates) * np.trace(cplg) / nstates

                grp.create_dataset('_'.join(map(str, modes)), data=cplg)
                strength = np.sum((cplg * cplg.conj()).real)
                f.write(f'{strength}\n')

            angm_grp = h.create_group('angmom')
            spin_grp = h.create_group('spin')

            for idx, comp in enumerate(["x", "y", "z"]):
                idc = np.ix_(range(nstates), range(nstates))
                angm_grp.create_dataset(comp, data=lvc.sos_angm[idx][idc])
                spin_grp.create_dataset(comp, data=lvc.sos_spin[idx][idc])

    return


def charges_func(args):
    """
    Wrapper function for cli call to charges
    """

    structure = Structure.from_file(args.poscar)
    equivalent_positions, elements, mappings, entities = \
        cells.get_unique_entities(structure)

    if args.gen:
        gen_charges_func(entities)
    elif args.parse:
        parse_charges_func(equivalent_positions, elements, mappings, entities)
    else:
        ValueError(f"{args.mode} mode not supported!")


def format_formula(formula):
    return formula.replace(" ", "")


def gen_charges_func(entities):
    """
    Wrapper function for cli call to charges gen
    """

    print("******************************")
    print("The unique entities are")
    for mol in entities:
        print(mol.formula)
        mol.to(f"{format_formula(mol.formula)}.xyz")
    print("******************************")

    # Create gaussian inputs for CHELPG calculation, one for each
    # member of the ASU

    # All electron aug-cc-pvtz
    ae_pvtz = [
        'H', 'Li', 'Be', 'Na', 'Mg', 'B', 'C', 'N', 'O', 'F', 'He', 'Ne', 'Al',
        'Si', 'P', 'S', 'Cl', 'Ar', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'
    ]
    ae_basis = {atom: "aug-cc-pvtz" for atom in ae_pvtz}

    unsupported = [
        "K", "Ca", "Rb", "Sr", "Cs", "Ba", "Ac", "Th", "Pa", "U", "Np",
        "Pu", "Am", "Cm"
    ]
    unsupported_basis = {atom: "????" for atom in unsupported}

    for lab in (site.specie.symbol for mol in entities for site in mol.sites):
        if lab in unsupported:
            print(f"\033[31m Warning, add basis for {lab} to .com file\033[0m \n")

    ae_basis = ae_basis | unsupported_basis

    # ECP
    pp_pvtz = [
        'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'
    ]
    small_pp_basis = {atom: "aug-cc-pvtz-pp" for atom in pp_pvtz}

    stuttgart = {metal: "stuttgart rsc 1997"
                 for metal in atomic.lanthanides + atomic.transition_metals}

    psuedo = small_pp_basis | stuttgart

    try:
        os.mkdir("gaussian")
    except OSError:
        pass

    for idx, mol in enumerate(entities, start=1):
        gsgi.gen_input(
            f"gaussian/{format_formula(mol.formula)}_{idx}.com",
            list(map(lambda site: site.specie.symbol, mol.sites)),
            list(map(lambda site: (site.x, site.y, site.z), mol.sites)),
            99,
            99,
            method="PBE",
            bs_spec=ae_basis,
            ecp_spec=psuedo,
            opt=False,
            freq=False,
            extra_title=f"{format_formula(mol.formula)} (molecule #{idx})",
            chelpg="charge"
        )
        print()

    print("\033[93mCharge and multiplicity set to 99 in all .com files")
    print("Please replace with actual values before submitting \033[0m \n")

    return


def parse_charges_func(equivalent_positions, elements, mappings, entities):
    """
    Wrapper function for cli call to charges parse
    """

    def read_charges(mol, idx):
        file = f"gaussian/{format_formula(mol.formula)}_{idx}.log"
        return np.array(gscd.get_chelpg_charges(file))

    def symmetrize(mapping, charges):
        for val in np.unique(mapping):
            for idc in np.flatnonzero(mapping == val):
                yield val, np.mean(charges[idc])

    def neutralize(charges):
        return np.array(charges) - np.mean(charges)

    mol_mappings = enumerate(zip(mappings, entities), start=1)
    atomic_charges = {idx: chrg for mol_idx, (mapping, mol) in mol_mappings
                      for idx, chrg in symmetrize(mapping, read_charges(mol, mol_idx))}

    unitcell_charges = neutralize([
        atomic_charges[pos] for pos in equivalent_positions])

    np.savetxt("charges.dat", unitcell_charges)

    # Make molcas basis file for environment charges
    cells.write_molcas_basis(
        elements, dict(enumerate(unitcell_charges, start=1)), "ENV")

    print("\033[93m")
    print("Molcas basis set file for environment written to:")
    print("     ENV (basis set specification)\033[0m")


def cluster_func(args):

    structure = Structure.from_file(args.poscar)
    central_index = args.central_index

    if args.from_central:
        molecular_graph = cells.generate_molecular_graph(structure)
        connected_graphs = cells.split_molecular_graph(molecular_graph, filter_unique=False)
        central_graph = next(filter(lambda nodes: central_index - 1 in nodes, connected_graphs))
        _, qm_region = cells.extract_molecule(structure, central_graph, central_index=central_index - 1)
    elif args.qm_region is not None:
        _, qm_region = Molecule.from_file(args.qm_region)
    else:
        raise NotImplementedError()

    central_site = structure.sites[central_index - 1]
    shift = np.array([central_site.x, central_site.y, central_site.z])

    if args.distortion_expansion is not None:
        cluster = cells.DistortionSupercell.from_poscar(
            args.poscar, args.distortion_expansion, central_index=central_index)
    elif args.distortion_cutoff is not None:
        cluster = cells.DistortionCluster.from_poscar(
            args.poscar, args.distortion_cutoff, central_index=central_index)

    def format_label(args):
        idx, specie = args
        return f"{specie.symbol}.ENV.{idx}"

    labels = list(map(format_label, enumerate(structure.species, start=1))) * cluster.n_cell

    def generate_mapping(ref_coords):

        for idx, site in enumerate(qm_region.sites):

            coord = np.array([site.x, site.y, site.z]) - shift
            idc = np.flatnonzero(np.isclose(ref_coords, coord).all(axis=1))

            if len(idc) == 0:
                continue
            elif len(idc) == 1:
                yield idc[0]
            else:
                raise ValueError(f"Multiple instances of atom {coord}!")

    for idx in generate_mapping(cluster.cart_coords):
        labels[idx] = labels[idx].split('.')[0]

    xyzp.save_xyz("cluster.xyz", labels, cluster.cart_coords)


def derivatives_func(args, unknown_args=None, **func_kwargs):

    if args.method == "findiff":
        dx = Finite.from_file(args.distortion_info)

    # parse extra function kwargs
    if not func_kwargs and unknown_args:
        if args.function == 'CFPs':
            func_kwargs = vars(angmom_suite.read_args(['cfp'] + unknown_args))
        elif not unknown_args:
            func_kwargs = {}
        else:
            raise ValueError("Unused extra arguments not known to the parser.")

    func = make_func(args, max_numerical_order=dx.order,
                     max_analytic_order=args.max_analytic_order, **func_kwargs)

    # prints derivatives and function values on the input grid
    if args.format == 'points':
        dx.write_points(
            args.function + "_points.dat", func, max_order=args.order)
        return

    ho = Harmonic.from_file(args.vibration_info)

    # remove normalisation and convert to units of zero point displacement
    conv = np.sqrt(ho.red_masses) * (ho.zpd if args.zpd_unit else 1.0)
    dQ = dx.transform(ho.displacements, func, args.order) * conv[:, np.newaxis]

    if args.format == 'tau':  # print central derivatives in tau style input

        if not args.order == 1:
            raise ValueError("Only first order derivatives with tau format.")

        if not args.function == 'CFPs':
            raise ValueError("Only function=CFPs possible with tau format.")

        print_tau_style(dQ, ho.freqs, 'CFP_polynomials.dat')

    else:  # print central derivatives to file
        pass

    return


def generate_lvc_input_func(args):

    # todo: make prettier by parsing numbers directly to list of ints using
    # parse_range and a custom action which flattens, check also other uses of
    # parse_range if flattened

    # todo: replace dict by global definition
    roots_dict = {'dy': [18]}

    if args.num_roots:
        num_roots = map(int, args.num_roots)
    elif args.ion:
        num_roots = roots_dict[args.ion.lower()]
    else:
        sys.exit("Invalid specification of the number of roots.")

    for iph_idx, num_root in enumerate(num_roots, start=1):

        if num_root == 0:
            continue

        generate_lvc_input(
            args.old_path,
            args.old_project,
            num_root,
            iph_idx,
            mclr_extra=args.mclr_extra,
            alaska_extra=args.alaska_extra,
            two_step=args.two_step,
            dry=args.dry
        )

    return


def parse_range(string):
    """
    adapted from https://stackoverflow.com/questions/6512280/accept-a-range-of-
    numbers-in-the-form-of-0-5-using-pythons-argparse
    """

    # match numbers in hyphen separated range
    # capture first and second string of digits, don't capture hyphon
    splt = re.match(r'(\d+)(?:-(\d+))?$', string)

    if not splt:
        raise ArgumentTypeError(
            "'{}' is not a range of number. Expected forms like '0-5' or '2'.".format( # noqa
                string
            )
        )

    # extract start and end of range, if single number is given -> end = start
    start = splt.group(1)
    end = splt.group(2) or start

    return list(range(int(start), int(end)+1))


def strength_func(args):
    """
    Wrapper for spin-phonon coupling strength CLI call
    """

    # Load CFP polynomials from file
    dQ, freqs = read_tau_style(args.cfp_file)

    # TODO delete
    args.n = 13
    args.J = 3.5
    args.L = 3
    args.S = 0.5

    if not args.nooef:
        # Get OEF values
        OEFs = crystal.calc_oef(args.n, args.J, args.L, args.S)
        print(np.shape(OEFs))

        # Add back in OEFs to polynomial values
        dQ *= OEFs

    # Calculate strength values of each mode
    S = np.array([crystal.calc_total_strength(mode) for mode in dQ])

    # Save strength to file
    np.savetxt("strengths.dat", S)
    print("Strengths saved to strengths.dat")

    # Read in symmetry labels if given
    if args.irreps:
        irreps = list(np.loadtxt(args.irreps, dtype=str))
    else:
        irreps = ['A']*len(freqs)

    unique_irreps, irrep_ints = np.unique(irreps, return_inverse=True)    

    if args.plot:

        _, ax = plt.subplots(num='Spin-phonon coupling strength')

        for unique_int in np.unique(irrep_ints):
            ax.stem(
                freqs[np.nonzero(irrep_ints == unique_int)[0]],
                S[np.nonzero(irrep_ints == unique_int)[0]],
                basefmt=' ',
                linefmt='C{:d}-'.format(unique_int),
                markerfmt='C{:d}o'.format(unique_int)
            )
        if args.irreps:
            ax.legend(unique_irreps, frameon=False)

        ax.set_ylabel(r'$S$ (cm$^{-1}$)', fontname="Arial")
        ax.set_xlabel('Mode energy (cm$^{-1}$)', fontname="Arial")

        ax.set_ylim([0., np.max(S)*1.05])

        plt.savefig("strengths.svg")
        plt.savefig("strengths.png")
        print("Strength plots saved to strengths.svg and strengths.png")
        plt.show()

    return


cluster = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        add_help=False
)

morph = cluster.add_mutually_exclusive_group(required=True)

morph.add_argument(
    '--distortion_expansion',
    nargs=3,
    metavar=('N_x', 'N_y', 'N_z'),
    type=int,
    help='Supercell expansion.'
)

morph.add_argument(
    '--distortion_cutoff',
    type=float,
    help='Cut-off distance for unit cell cluster.'
)

cluster.add_argument(
    '--central_index',
    type=int,
    help='Index of the central spin center.'
)


def read_args(arg_list=None):
    description = '''
    A package for performing Spin-Phonon coupling calculations.
    '''

    parser = ArgumentParser(
            description=description,
            formatter_class=RawDescriptionHelpFormatter
            )

    subparsers = parser.add_subparsers(dest='prog')

    coords = subparsers.add_parser('coords')
    coords.set_defaults(func=coords_func)

    coords.add_argument(
        '-D',
        '--distortion_info',
        type=str,
        help='HDF5 database containing information about the distortion.'
    )

    coords.add_argument(
        '--num_atoms',
        type=int,
        default=1,
        help='Number of atoms.'
    )

    coords.add_argument(
        '--mode_wise',
        nargs='*',
        default=None,
        type=parse_range,
        help='Mode indices to be included in distortions calculations ' +
             '- activates mode-wise distortions.'
        )

    coords.add_argument(
        '--atomic',
        nargs='*',
        default=None,
        type=parse_range,
        help='Atomic indices to be included in distortion calculations ' +
             '- activates atomic distortions.'
        )

    coords.add_argument(
        '--num_steps',
        type=int,
        default=0,
        help='Number of distortion steps.'
    )

    coords.add_argument(
        '--order',
        type=int,
        default=1,
        help='Order of distortion.'
    )

    coords.add_argument(
        '--constant_step',
        type=float,
        help='Step size factor for constant displacement.'
    )

    evaluate = subparsers.add_parser('eval')
    evaluate.set_defaults(func=eval_func)

    evaluate.add_argument(
        '-H',
        '--Help',
        action=FunctionHelp,
        help='show help message for additional arguments and exit'
    )

    evaluate.add_argument(
        '-L',
        '--lvc_data',
        type=str,
        help='HDF5 database containing the LVC parameters.'
    )

    coords = evaluate.add_mutually_exclusive_group()

    coords.add_argument(
        '-V',
        '--vibration_info',
        type=str,
        help=('HDF5 database containing information about the vibrations.'
              'Derivatives are evaluated in the basis of dimension-less'
              'mass-frequency weighted normal mode coordinates.')
    )

    evaluate.add_argument(
        '--geom',
        nargs='+',
        help='*.xyz coordinates at which properties will be evaluated.'
    )

    evaluate.add_argument(
        '--order',
        type=int,
        default=0,
        help='Order of derivative.'
    )

    evaluate.add_argument(
        '--truncate',
        type=int,
        metavar="max_state",
        help='Truncate matrix elements at max_state'
    )

    evaluate.add_argument(
        '--align',
        action=BooleanOptionalAction,
        default=True,
        help='Align LVC model reference to input geometry by minimising RMSD.'
    )

    evaluate.add_argument(
        '--adiabatic_energies',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['mch', 'soc'],
        help='Energies of the MCH or SOC eigenstates.'
    )

    evaluate.add_argument(
        '--diabatic_hamiltonian',
        nargs='+',
        action=OrderedSelectionAction,
        choices=['mch', 'soc'],
        help='Diabatic potential energy matrix between MCH or SOC states.'
    )

    evaluate.add_argument(
        '--proj',
        nargs='+',
        action=OrderedSelectionAction,
        help='Model Hamiltonian projection'
    )

    evaluate.add_argument(
        '--sus',
        nargs='+',
        action=OrderedSelectionAction,
        help='Magnetic susceptibility'
    )

    inp = subparsers.add_parser('generate_input')
    inp.set_defaults(func=generate_lvc_input_func)

    inp.add_argument(
        'old_project',
        type=str,
        help='Project name of preceding Molcas calculation.'
    )

    inp.add_argument(
        '--old_path',
        type=str,
        default='../',
        help='Path to WorkDir of preceding Molcas calculation.'
    )

    roots = inp.add_mutually_exclusive_group(required=True)

    roots.add_argument(
        '--num_roots',
        nargs='+',
        help='Number of states per JOBIPH.'
    )

    roots.add_argument(
        '--ion',
        type=str,
        help='Label of the metal center, e.g. Dy.'
    )

    inp.add_argument(
        '--jobiph',
        nargs='+',
        help='Indices of Molcas JOBIPH wavefunction files *_IPH.'
    )

    inp.add_argument(
        '--mclr_extra',
        nargs='+',
        default=((), {}),
        type=make_parse_dict(str, str, key_only=True),
        action=ParseExtra,
        help='Manually run mclr with custom options, e.g. thre=1e-8',
        metavar='name=value')

    inp.add_argument(
        '--alaska_extra',
        nargs='+',
        default=((), {}),
        type=make_parse_dict(str, str, key_only=True),
        action=ParseExtra,
        help='Run alaska with custom options, e.g. cuto=1e-8',
        metavar='name=value')

    inp.add_argument(
        '--two_step',
        action=BooleanOptionalAction,
        default=True,
        help='Utilize two-step procedure for MCLR runs'
    )

    inp.add_argument(
        '--dry',
        default=False,
        action='store_true',
        help='Dry-run which prints files to be created'
    )

    lvc = subparsers.add_parser('lvc')
    lvc.set_defaults(func=lvc_func)

    lvc.add_argument(
        '-L', '--lvc_data',
        type=str,
        help='HDF5 database output containing the LVC data.'
    )

    grad = lvc.add_mutually_exclusive_group()

    grad.add_argument(
        '--grad',
        type=str,
        nargs='+',
        help='Molcas output file(s) containing gradients and NACs.'
    )

    grad.add_argument(
        '--efld',
        type=str,
        nargs='+',
        help='Molcas output file(s) containing electric field values.'
    )

    grad.add_argument(
        '--add',
        type=str,
        nargs='+',
        help='LVC HDF5 data bases to be added.'
    )

    frozen = lvc.add_argument_group('Frozen density gradient arguments')

    frozen.add_argument(
        '--charge',
        type=str,
        nargs='+',
        help='Text file(s) containing point charge values.'
    )

    frozen.add_argument(
        '--xyz',
        type=str,
        nargs='+',
        help='xyz file(s) containing point charge coordinates.'
    )

    add = lvc.add_argument_group('LVC addition arguments')

    add.add_argument(
        '--reference_xyz',
        type=str,
        help='xyz file containing the reference coordinates.'
    )

    lvc.add_argument(
        '--rassi',
        type=str,
        help=('Molcas *.rassi.h5 output file containing AMFI integrals, '
              'SF_ANGMOM operators and the spin multiplicities.')
    )

    subset = lvc.add_mutually_exclusive_group()

    subset.add_argument(
        '--active_atoms',
        nargs='+',
        type=parse_range,
        help=(
            'Atomic indices active during spin-phonon coupling. Effectively '
            'effectively setting the coupling of all other atoms to zero. '
            'Useful to suppress coupling of specific atoms.'
        )
    )

    subset.add_argument(
        '--ref_coordinates',
        help='xyz coordinates containing the atomic positions of active atoms.'
    )

    lvc.add_argument(
        '--verbose',
        action='store_true',
        help='Plot gradient norm and invariance measures.'
    )

    build = subparsers.add_parser('cluster', parents=[cluster])
    build.set_defaults(func=cluster_func)

    build.add_argument(
        '--poscar',
        type=str,
        help='Unit cell POSCAR.'
    )

    qm = vib_calc_excl = build.add_mutually_exclusive_group(required=True)

    qm.add_argument(
        '--from_central',
        action='store_true',
        help=('QM region is built by completing the molecule around the '
              'central index.')
    )

    qm.add_argument(
        '--qm_region',
        type=str,
        help='Coordinates of the QM-region.'
    )

    vibrate = subparsers.add_parser('vib', parents=[cluster])
    vibrate.set_defaults(func=vib_func)

    vibrate.add_argument(
        '-V', '--vibration_info',
        type=str,
        help='HDF5 database containing information about the vibrations.'
    )

    vib_calc_excl = vibrate.add_mutually_exclusive_group(required=True)

    vib_calc_excl.add_argument(
        '--gaussian_log',
        type=str,
        help='Text output of a gaussian freq calculation.'
    )

    vib_calc_excl.add_argument(
        '--gaussian_fchk',
        type=str,
        help='Formatted checkpoint file of a gaussian freq calculation.'
    )

    vib_calc_excl.add_argument(
        '--force_sets',
        type=str,
        help='FORCE_SETS file from VASP-phonopy pre-process.'
    )

    vib_calc_excl.add_argument(
        '--phonopy_hdf5',
        type=str,
        help='Phonon database from phono3py calculation.'
    )

    vibrate.add_argument(
        '--poscar',
        type=str,
        help='Unit cell POSCAR from VASP-phonopy pre-process.'
    )

    vibrate.add_argument(
        '--force_expansion',
        nargs=3,
        metavar=('N_x', 'N_y', 'N_z'),
        default=(1, 1, 1),
        type=int,
        help='Supercell expansion used in phonon calculation'
    )

    qpoints = vibrate.add_mutually_exclusive_group()

    qpoints.add_argument(
        '--q_mesh',
        nargs=3,
        metavar=('N_x', 'N_y', 'N_z'),
        type=int,
        help='Mesh in q-space for phonon evaluation.'
    )

    vibrate.add_argument(
        '--gamma_center',
        action=BooleanOptionalAction,
        default=True,
        help='Center q-mesh around gamma point.'
    )

    vibrate.add_argument(
        '--mass',
        type=make_parse_dict(str_int, float),
        default={},
        nargs='+',
        action=ParseKwargs,
        help='Modify atomic masses for isotopic substitution.',
        metavar='atom_index=mass or element_symbol=mass'
    )

    vibrate.add_argument(
        '--trans',
        action=BooleanOptionalAction,
        default=True,
        help='Project out three rigid body translations.'
    )

    vibrate.add_argument(
        '--rot',
        action=BooleanOptionalAction,
        default=True,
        help='Project out three rigid body rotations.'
    )

    subset = vibrate.add_mutually_exclusive_group()

    subset.add_argument(
        '--active_atoms',
        nargs='+',
        type=parse_range,
        help=(
            'Atomic indices active during spin-phonon coupling. Effectively'
            ' subsets the displacement vectors. Useful if coupling is '
            'evaluated with a subset of the atoms present in the vibrational'
            ' calculation.'
        )
    )

    subset.add_argument(
        '--ref_coordinates',
        help='xyz coordinates containing the atomic positions of active atoms.'
    )

    vibrate.add_argument(
        '--save_pyvibms',
        type=str,
        help='optional pyvibms output for visualisation in PyMol.'
    )

    vibrate.add_argument(
        '--store_vecs',
        action=BooleanOptionalAction,
        default=True,
        help='Flag to disable expensive storage of normal mode displacements.'
    )

    prepare = subparsers.add_parser('prep')
    prepare.set_defaults(func=prepare_func)

    prepare.add_argument(
        'program',
        choices=['tau', 'tau_direct'],
        help='Program for which to prepare inputs.'
    )

    data = prepare.add_argument_group('database files')

    data.add_argument(
        '-L', '--lvc_data',
        help='HDF5 database containing the LVC parameters.')

    data.add_argument(
        '-V', '--vibration_info',
        help='HDF5 database containing information about the vibrations.')

    prepare.add_argument(
        '--ground_level',
        type=Level.parse,
        help='Symbol of the model space.'
    )

    prepare.add_argument(
        '--ion',
        type=Ion.parse,
        help='Central ion.'
    )

    prepare.add_argument(
        '--k_max',
        type=int,
        default=6,
        help='Maximum Stevens operator rank.'
    )

    prepare.add_argument(
        '--quax',
        action=angmom_suite.QuaxAction,
        help='Quantisation axes.'
    )

    prepare.add_argument(
        '--truncate',
        type=int,
        metavar="max_state",
        help='Truncate matrix elements at max_state'
    )

    prepare.add_argument(
        '--trace_less',
        action=BooleanOptionalAction,
        default=True,
        help='Substract out trace from bare coupling elements.'
    )

    charges = subparsers.add_parser(
        "charges",
        description="""
        Creates inputs for Gaussian CHELPG charge calculations of each
        entity in the unit cell of a VASP optimised structure and
        collects the resulting charges
        """)

    charges.set_defaults(func=charges_func)

    charges.add_argument(
        "poscar",
        type=str,
        help='Poscar containing optimised geometry'
    )

    mode = charges.add_mutually_exclusive_group(required=True)

    mode.add_argument(
        "--gen",
        action='store_true',
        help='Generate Gaussian ChelpG inputs.'
    )

    mode.add_argument(
        "--parse",
        action='store_true',
        help='Parse Gaussian ChelpG outputs.'
    )

    strength = subparsers.add_parser('strength')
    strength.set_defaults(func=strength_func)

    strength.add_argument(
        "cfp_file",
        type=str,
        help=(
            "File (hdf5 or CFP_polynomials) containing coupling crystal",
            "field parameters"
        )
    )

    strength.add_argument(
        "n",
        type=float,
        help=(
            "Number of unpaired electrons in 4f subshell"
        )
    )

    strength.add_argument(
        "J",
        type=float,
        help=(
            "Total angular momentum quantum number"
        )
    )

    strength.add_argument(
        "L",
        type=float,
        help=(
            "Orbital angular momentum quantum number"
        )
    )

    strength.add_argument(
        "S",
        type=float,
        help=(
            "Spin angular momentum quantum number"
        )
    )

    strength.add_argument(
        "--plot",
        action="store_true",
        help="Produce plot of strength as a function of mode energy"
    )

    strength.add_argument(
        '--irreps',
        type=str,
        metavar='<file_name>',
        help=(
            'Color code strength plot based on mode symmetries listed in file',
            'file must contain column of IRREPs, one per mode'
        )
    )

    strength.add_argument(
        "--nooef",
        action="store_true",
        help="Produce plot of strength as a function of mode energy"
    )

    # If arg_list==None, i.e. normal cli usage, parse_args() reads from
    # "sys.argv". The arg_list can be used to call the argparser from the
    # back end.

    # read sub-parser
    parser.set_defaults(func=lambda args: parser.print_help())
    _args, _ = parser.parse_known_args(arg_list)

    # select parsing option based on sub-parser
    if _args.prog in ['derivatives', 'eval']:
        args, hpc_args = parser.parse_known_args(arg_list)
        args.func(args, hpc_args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)


def main():
    read_args()
