# irisml-tasks

A collection of tasks for irisml framework.

Visit [irisml](https://github.com/microsoft/irisml) for the detail.

## tasks
### assertion
This task throws an exception if the given assertion failed for the input object.

## branch
'If' condition for tasks.

### calculate_cosine_similarity
Calculate cosine similarity between two sets of vectors.

### download_azure_blob
Download a file from azure blob.

### get_current_time
Get the current time in seconds from epoch.

### get_dataset_stats
Get statistics of the input dataset.

### get_dataset_subset
Create a new dataset with a subset of the input dataset.

### get_fake_image_classification_dataset
Create a new dataset with fake classification images.

### get_fake_object_detection_dataset
Create a new dataset with fake object detection examples.

### get_item
Get an item from a given list.

### get_secret_from_azure_keyvault
Get a secret string from Azure KeyVault.

### get_topk
Get TopK from a given tensor.

### join_filepath
Join a given directory path and a filename.

### load_state_dict
Load a specified file to the input model.

### print_environment_info
Print the enviromnent infomation such as GPU, CPU, Memory

### run_parallel
Run child tasks in new forked processes.

### run_sequential
Run child tasks sequentially on the same process.

### save_file
Save the input binary as a file.

### save_state_dict
Save the state_dict of the input model.

### search_grid_sequential
Grid search hyperparameters in sequential. Run the child tasks and returns a set of parameters that achieved the best result.

### upload_azure_blob
Upload a file to azure blob.
