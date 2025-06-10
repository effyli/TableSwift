TableSwift is a python package that can do different types of data wrangling, using LLMs with code generation.

This package currently supports three functions. 
To start using the package, first configurre with your API key. 
```
ts.configure(api_key="your API key here.")
```
Or alternatively define yoru API key in the system environment using variable name TABLESWIFT_API_KEY.



To generate labels, use:
```
labeled_data = ts.generate_labels(instruction="label the input samples", 
                                      task="data_transformation",
                                      column_name="name",
                                      demonstrations=[{"Input": "sample1", "Output": "label1"},
                                                     {"Input": "sample2", "Output": "label2"}],
                                      samples_to_label=[{"Input": "sample1", "Output": ""},
                                                        {"Input": "sample2", "Output": ""},
                                                        {"Input": "sample3", "Output": ""}])
```

To generate code, use:
```
code, router_code = ts.generate_code(instruction="Transform input into output",
                     task="data_transformation",
                     samples=[{"Input": "sample1", "Output": "label1"},
                              {"Input": "sample2", "Output": "label2"}],
                     lang="python")
```

There are also hyperparameters that can be overriden, to do so, use:
```
code, router_code = ts.generate_code(instruction="Transform input into output",
                     task="data_transformation",
                     samples=[{"Input": "sample1", "Output": "label1"},
                              {"Input": "sample2", "Output": "label2"}],
                     lang="python",
                     num_trials=1,
                     num_retry=3,
                     num_iterations=1)
```

A list of hyperparameters with their defaul value is:
```
DEFAULT_PARAMS = {
    "use_data_router": True,
    "num_trials": 2,
    "num_retry": 3,
    "seed": 42,
    "num_iterations": 2,
    "max_num_solutions": 3,
    "limit_fallback": 20, # number of invalid data samples before fallback, should be a percentage in the future
    "llm": "gpt-4o-mini" 
}
```

Current package supports two languages: python and duckdb SQL. To generate python code use `lang=python`, and to generate duckdb SQL query, use `lang=sql`.
Current pakcage supports the following tasks, remember to match the task parameter with the following string.
```
"data_transformation"
"entity_matching"
"error_detection_spelling"
"value_imputation"
```

