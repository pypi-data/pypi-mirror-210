# IP SoC Generator

**IP SoC gen** is a framework to generate MP/SoCs with different configurations through a set of masters/slaves for fast
digital design development. To install through pip: 
```bash
pip install --upgrade ipsocgen
```

## Template projects 
In order to get started generating your own designs, check the [template
repository](https://github.com/aignacio/ipsocgen_template) which contains an example of SoC and MPSoC using
[NoX](https://github.com/aignacio/nox)
processor as the main CPU.

## To contribute/develop/extend the work
Please follow the steps below to build the virtual environment and install the dependencies.
```bash
python3 -m venv venv
source venv/bin/activate 
python3 setup.py install
```


