## Version changelog 

### `0.0.13`

- Fixed bugs and added features in/to `ml.load_image`,  `ml.classification_dataset`. 

### `0.0.12`

- Added `ml.classification_dataset`, `ml.img_dir_to_data`
- Legacy versions of the new functions are kept in tact for backwards compatability. 

### `0.0.11`

- Added `ml.load_image` 


### `0.0.10`

- Added `ml.numpy_collate` 


### `0.0.9`

- Added `misc.load_dataset`


### `0.0.8`

- Added `ml.MeanMetric`


### `0.0.7`

- Fixed bug in `misc.timestamp`

### `0.0.6`
- Added `print_model_size`, `img_dataset_from_dir`, `get_img` functions. 

### `0.0.5`

- Improved documentation. 
- Added new and improved `plot` function in `ml.py` and removed redundant `plot_tensor` function. `plot_np_img` was kept for longevity purposes. 
- Added `misc.timestamp`, `misc.pickle` and `misc.unpickle`. 

### `0.0.4`

- Changed `ml_utils.py` to `ml.py` for ease-of-use. 

### `0.0.3`

- Added more documentation.  

### `0.0.2`

- Removed Jax functions to enable use of `rsbox` on m1 without needing to build Jax from source. 

### `0.0.1`

- Initial module upload. Contains `ml_utils.py`. 
