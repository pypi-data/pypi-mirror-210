import numpy as np
from angmom_suite.basis import extract_blocks, dissect_array, \
    print_sf_term_content
from angmom_suite.crystal import ProjectModelHamiltonian, evaluate_term_space,\
    evaluate_term_operators, print_basis
from angmom_suite.utils import plot_op
from .extractor import make_extractor


def make_proj_evaluator(h_file, options):
    return ProjectModelHamiltonianMolcas(h_file, options)


class ProjectModelHamiltonianMolcas(ProjectModelHamiltonian):

    def __init__(self, h_file, options):

        angm = make_extractor(h_file, ("rassi", "SFS_angmom"))[()]
        ener = make_extractor(h_file, ("rassi", "SFS_energies"))[()]
        amfi = make_extractor(h_file, ("rassi", "SFS_AMFIint"))[()]

        spin_mult = make_extractor(h_file, ("rassi", "spin_mult"))[()]

        ops = {
            'sf_angm': list(extract_blocks(angm, spin_mult, spin_mult)),
            'sf_mch': list(map(np.diag, extract_blocks(ener, spin_mult))),
            'sf_amfi': list(map(list, dissect_array(amfi, spin_mult, spin_mult)))
        }

        sf_mult = dict(zip(*np.unique(spin_mult, return_counts=True)))

        self.comp_thresh = options.pop("comp_thresh")
        self.field = options.pop("field")

        super().__init__(ops, sf_mult, **options)

    def __iter__(self):

        if self.model_space is None:
            print_sf_term_content(self.ops['sf_angm'], self.sf_mult)

        elif not self.terms:
            term_space, trafo = \
                evaluate_term_space(self.sf_mult, self.model_space,
                                    coupling=self.coupling, complete=True)

            hamiltonian, spin, angm = \
                evaluate_term_operators(
                    self.ops['sf_angm'], self.ops['sf_mch'], self.ops['sf_amfi'],
                    self.sf_mult, term_space, quax=self.quax, complete=True)

            print_basis(trafo(hamiltonian), trafo(spin), trafo(angm),
                        [self.model_space], comp_thresh=self.comp_thresh,
                        field=self.field, plot=self.verbose,
                        S=trafo(spin), L=trafo(angm), J=trafo(spin + angm))

        else:
            yield from super().__iter__()
