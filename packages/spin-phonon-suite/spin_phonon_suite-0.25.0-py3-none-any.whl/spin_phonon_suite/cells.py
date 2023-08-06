from itertools import product
from functools import reduce
from math import ceil

from pymatgen.io.vasp import Poscar
from pymatgen.core.structure import Molecule
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.local_env import JmolNN, CrystalNN, IsayevNN
import networkx as nx
import networkx.algorithms.isomorphism as iso

from phonopy.interface.vasp import read_vasp
import numpy as np
import numpy.linalg as la
import molvis.core as mvis
import matplotlib.cm as cm


def generate_molecular_graph(structure):
    strategy = IsayevNN(cutoff=3.0, allow_pathological=True)
    graph = StructureGraph.with_local_env_strategy(structure, strategy, weights=True)

    # build directed multi-graph
    twoway = nx.MultiDiGraph(graph.graph)
    # nodes are labelled by species
    nx.set_node_attributes(twoway, {node: {'specie': str(structure[node].specie)} for node in twoway})

    def flip_edge(u, v, data):
        return v, u, {key: tuple(-i for i in val) if key == 'to_jimage'
                      else val for key, val in data.items()}

    # edges are labelled by periodic image crossing
    twoway.add_edges_from([flip_edge(*edge) for edge in twoway.edges(data=True)])

    return twoway


def split_molecular_graph(graph, filter_unique=False):

    connected = nx.connected_components(nx.Graph(graph))

    subgraphs = map(graph.subgraph, connected)

    def filter_unique_graphs(graphs):

        edge_match = iso.numerical_edge_match("weight", 1.0)
        node_match = iso.categorical_node_match("specie", None)

        unique_graphs = set()

        for graph in graphs:

            def graph_match(g):
                return nx.is_isomorphic(
                    graph, g, node_match=node_match, edge_match=edge_match)

            already_present = map(graph_match, unique_graphs)

            if not any(already_present):
                unique_graphs.add(graph)
                yield graph

    if filter_unique:
        return list(filter_unique_graphs(subgraphs))
    else:
        return list(subgraphs)


def extract_molecule(structure, graph, central_index=None):

    # walk graph and consider to_jimage
    def generate_shifts():

        start = next(iter(graph.nodes())) if central_index is None else central_index

        def walk(shifts, edge):
            a, b = edge
            return shifts | {b: shifts[a] + graph[a][b][0]['to_jimage']}

        edges = nx.bfs_edges(graph, source=start)
        shifts = reduce(walk, edges, {start: np.zeros(3)})
        return dict(sorted(shifts.items()))

    shifts = generate_shifts()

    species = [structure.species[idx] for idx in shifts]
    coords = [structure.lattice.get_cartesian_coords(
        structure.frac_coords[idx] + shift) for idx, shift in shifts.items()]
    molecule = Molecule(species, coords)

    return list(shifts.keys()), molecule


def get_unique_entities(structure):

    molecular_graph = generate_molecular_graph(structure)
    connected_graphs = split_molecular_graph(molecular_graph, filter_unique=True)
    indices, molecules = zip(*map(lambda x: extract_molecule(structure, x), connected_graphs))

    sym_structure = SpacegroupAnalyzer(structure).get_symmetrized_structure()
    structure_dict = sym_structure.as_dict()
    equivalent_positions = structure_dict['equivalent_positions']

    elements = [site.specie.symbol for site in structure]

    mappings = [[equivalent_positions[idx] for idx in shift_dict]
                for shift_dict in indices]

    return equivalent_positions, elements, mappings, molecules


def build_cluster(poscar, central_index=None, distortion_expansion=None,
                  distortion_cutoff=None):

    if distortion_expansion is not None:
        cluster = DistortionSupercell.from_poscar(
            poscar, distortion_expansion, central_index=central_index)
    elif distortion_cutoff is not None:
        cluster = DistortionCluster.from_poscar(
            poscar, distortion_cutoff, central_index=central_index)

    return cluster


class DistortionExpansion:
    """
    Contains information on supercell created from a given cell with
    specified expansion

    Parameters
    ----------
    lat_vecs : list
        Lattice vectors of unit cell as rows
    frac_coords : list
        Coordinates of each atom in cell as fraction of cell parameters
        (spin centre at the origin)
    atom_numbers : list
        Atomic number of each atom in cell

    Attributes
    ----------
    expansion : list[int]
        Expansion used to generate supercell from cell e.g. [3, 3, 3]
    uc_sc_map : list
        Mapping of supercell atoms onto unit cell atoms
    """
    def __init__(self, lat_vecs, coords, atom_numbers, *args, **kwargs):

        self.lat_vecs = lat_vecs
        self.coords = self.recenter_unitcell(coords, *args)
        self.atom_numbers = atom_numbers

        self.cart_coords = self.generate_cluster(*args)
        self.frac_coords = self.cart_coords @ la.inv(self.lat_vecs)
        self.n_atoms = len(atom_numbers)
        self.n_cell = self.frac_coords.shape[0] // self.coords.shape[0]

    @classmethod
    def from_poscar(cls, poscar_name, *args, central_index=None):
        atoms = read_vasp(poscar_name)

        if central_index is None:
            coords = atoms.scaled_positions
        else:
            shift = atoms.scaled_positions[central_index - 1]
            coords = (atoms.scaled_positions - shift) % 1.

        return cls(atoms.cell, coords, atoms.numbers, *args)

    def generate_cluster(self, *args):

        def shift_coords(idc):
            return (self.coords + np.array(idc)) @ self.lat_vecs

        coords = np.array([coord for idc in self.generate_cell_idc(*args)
                           for coord in shift_coords(idc)])

        return self.recenter_cluster(coords, *args)


class DistortionSupercell(DistortionExpansion):

    def generate_cell_idc(self, expansion):

        def expansion_range(num):

            start = stop = num // 2

            if num % 2 == 0:  # even
                return range(-start, stop)
            elif num % 2 == 1:  # odd
                return range(-start, stop + 1)

        for nvec in product(*map(expansion_range, expansion)):
            yield nvec

    def recenter_cluster(self, cart, expansion):

        def shift(num, vec):
            if num % 2 == 0:  # even
                return 0.0
            elif num % 2 == 1:  # odd
                return vec / 2

        return cart - np.sum(list(map(shift, expansion, self.lat_vecs)), axis=0)

    def recenter_unitcell(self, frac, expansion):

        def shift(num):
            if num % 2 == 0:  # even
                return 0.0
            elif num % 2 == 1:  # odd
                return 1 / 2

        return (frac + np.array(list(map(shift, expansion)))) % 1.0


class DistortionCluster(DistortionExpansion):

    def generate_cell_idc(self, cutoff):

        def expansion_range(vec):
            num = ceil(cutoff / np.linalg.norm(vec))
            return range(-num, num + 1)

        for nvec in product(*map(expansion_range, self.lat_vecs)):

            r = np.sum([ni * ci for ni, ci in zip(nvec, self.lat_vecs)], axis=0)

            if np.linalg.norm(r) <= cutoff:
                yield nvec

    def recenter_cluster(self, cart, *args):
        return cart - np.sum(self.lat_vecs, axis=0) / 2

    def recenter_unitcell(self, frac, *args):
        return (frac + 1 / 2) % 1.0


def write_molcas_basis(labels, charge_dict, name):
    """
    Writes dummy molcas basis file for environment charges to a textfile named
    according to the basis name.

    Parameters
    ----------
    labels : list[str]
        Atomic labels of environment with no indexing
    charge_dict : dict
        CHELPG charge of each environment atom
    name : str
        Root name of basis
    """

    with open(name, 'w') as f:

        f.write("* This file was generated by spin_phonon_suite\n")
        for elem, (lab, chrg) in zip(labels, charge_dict.items()):
            f.write(f"/{elem}.{name}.{lab}.0s.0s.\n")
            f.write("Dummy basis set for atomic charges of environment\n")
            f.write("no ref\n")
            f.write(f"{chrg:.9f} 0\n")
            f.write("0 0\n")

    return


def vis_charges_viewer(coords, labels, norm_charges, extra_coords=[],
                       extra_labels=[], extra_color='', viewer_style_args={},
                       viewer_div_args={}, main_kwargs={}, extra_kwargs={}):

    ms1 = mvis.Model(labels, coords, **main_kwargs)

    colours = cm.get_cmap('coolwarm', 250)

    ms1.atom_colours = [
        '#{0:02x}{1:02x}{2:02x}'.format(*col[:-1])
        for col in colours(norm_charges, bytes=True)
    ]

    ms2 = mvis.Model(extra_labels, extra_coords, **extra_kwargs)

    if extra_color:
        ms2.atom_colours = extra_color

    viewer = mvis.Viewer(
        objects=[ms1, ms2],
        extra_div_args=viewer_div_args,
        extra_style_args=viewer_style_args
    )

    return viewer
