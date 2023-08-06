# Liteobj

Liteweight configuration format for defining and recursively instantiating python objects composed of nested object parameters

See [tutorial.ipynb](https://github.com/1lint/liteobj/blob/master/tutorial.ipynb) example use of `liteobj` (tutorial for previous version, currently out of date, will be fixed soon)

## Install

Install from pip
```
pip install liteobj
```

## Quickstart Example
As a basic example, run the Pytorch Lightning Basic GAN tutorial from https://pytorch-lightning.readthedocs.io/en/stable/notebooks/lightning_examples/basic-gan.html
```
git clone https://github.com/1lint/liteobj
cd liteobj
python -m pip install -r basic_gan/requirements.txt
python lite.py basic_gan/lab.yaml fit
```

To run lite.py in other directories, install the pip package. Then run configurations with the `lite` console script 
```
python -m pip install .
lite basic_gan/lab.yaml fit
```

CLI syntax is 
```
lite {config_path} {object_method} {method_args} {method_kwargs}
```
`config_path` is path to the yaml file to instantiate, and is the only required parameter. Returns the instantiated object instance
`object_method` is the name of the object method to invoke once the object is instantiated. If passed, returns the output of the object method
`method_args` and `method_kwargs` are passed directly into the object method. 








