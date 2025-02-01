# run duckdb sql generation for data transformation
export PYTHONPATH=/Users/Effy/workspace/full_llm_wrangler:$PYTHONPATH
export DATASET_PATH=/Users/Effy/workspace/full_llm_wrangler/data/datasets
export LLM="llama3.1-405b"
export lang="sql"

# googlerefine without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-FF-Trifacta-GoogleRefine  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# headcase without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-headcase  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# stackoverflow without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-stackoverflow  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang
