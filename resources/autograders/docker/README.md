
``` bash
# From IArena/.

# Activate IArena environment
# source .venv/bin/activate

# Build docker
sudo docker build -t iarena-grader:multigrader --no-cache resources/autograders/docker/

# Build docker with specific branch
# sudo docker build --build-arg IARENA_REF=jparisu/multigrader -t iarena-grader:multigrader --no-cache resources/autograders/docker/

# Run docker
sudo docker run --rm -v "$(pwd)/resources/autograders/docker/shared:/data" iarena-grader:multigrader --zip-file /data/IA_2526_P1_01.zip --configuration-file https://raw.githubusercontent.com/jparisu/IArena/refs/heads/main/resources/graders/IA_MAT_2526_wordle_norep.yaml --result-file /data/result.csv --repetitions 10
```
