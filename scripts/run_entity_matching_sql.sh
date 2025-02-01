# run duckdb sql generation for data transformation
export PYTHONPATH=/Users/Effy/workspace/full_llm_wrangler:$PYTHONPATH
export DATASET_PATH=/Users/Effy/workspace/full_llm_wrangler/data/datasets

export lang="sql"
export LLM="gpt-4"

# all with data router
/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/Fodors-Zagats/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/Beer/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/Amazon-Google/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/DBLP-ACM/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/DBLP-GoogleScholar/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/iTunes-Amazon/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

/Users/Effy/miniconda3/envs/md/bin/python /Users/Effy/workspace/full_llm_wrangler/src/run_wrangler.py --data_dir /Users/Effy/workspace/full_llm_wrangler/data/datasets/entity_matching/structured/Walmart-Amazon/  --num_trials 5  --seed 42 --k 10 --d 0 --num_iter 5 --llm $LLM --lang $lang

