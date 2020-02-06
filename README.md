# Language Models for Text Classification

## Usage

```sh
python build_test_LM.py -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file

# Example
python build_test_LM.py -b temp.txt -t input.test.txt -o input.out.txt

python build_test_LM.py -b input.train.txt -t input.test.txt -o input.out.txt
```

## Evaluation

```sh
python eval.py file-containing-your-results file-containing-correct-results

# Example
python eval.py input.out.txt input.correct.txt
```
