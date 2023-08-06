# stqe

Kernel-QE Storage test suite

### Dependencies
* Python >= 3.6
* pip >= 20.3

### Installation
Using virtualenv:  
`python3 -m pip install virtualenv`
`python3 -m venv stqe-venv && source stqe-venv/bin/activate`  
`python3 -m pip install -U pip wheel`  
`python3 -m pip install stqe`

(optional) edit /etc/san_top.conf example

#### How to Uninstall
`python3 -m pip uninstall stqe`

#### Basic cli usage
`stqe-test --help`
