The README is availabe as a <a href='README.ipynb'>Jupyter notebook</a>. The object structure is represented as a <a href="./docs/object_structure.json">dictionary</a>.

Log in to the container to work interactively:
```
docker run -it -w /home -v $(pwd):/home learners bash
```

Run a predefined learner from the current directory `$(pwd)`:
```
docker run -it -w /home -v $(pwd):/home learners python main.py $1
```