"""
$SCHRODINGER/run build_peptide.py input_file output_file [options]

Builds one or more peptides from single-letter amino acid codes.

Input is a file of one or more lines with amino acids
represented by standard one-letter codes. Each line in the input file will
create a structure in the output file. However, if FASTA files are specified,
peptides will be built for each FASTA entry. If PDB is the specified output,
an output file will be written for each peptide. Blank lines are ignored.

Copyright Schrodinger, LLC. All rights reserved.
"""

import argparse
import sys

from schrodinger import structure
from schrodinger.protein import buildpeptide
from schrodinger.protein import pdbname
from schrodinger.structutils import build
from schrodinger.utils import fileutils


def process_command_line():
    """
    Process the commandline arguments.
    :return: Processed parser
    """
    SUPPORTED_SECONDARY = [
        'AlphaHelix', 'PiHelix', 'ThreeTenHelix', 'CollagenHelix',
        'ParallelPleatedSheet', 'AntiparallelPleatedSheet', 'Extended',
        'LeftHandedAlphaHelix'
    ]

    parser = argparse.ArgumentParser(usage=__doc__)

    parser.add_argument('input_file',
                        help='File of one or more lines with '
                        'single-letter codes of amino acids')
    parser.add_argument('output_file',
                        help='Structure file in maestro or pdb format')
    parser.add_argument("-c",
                        "-cap",
                        action="store_true",
                        dest="cap",
                        default=False,
                        help="Add capping groups to peptides.")

    parser.add_argument(
        "-z",
        "-zwitterion",
        action="store_true",
        dest="zwitterion",
        default=False,
        help=("Create zwitterionic form of peptides. This option is "
              "supported only when not adding caps"))

    parser.add_argument("-f",
                        "-fasta",
                        action="store_true",
                        dest="fasta",
                        default=False,
                        help="Input file is in FASTA format.")

    parser.add_argument(
        '-s',
        '-secondary_structure',
        dest='secondary',
        choices=SUPPORTED_SECONDARY,
        default='AlphaHelix',
        metavar='',
        help=
        f'secondary structure of the peptide. Allowed: {", ".join(SUPPORTED_SECONDARY)}, '
        'default: AlphaHelix')

    return parser


def canonicalize(st):
    """
    Repair termini hydrogens to match with parent atom pdbname type

    :param st: The Structure without end caps, atomtypes to be fixed
    :type st: schrodinger.structure.Structure

    :return: The Structure without end caps, atomtypes fixed
    :rtype: schrodinger.structure.Structure
    """

    pdbname.assign_pdb_names(st)
    n1_nitrogen = pdbname.find_n1_atom(st.atom)
    if n1_nitrogen:
        n1_nitrogen.pdbname = ' N1 '
    build.delete_hydrogens(st)
    build.add_hydrogens(st)
    build.reorder_protein_atoms_by_sequence(st)
    return st


def read_sequence(filename, fasta=False):
    """
    Read the sequence file and return list with tuples - (tile, sequence)

    :param filename: Input sequence file name.
    :type: string

    :param fasta: Define if the file is fasta format
    :type: Boolean

    :return: List of tuples - (title, sequence)

    """
    seq_list = []

    with open(filename, 'rt') as inputFile:
        if fasta:
            sequence = ''
            title = 'blanktitle'

            for line in inputFile:
                line = line.strip()
                if line.startswith(">"):
                    if sequence:
                        seq_list.append((title, sequence))
                        sequence = ""
                    title = line.lstrip(">")
                else:
                    if title == "blanktitle":
                        print(
                            "Input file does not appear to be in FASTA format.")
                        return None
                    else:
                        sequence += line.upper()
            if sequence:
                seq_list.append((title, sequence))

        else:
            for line in inputFile:
                if ">" in line:
                    print(
                        "Input file may be a FASTA file. If so, please use the "
                        "-f flag.")
                    return None
                else:
                    line = line.strip().upper()
                    if len(line):
                        seq_list.append((line, line))
        return seq_list


def build_structure(inp_seq, cap=False, zwitterion=False, secondary=None):
    """
    Build the 3D structure of peptide from the given sequence.
    Add cap or canonicalize the structure based on the option parsed.
    Return structure.Structure class object

    :param inp_seq: A tuple - (title, sequence)

    :param cap: Add terminal cap to peptide.
    :type: bool

    :param zwitterion: Generate zwitterionic form of peptide
    :type: bool

    :param secondary: Secondary structure for the peptide
    :type: str

    return: structure.Structure class object.
    """

    bad_AA = False

    title, sequence = inp_seq

    print("Handling sequence %s" % sequence)

    for seq in sequence:
        # Check if is not a standard amino acid code
        if seq not in structure.RESIDUE_MAP_1_TO_3_LETTER:
            bad_AA = True

    if not bad_AA:
        # Building the peptide
        st = buildpeptide.build_peptide(sequence,
                                        secondary_structure=secondary,
                                        cap=cap)

        # The peptide hydrogens need canonicalizing if uncapped
        if not cap:
            # Creating zwitterion
            if zwitterion:
                # Find the termini from which the caps have been removed
                atoms = [st.atom[a] for a in st.getAtomIndices()]
                term_nit = pdbname.find_n1_atom(atoms)
                term_ox = pdbname.find_oxt_atom(atoms)
                term_nit.formal_charge = 1
                term_ox.formal_charge = -1

            # Canonicalizing peptide hydrogens to map with parent atom
            # pdbnames
            st = canonicalize(st)

        st.title = title
        return st
    else:
        print("Specified sequence contains a non-standard amino acid. "
              "Skipping this sequence")


if __name__ == "__main__":

    # Process the command line.
    args = process_command_line().parse_args()
    inputFile = args.input_file
    outFile = args.output_file
    zwitterion = args.zwitterion
    cap = args.cap
    secondary = buildpeptide.SECONDARY_STRUCTURE[args.secondary]

    # Read Sequence from files
    try:
        sequence_list = read_sequence(inputFile, args.fasta)
    except IOError:
        print('Could not find input file %s' % inputFile)
        sys.exit(1)

    # Build structure from the sequence and write to file
    is_pdb = fileutils.get_structure_file_format(outFile) == 'pdb'

    if sequence_list:
        if is_pdb:
            for i, title_seq_pair in enumerate(sequence_list, start=1):
                basename = fileutils.get_basename(outFile)
                name_format = basename + '_{}.pdb'

                st = build_structure(title_seq_pair,
                                     cap=cap,
                                     zwitterion=zwitterion,
                                     secondary=secondary)
                if st:
                    st.write(name_format.format(i))
        else:
            try:
                with structure.StructureWriter(outFile) as writer:
                    for title_seq_pair in sequence_list:
                        st = build_structure(title_seq_pair,
                                             cap=cap,
                                             zwitterion=zwitterion,
                                             secondary=secondary)
                        if st:
                            writer.append(st)
            except ValueError:
                print('Unrecognized file format for output file - %s' % outFile)
                sys.exit(1)

    else:
        print("Invalid sequence in the file %s" % outFile)
        sys.exit(1)
