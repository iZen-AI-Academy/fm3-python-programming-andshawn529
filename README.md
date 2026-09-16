# FM2 - Python Programming

Complete the functions in `python_programming_exercises.ipynb`, then commit and push your changes.
A push triggers GitHub Actions, which automatically grades your work and syncs the score to Moodle.

## What to edit

**Edit ONLY `python_programming_exercises.ipynb`.** Write your implementation inside each function
body, in the notebook, where indicated.

Do **not** edit or delete anything in `.github/`, `scripts/`, or `tests/`, and do not create your own
`student_solution.py`. That file is generated automatically from your notebook every time you push —
any manual copy you create will be overwritten and ignored by the grader.

Functions to implement:
- `full`
- `get`
- `set`
- `equal`
- `copy`
- `transpose`
- `flatten`
- `reshape`
- `compute`
- `mean`

**Keep function names, parameters, and return values exactly as specified in the notebook.** The
autograder imports these functions by name — renaming them or changing their signatures will cause
every test to fail.

## How grading works

Pushing to `main` automatically grades your work and syncs your score to Moodle — that's it, no
separate submission step. Note: your score will **not** appear on the GitHub Classroom assignment
page. Moodle is where your grade lives.

## Checking your results

Go to the **Actions** tab of this repository and open the most recent workflow run:
- A green check on **"Run tests and write report"** means all tests passed.
- A red X means one or more tests failed — expand that step to see which function failed and why
  (the error message shows the input, expected output, and what your function actually returned).

## Testing locally (optional)

If you'd rather check your work before pushing, open a terminal in Codespaces or locally and run:

```bash
pip install -r requirements.txt
python scripts/extract_notebook.py
pytest tests/ -q
```

This runs the same tests the autograder runs, so you can see exactly which functions pass or fail
before committing.

## Notes
- Work in Codespaces or locally with Jupyter.
- You can push as many times as you like before the deadline — each push re-grades your latest work.
