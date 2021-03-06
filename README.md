# Kmax

## Dependencies

### lockfile

https://github.com/openstack/pylockfile

    python setup.py install --user

### enum34

https://pypi.python.org/packages/source/e/enum34/enum34-1.0.tar.gz#md5=9d57f5454c70c11707998ea26c1b0a7c

    python setup.py install --user

### pycudd

http://bears.ece.ucsb.edu/ftp/pub/pycudd2.0/pycudd2.0.2.tar.gz

The package contains two directories, `cudd-2.4.2/` and `pycudd/`.
First enter `cudd-2.4.2/`.

Be sure to edit the cudd-2.4.2/Makefile to build a 64-bit version if
your machine is 64-bit, according to the directions in the README
file.  Install swig for the python to c interface.  In apt-based
distributions `apt-get install swig`.

Now compile cudd-2.4.2 and create shared libraries for pycudd:

    make
    make libso

`make libso` may fail on nanotrav, but as long as the `lib/` directory
contains six shared object libraries, libcudd.so, libdddmp.so, etc,
then pycudd should build.

Finally, go up to the parent directory, enter `pycudd/`, and build:

    make FLAGS="-I /opt/python/include/python2.7/ -fPIC"

## Building Kmax

`check_dep` gathers constraints and other information from Kconfig files

    # inside the kconfig/ directory
    make

The Kbuild portion of Kmax is written in python, and needs no compilation.  It depends on `pymake`, so install that with

    # inside the kbuild/ directory
    make

## Environment

Kmax expects several environment variables to be set:

    KMAX_ROOT=/path/to/kmax/
    PYCUDD_ROOT=/path/to/pycudd/
    KMAX_SCRATCH=/path/to/kmax_scratch
    KMAX_DATA=/path/to/kmax_data
    export KMAX_ROOT PYCUDD_ROOT KMAX_SCRATCH KMAX_DATA

- set `KMAX_ROOT` to the path to the Kmax source directory
- set `PYCUDD_ROOT` to the path to the pycudd directory that
  contains both pycudd itself and cudd-2.4.2
- set `KMAX_SCRATCH` to a new directory for storing linux instances
- set `KMAX_DATA` to a new directory to store kmax's output

With those variables configured, modify the `PATH`, `PYTHONPATH`, and
`LD_LIBRARY_PATH` variables to point to kmax and pycudd like so:

    export PATH=$PATH:${KMAX_ROOT}/kconfig:${KMAX_ROOT}/kbuild:$KMAX_ROOT/analysis
    export PYTHONPATH=$PYTHONPATH:${PYCUDD_ROOT}/pycudd:${KMAX_ROOT}/lib
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${PYCUDD_ROOT}/cudd-2.4.2/lib

## Example run

This will download and collect all compilation units and presence
conditions from v4.0 of the Linux kernel source.

    # from the top-level kmax source directory
    python analysis/collect_buildsystem.py 4.0 x86

## Getting constraints on compilation units

Constraints for each compliation unit are in `$KMAX_DATA/unit_pc_VERARCH.txt`, e.g., `unit_pc_4.0x86.txt`.  The file containts two types of lines:

1. "`subdir_pc DIRNAME boolean_formula`" describes constraints for directories.
2. "`unit_pc OBJFILE boolean_formula`" describes constraints for
   compilation units.

These constraints are local to subdirectories, i.e., they need to be
combined to find the complete constraints.  For instance, in , the
complete constraints for `drivers/net/ethernet/ethoc.o` can be found by the
conjunction of the following constraints:

    subdir_pc drivers/net 1
    subdir_pc drivers/net/ethernet CONFIG_ETHERNET=y && defined(CONFIG_ETHERNET)
    unit_pc drivers/net/ethernet/ethoc.o defined(CONFIG_ETHOC) && CONFIG_ETHOC=y

Combining them yields the complete constraint for `ethdoc.o`:

    1 && CONFIG_ETHERNET=y && defined(CONFIG_ETHERNET) && defined(CONFIG_ETHOC) && CONFIG_ETHOC=y

Top-level directories like `drivers/` are always unconstrained, and a
constraint of `1` also means unconstrained.  Since Makefiles do not
have boolean variables, `CONFIG_ETHERNET=y` and
`defined(CONFIG_ETHERNET)` are boolean representations of these
variables that reflect both ways Makefiles can test variables, via
`ifeq` and `ifdef`.
