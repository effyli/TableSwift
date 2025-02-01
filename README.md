Following work by [Narayan et al.](https://arxiv.org/abs/2205.09911), we use the same set of benchmark [datasets](https://github.com/HazyResearch/fm_data_tasks).
You can clone the repo and download the data by using:

```
git clone git@github.com:effyli/efficient_llm_data_wrangling.git
mkdir data/
wget https://fm-data-tasks.s3.us-west-1.amazonaws.com/datasets.tar.gz -P data
tar xvf data/datasets.tar.gz -C data/
```

To run the script, first setup the data_dir environmental variable by using:

```
export DATASET_PATH="$PWD/data/datasets"
```
