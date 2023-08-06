"""
File: ml.py 
-------------- 
Contains useful functions that I may import while programming 
machine learning projects.  
""" 

from matplotlib import pyplot as plt
from PIL import Image
import requests
import torch 
import numpy as np 
from glob import glob
from tqdm.auto import tqdm
import random
import torchvision.transforms as T


def plot_png(file_path, color):
	"""
	Plots a png file (or jpeg really) using matplotlib. Color is a bool value. 
	If true, image will be displayed in color. Else, it will be displayed in 
	greyscale.
	"""
	image = Image.open(file_path)
	if color == True:
		plt.imshow(image, interpolation='nearest')
		plt.show()
	else:
		plt.imshow(image, interpolation='nearest', cmap='Greys_r')
		plt.show()


def plot_np_img(image_array, color):
	"""
    (Here for longevity purposes... use plot instead)
	Plots a numpy array using matplotlib. Color is a bool value. If true, 
	image will be displayed in color. Else, it will be displayed in 
	greyscale.

    input: image_array must be of shape (1, H, W) or (H, W) for greyscale
    and (3, H, W) for color. 
	"""
	if color == True:
		plt.imshow(image_array, interpolation='nearest')
		plt.show()
	else:
		plt.imshow(image_array, interpolation='nearest', cmap='Greys_r')
		plt.show()


def plot(image_array, color=True):
    """
    Plots a numpy array using matplotlib. Color is a bool value which
    is true by default. If passed in as False, image will be displayed in 
    greyscale. 

    input: image_array must be of shape (1, H, W) or (H, W, 1) or (H, W) for greyscale
    and (3, H, W) or (H, W, 3) for color. 
    """

    # move to numpy is not already in numpy array format 
    image_array = np.array(image_array)
    image_array = np.squeeze(image_array)

    if color == True:
        if image_array.shape[0] == 3:
            image_array = np.moveaxis(image_array, 0, -1)
        plt.imshow(image_array, interpolation='nearest')
        plt.show()
    else:
        plt.imshow(image_array, interpolation='nearest', cmap='Greys_r')
        plt.show()


def image_dir_to_data(dirpath, extension):
    """
    Takes in a directory containing images
    and returns a list of numpy arrays representing
    those images. 
    Args:
        - dirpath: path to directory 
        - extension: image extension type (e.g. png) (string)
    """
    data_subset = []
    sub_set = glob(dirpath + '/*.' + extension)
    for elem in sub_set:
        image = Image.open(elem)
        image_array = np.array(image)
        data_subset.append(image_array)
    return data_subset  


def image_dir_to_data_norm(dirpath, extension):
    """
    (Same as image_dir_to_data but with max value 
    (255) normalization). 
    Takes in a directory containing images
    and returns a list of numpy arrays representing
    those images. 
    Args:
        - dirpath: path to directory 
        - extension: image extension type (e.g. png) (string)
    """
    data_subset = []
    sub_set = glob(dirpath + '/*.' + extension)
    for elem in sub_set:
        image = Image.open(elem)
        image_array = np.array(image)
        image_array = image_array.astype(float)
        image_array = image_array/255.0
        data_subset.append(image_array)
    return data_subset    


def gen_label_pair(data_samples, label):
	"""
	Takes in a list of data samples (i.e. images, x)
	and a corresponding label and returns a list of tuples
	where each tuple is an (x, y) pair. 
	"""
	d_set = []
	for elem in data_samples:
	    sample_pair = (elem, label)
	    d_set.append(sample_pair)
	return d_set 


def gen_distro(master_list):
    """
    Takes in a list of lists who each contain
    (x, y) tuple samples for that class and returns 
    a randomly concatenated version. 
    """
    generated_distro = []
    for class_list in master_list:
        generated_distro = generated_distro + class_list
    random.shuffle(generated_distro)
    return generated_distro


def get_img(url='https://stanford.edu/~rsikand/assets/images/seal.png', resize=True, size=(128, 128)):
    """
    Returns a sample numpy image to play with. 
    Arguments:
    -----------
    - url: Can pass in custom url if you want a different image. 
    Defaults to a baby seal!  
    - resize: by default, all images are resized to 128x128. If you'd
    like to keep the default size, specify False. 
    - size: size to resize to. Default is 128x128. 
    """

    image = np.array(Image.open(requests.get(url, stream=True).raw))


    if resize:
        if len(image.shape) == 3:
            image = np.array(T.Resize(size=size)(torch.movedim(torch.tensor(image), -1, 0)))
        else:
            image = np.array(T.Resize(size=size)(torch.tensor(image)))
    else:
        if len(image.shape) == 3:
            if image.shape[0] != 3 and image.shape[2] == 3:
                image = np.moveaxis(image, -1, 0)
            elif image.shape[0] != 1 and image.shape[2] == 1:
                image = np.moveaxis(image, -1, 0)
            else:
                image = image
        else:
            image = image

    return image


def img_dataset_from_dir(dir_path):
    """
    Given a directory containing folders
    representing classes of images, this
    functions builds a valid numpy
    dataset distribution. 
    Input (dir_path) structure: 
    dir_path/class_1, class_n/1.png 
    Note: 'dir_path' must be the raw
    dir name (no trailing dash) 
    Output: [(x,y), ..., (x,y)]
    """

    dir_path = dir_path + "/*/"
    class_list = glob(dir_path, recursive = True)
    
    master_list = []
    idx = 0
    for class_ in class_list:
        curr_class = image_dir_to_data_norm(class_, "png")
        new_arrays = []
        for elem in curr_class:
            if len(elem.shape) == 2:
                elem = np.expand_dims(elem, axis=0)
            assert len(elem.shape) == 3
            if elem.shape[0] != 3 and elem.shape[2] == 3:
                elem = np.moveaxis(elem, -1, 0)
            elif elem.shape[0] != 1 and elem.shape[2] == 1:
                elem = np.moveaxis(elem, -1, 0)
            new_arrays.append(elem)

        labeled_list = gen_label_pair(new_arrays, idx)
        master_list.append(labeled_list)
        idx += 1

    return gen_distro(master_list)


def print_model_size(net):
    """
    Function that calculates PyTorch model size
    and prints it out in mb, bytes, and num params.  
    """
    # taken from 
    # https://stackoverflow.com/questions/49201236/check-the-total-number-of-parameters-in-a-pytorch-model
    total_params = sum(p.numel() for p in net.parameters())
    
    # taken from 
    # https://discuss.pytorch.org/t/finding-model-size/130275/2 
    param_size = 0
    for param in net.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in net.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_all_mb = (param_size + buffer_size) / 1024**2
    
    print("Total number of parameters: ", total_params)
    print("model size (bytes): ", (param_size + buffer_size))
    print('model size (mb): {:.3f}MB'.format(size_all_mb))


class MeanMetric:
  """
  Scalar metric designed to use on a per-epoch basis 
  and updated on per-batch basis. For getting average across
  the epoch. 
  """

  def __init__(self):
    self.vals = []

  def update(self, new_val):
    self.vals.append(new_val)

  def reset(self):
    self.vals = []

  def get(self):
    mean_value = sum(self.vals)/len(self.vals)
    return mean_value
    


def numpy_collate(batch):
    """batch collate function but keep as numpy array instead 
    of converting to torch tensor like pytorch default does. inputs
    must be np.arrays 
    https://github.com/pytorch/pytorch/blob/35c8f93fd238d42aaea8fd6e730c3da9e18257cc/torch/utils/data/dataloader.py#L218
    """

    r_tuple = []

    for i in range(len(batch[0])):
        arrays_to_stack = []
        for j in range(len(batch)):
            arrays_to_stack.append(batch[j][i])
        stacked = np.stack(arrays_to_stack, axis=0)
        r_tuple.append(stacked)
    
    return tuple(r_tuple)


def load_image(img_path, resize=None, normalize=True):
    """
    Loads an image file into a numpy array in (C, H, W) form. 
    Arguments:
    -----------
    - img_path (str): image filename (relative) 
    - resize (tuple): (x, y) size to resize to. If None, won't resize. Default = None. 
    - normalize: if True, divide by 255. 
    Returns:
    -----------
    - image_array: loaded numpy array of the image file     
    """
    
    x = Image.open(img_path)
    image_array = np.array(x)

    # remove transparency dimension if it exists 
    if image_array.shape[-1] == 4 and len(image_array.shape) == 3:
        image_array = image_array[:, :, :3]
    elif image_array.shape[0] == 4 and len(image_array.shape) == 3:
        image_array = image_array[:3, :, :]
    
    # if image has only 2 channels, add a third channel
    if len(image_array.shape) == 3 and image_array.shape[-1] == 2:
        image_array = np.concatenate([np.expand_dims(image_array[:, :, -1], axis=-1), image_array], axis=-1)
    elif len(image_array.shape) == 3 and image_array.shape[0] == 2:
        image_array = np.concatenate([np.expand_dims(image_array[-1, :, :], axis=0), image_array], axis=0)

    if normalize:
        image_array = image_array / 255.0

    # if image is grayscale, add a channel dimension
    if len(image_array.shape) == 2:
        image_array = np.expand_dims(image_array, axis=0)
    
    assert len(image_array.shape) == 3

    # switch dim 
    if (image_array.shape[0] != 3 and image_array.shape[2] == 3) or (image_array.shape[0] != 1 and image_array.shape[2] == 1):
        image_array = np.moveaxis(image_array, -1, 0)

    assert image_array.shape[0] == 3 or image_array.shape[0] == 1

    # resize 
    if resize is not None:
        image_array = np.array(T.Resize(size=resize)(torch.tensor(image_array)))

    return image_array



# v2 functions 

def img_dir_to_data(dirpath, resize=None, normalize=True, extension=None):
    """
    (New version of image_dir_to_data). 
    Takes in a directory containing images
    and returns a list of numpy arrays representing
    those images. 
    Args:
        - dirpath: path to directory 
        - extension: include only files with this extension. Default = None. 
        - resize: tuple of (h, w) for what to resize the images to. If None, won't resize. Default = None. 
        - normalize: if True, divide by 255. 
    """
    data_subset = []
    if extension is not None:
        dirpath = dirpath + "/*." + extension
    else:
        dirpath = dirpath + "/*"
    sub_set = glob(dirpath)

    for elem in sub_set:
        image = load_image(elem, resize=resize, normalize=normalize)
        data_subset.append(image)

    return data_subset  



def classification_dataset(dir_path, resize=None, normalize=True, extension=None):
    """
    (New version of img_dataset_from_dir).  
    Given a directory containing folders
    representing classes of images, this
    functions builds a valid numpy
    dataset distribution. 
    Input (dir_path) structure: 
    dir_path/class_1, class_n/1.png 
    Note: 'dir_path' must be the raw
    dir name (no trailing dash) 
    Output: [(x,y), ..., (x,y)]
    Arguments:
    - dir_path (str): path to the directory containing the class folders. 
    - resize: tuple of (h, w) for what to resize the images to. If None, won't resize. Default = None. 
    - normalize: if True, divide by 255. Default = True. 
    - extension: include only files with this extension. Default = None. 
    """

    dir_path = dir_path + "/*/"
    class_list = glob(dir_path, recursive = True)
    
    master_list = []
    idx = 0
    tqdm_class_idx = 1
    tqdm_class_list = tqdm(class_list)
    for class_ in tqdm_class_list:
        tqdm_class_list.set_description(f"Loading class {tqdm_class_idx}")
        tqdm_class_idx += 1
        curr_class = img_dir_to_data(class_, resize, normalize, extension)
        new_arrays = []
        for elem in curr_class:
            if len(elem.shape) == 2:
                elem = np.expand_dims(elem, axis=0)
            assert len(elem.shape) == 3
            if elem.shape[0] != 3 and elem.shape[2] == 3:
                elem = np.moveaxis(elem, -1, 0)
            elif elem.shape[0] != 1 and elem.shape[2] == 1:
                elem = np.moveaxis(elem, -1, 0)
            new_arrays.append(elem)

        labeled_list = gen_label_pair(new_arrays, idx)
        master_list.append(labeled_list)
        idx += 1

    return gen_distro(master_list)
