
SHAPerone is a patched fork of [SHAP](https://pypi.org/project/shap)

Current patches:

* patched [issue 2721](https://github.com/slundberg/shap/issues/2721), [pull 2697](https://github.com/slundberg/shap/pull/2697) with `beeswarmplot` that 
broke compatibility with `matplotlib>3.5.3`
* removed usage of np.int, np.bool and np.float [pull 1890](https://github.com/slundberg/shap/pull/1890). 
The use of np.int, np.bool and np.float has been depreciated since numpy 1.20.0 and removed in `numpy>=1.24.0`.

## Install

SHAPerone can be installed from [PyPI](https://pypi.org/project/shaperone):

<pre>
pip install shaperone
</pre>
