# `rsbox`: Utility Toolbox

([Github](https://github.com/rosikand/rsbox) | [PyPI](https://pypi.org/project/rsbox) | [Documentation](https://rosikand.github.io/rsbox/))

A toolbox of utility functions [I](http://rosikand.github.io/) commonly use when programming in Python. Includes mostly machine learning utilities. 

The full API consists of importable functions from modules located in `src/rsbox/`. Functions are documented via docstrings under the function header. An HTML front-end documentation for the API is available [here](https://rosikand.github.io/rsbox/).

## Installation 

```
$ pip install rsbox
```

## Examples 

Here are some highlighted functions: 

```python
import rsbox
from rsbox import ml, misc

ml.print_model_size(pytorch_net)
current_time_in_string = misc.timestamp()
dataset = ml.image_dir_to_data(dirpath="./data", extension='png')
img_np_array = ml.get_img(url='https://stanford.edu/~rsikand/assets/images/seal.png')  
ml.plot(img_np_array)
```

<img width="200" alt="image" src="https://user-images.githubusercontent.com/57341225/190890819-6b4a5266-2f21-4703-a70e-e18358f5c247.png">





## Modules 

The modules are located in `src/rsbox/`

- `ml.py`: machine learning programming utilities. 
- `misc.py`: misc. utilities. 
