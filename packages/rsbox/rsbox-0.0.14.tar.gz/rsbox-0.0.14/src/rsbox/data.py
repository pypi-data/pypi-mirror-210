"""
File: data.py 
-------------- 
Utility functions for data processing for machine learning projects.   
""" 

import boto3
import ml
import imageio
import io
import torch
from torch.utils.data import Dataset
from PIL import Image



class S3ImageClassificationDataset(Dataset):
    def __init__(self, s3_bucket, extension='.png', resize=None, normalize=False):
        print('Initializing S3ImageClassificationDataset...')
        
        # init vars 
        self.s3_client = boto3.client('s3')
        self.s3_bucket = s3_bucket
        self.extension = extension

        # transformations 
        self.resize = resize
        self.normalize = normalize

        # class folders 
        self.class_folders = self.get_all_folders_in_bucket(self.s3_bucket) 

        filepaths, labels = self.get_filepaths_and_labels()

        # zip 
        assert len(filepaths) == len(labels)
        self.data_dist = list(zip(filepaths, labels))

        print('Done initializing S3ImageClassificationDataset.')


    def get_all_folders_in_bucket(self, bucket_name):
        # to get the class names 

        folders = []

        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Delimiter='/')

        # Retrieve common prefixes (folders)
        if 'CommonPrefixes' in response:
            folders.extend([prefix['Prefix'] for prefix in response['CommonPrefixes']])

        # Continue retrieving folders if there are more pages
        while response['IsTruncated']:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Delimiter='/', ContinuationToken=response['NextContinuationToken'])
            if 'CommonPrefixes' in response:
                folders.extend([prefix['Prefix'] for prefix in response['CommonPrefixes']])

        return folders
    

    def get_filepaths_with_extension_in_folder(self, bucket_name, folder_name, file_extension):
        filepaths = []

        response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

        # Retrieve file paths with the specified extension
        if 'Contents' in response:
            filepaths.extend([obj['Key'] for obj in response['Contents'] if obj['Key'].endswith(file_extension)])

        # Continue retrieving file paths if there are more pages
        while response['IsTruncated']:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name, ContinuationToken=response['NextContinuationToken'])
            if 'Contents' in response:
                filepaths.extend([obj['Key'] for obj in response['Contents'] if obj['Key'].endswith(file_extension)])

        return filepaths
    

    def get_filepaths_and_labels(self):
        filepaths = []
        labels = []

        for i, class_name in enumerate(self.class_folders):
            curr_paths = self.get_filepaths_with_extension_in_folder(self.s3_bucket, class_name, self.extension)
            filepaths.extend(curr_paths)
            labels.extend([i] * len(curr_paths))
        
        return filepaths, labels
    

    def load_s3_image(self, bucket_name, image_name):
        # Load image from S3
        response = self.s3_client.get_object(Bucket=bucket_name, Key=image_name)
        image_bytes = response['Body'].read()
        image_stream = io.BytesIO(image_bytes)
        img = ml.load_image(image_stream, resize=self.resize, normalize=self.normalize)
        
        return img 
    

    def __getitem__(self, index):
        sample_path = self.data_dist[index][0]
        label = self.data_dist[index][1]

        sample = self.load_s3_image(self.s3_bucket, sample_path)
        sample = torch.tensor(sample, dtype=torch.float)
        label = torch.tensor(label)

        return (sample, label) 
    

    def __len__(self):
        return len(self.data_dist)
    