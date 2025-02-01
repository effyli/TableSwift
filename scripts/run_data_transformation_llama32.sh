# run duckdb sql generation for data transformation
export PYTHONPATH=/Users/Effy/workspace/full_llm_wrangler:$PYTHONPATH
export DATASET_PATH=/Users/Effy/workspace/full_llm_wrangler/data/datasets
export LLM="llama3.2"  # Define the LLM parameter here
export lang="python"

# bing-query-logs-semantics without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-bing-query-logs-semantics  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# bing-query-logs-unit without data router 
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-bing-query-logs-unit  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# google refine with data router
# /Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-FF-Trifacta-GoogleRefine  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --use_data_router --use_fallback --llm $LLM --lang $lang

# googlerefine without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-FF-Trifacta-GoogleRefine  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# headcase with data router
# /Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-headcase  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --use_data_router --use_fallback --llm $LLM --lang $lang

# headcase without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-headcase  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang

# stackoverflow with data router
# /Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-stackoverflow  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --use_data_router --use_fallback --llm $LLM --lang $lang

# stackoverflow without data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/data_transformation/benchmark-stackoverflow  --num_trials 3  --seed 42 --k 3 --d 0 --num_iter 5 --llm $LLM --lang $lang