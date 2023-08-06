import h5py
import numpy as np
from .vibrations import Harmonic

class CoordinateInfo:

    def __init__(self, method, natoms, ndisto, geom_list, distortion_idc,
                 distortion_mtx=None, order=1, nsteps=0, steps=None):

        self.method = method
        self.natoms = natoms
        self.ndisto = ndisto
        self.distortion_idc = distortion_idc
        self.order = order
        self.nsteps = nsteps
        self.steps = steps

        self._distortion_mtx = distortion_mtx

    @property
    def distortion_mtx(self):
        if self.method == 'atomic':
            return np.identity(3 * self.natoms).reshape((-1, self.natoms, 3))
        else:
            return self._distortion_mtx

    @classmethod
    def from_file(cls, h_file):

        with h5py.File(h_file, 'r') as h:
            method = h.attrs['method']
            natoms = h.attrs['num_atoms']
            ndisto = h.attrs['num_disto']
            distortion_idc = h['distortion_idc'][...]
            order = h.attrs['order']
            nsteps = h.attrs['num_steps']

            if nsteps > 0:
                steps = h['step_size'][...]
            else:
                steps = None

            try:
                distortion_mtx = h['distortion_mtx'][...]
            except KeyError:
                distortion_mtx = None

        return cls(method, natoms, ndisto, distortion_idc,
                   distortion_mtx=distortion_mtx, order=order,
                   nsteps=nsteps, steps=steps)

    @classmethod
    def from_args(cls, args):
        # parse distortion method
        method, ndisto, distortion_idc = resolve_distortion_method(args)

        if args.num_steps > 0:
            steps = resolve_step_sizes(args, args.num_atoms, distortion_idc)
        else:
            steps = None

        if method == 'mode_wise':
            distortion_mtx = \
                Harmonic.from_file(args.vibration_info).displacements
        else:
            distortion_mtx = None

        return cls(method, args.num_atoms, ndisto, distortion_idc,
                   distortion_mtx=distortion_mtx, order=args.order,
                   nsteps=args.num_steps, steps=steps)

    def to_file(self, h_file=None):

        with h5py.File(h_file, 'w') as h:
            h['/'].attrs.create('method', self.method)
            h['/'].attrs.create('num_atoms', self.natoms)
            h['/'].attrs.create('num_disto', self.ndisto)
            h.create_dataset('distortion_idc', data=self.distortion_idc)
            h['/'].attrs.create('order', self.order)
            h['/'].attrs.create('num_steps', self.nsteps)

            if self.steps is not None:
                h.create_dataset('step_size', data=self.steps)

            if self._distortion_mtx is not None:
                h.create_dataset('distortion_mtx', data=self._distortion_mtx)


def resolve_distortion_method(args):
    """Helper for the cli interface resolving the distortion method relevant
    arguments.
    """

    if args.mode_wise is not None:
        method = "mode_wise"

        distortion_idc = {int(m) - 1 for grp in args.mode_wise for m in grp}
        ndisto = len(distortion_idc)

    elif args.atomic is not None:
        method = "atomic"

        distortion_idc = {3 * (int(a) - 1) + c
                          for grp in args.atomic
                          for a in grp
                          for c in range(3)}
        ndisto = len(distortion_idc)

    else:
        raise ValueError("No distortion method specified.")

    return method, ndisto, list(distortion_idc)


def resolve_step_sizes(args, natoms, distortion_idc):

    step_list = [0.0 for _ in range(3 * natoms)]

    if args.constant_step:
        for idx in distortion_idc:
            step_list[idx] = args.constant_step

    else:
        print("Warning: Invalid step size specification. "
              "Only analytic derivatives.")

    return step_list
