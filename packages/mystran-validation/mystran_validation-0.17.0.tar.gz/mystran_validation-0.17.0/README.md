MYSTRAN validation
==================


![pypi](https://img.shields.io/pypi/v/mystran_validation.svg "https://pypi.python.org/pypi/mystran_validation")


Python framework for [MYSTRAN](http://https://github.com/dr-bill-c/MYSTRAN) validation.


* Free software: MIT license

[[_TOC_]]

Features
--------

* [declarative framework](#a-declarative-framework)
* [flexible](#a-flexible-framework)
* built on top of [pytest](https://pytest.org/), [femap-neutral-parser](https://pypi.org/project/femap-neutral-parser/) and [PyNastran](https://pypi.org/project/pyNastran/).
* tests-results are summarized within a [JUnitXML](https://junit.org/junit5/docs/current/user-guide) file, therefore compatible with Jenkins/Travis or other CI tools.
* HTML files are created out of the JUnit file (`--report`) 

Limitations
-----------

* for now, only [a few vectors](#vectors) are implemented 
* Mystran results are based on `.NEU` result file, therefore, somewhere limited with available results. Plan is to migrate to OP2 parsing once it will have been developped.


Vectors
-------

Currently implemented vectors:

- [x] Displacements (3 translations, 3 rotations)
- [x] Reactions (6-dof reactions)
- [x] CBAR internal forces
- [x] CBUSH internal forces

Next in the pipe:

- [ ] CQUAD4 internal forces
- [ ] CTRIA3 internal forces

A declarative Framework
-----------------------

`mystran_validation` is a python **declarative** framework dedicated to MYSTRAN test cases.

**declarative** means that end-user do not need to know python **at-all**. Test cases are declared as `ini` text files, pointing to relevant files, and describing the test itself.

Example::

        [DEFAULT]
        title = test 00
        bulk = bulk_model.nas
        reference = test_case_03.op2
        
        [Checking Displs]
        # we check all nodes displacements
        description = check all displacements
        vector = displacements

        [Reactions]
        # we check all nodes displacements
        description = this is a multi-lines
        	description
        vector = reactions

The above configuration file describes **two tests** performed on ``bulk_model.nas`` (named "Checking Displs"). This test will check **all displacements** and **all ractions** against ``test_case_03.op2`` file. 


A flexible framework
--------------------

Event though [many limitations] still remain, the framework features:

### tolerance management

The above example may be tweaked as follows::

     [...]
     
     [Displacements]
     # we check all nodes displacements
     description = check all displacements
     vector = displacements
     ## we can reduce / increase tolerance
     rtol = 1e-05 # default relative tolerance
     atol = 1e-08 # default absolute tolerance 

### checking data subset

Data subset can be checked by specifying `gids`, `SubcaseIDs`::

     [...]
     
     [Displacements]
     # we check all nodes displacements
     description = check all displacements
     vector = displacements
     ## we can restrict checked data:
     gids = 1, 2
     SubcaseIDs = 1,2

### Manual references

Beside reference results file, one can specify a value *by-hand* as follows::

        [Displacements II]
        description = Check one single value
        vector = displacements
        ## restrict check to MYSTRAN subset:
        gids = 1
        SubcaseIDs = 2
        axis = 6
        reference = 0.00513
        atol = 1e-06 


USAGE
=====

`mystran-validation` is a command-line tool. The main entry point is the `mystran-val` command. `mystran-val --help` for options and arguments.

The main command ``mystran-val run`` will trigger all the test-suites found in the tests repository. 

Configuration
-------------

`mystran-validation` finds its settings from a central configuration file located under:

* Linux: /home/<user>/.config/mystran-validation/config.ini
* Windows: C:\\Users\\<user>\\AppData\\Roaming\\numeric\\mystran-validation\\config.ini

By default, only the ``[DEFAULT]`` section is present. You can create any number of profile by adding a new section with relevant name::

    [dev]
    mystran-bin = path/to/dev/mystran/version

You can now pass ``--profile dev`` to ``maystran-val`` command.

Overriding test repository
--------------------------

The test repository is defaulted to `$HOME/mystran_test_cases` and can be overridden by passing ``--rootdir`` option::

    $ mystran-val --rootdir ~/another-repo run


Specifying MYSTRAN binary to use
--------------------------------

MYSTRAN Binary is found with the following scheme:

- from `--mystran-bin` (`-m` short option) passed option
- from "``mystran-bin``" value in configuration file

Starting from scratch
=====================

After installing `mystran-validation` (*eg* using [pipx](https://pypi.org/project/pipx/)), you will need to setup a tests repository. This can be done automatically by using (without additional options)::

	mystran-val init

This will create:

* a configuration file in `/.config/mystran-validation/config.ini`
* an example folder with two simple models, `.OP2` for reference and a `.ini` file ready to be ran.

You can crate as many profiles as you wish in the configuration file. Just add a new section like:

    [dev]
    mystran-bin = /path/to/mystran
    rootdir = ~/mystran-test-cases

Yo will then be able to run test-cases per profile:

    mystran-val -p toto run

Running your first run
----------------------

Once your repository is setup, trigger your first test-cases checking:

	mystran-val run

Or, if `toto` profile is defined in the configuration file:

    mystran-val -p toto run

If you need to override MYSTRAN binary:

	mystran-val -m "path/to/my/mystran" run

        



  


