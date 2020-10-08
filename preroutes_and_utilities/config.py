import json
import sys

f = open("Dockerrun.aws.json", "r")
docker = json.load(f)

docker_id = input("Docker ID: ").lower()

if docker_id == "exit" or docker_id == "quit" or docker_id == "q":
    print("Exiting program...")
    sys.exit()

elif docker_id == "reset":
    docker["Image"]["Name"] = "DOCKER_ID/labs26-citrics-ds-teama_web:latest"

elif docker_id == "reset team":
    docker["Image"]["Name"] = "ekselan/labs26-citrics-ds-teama_web:latest"

else:
    docker["Image"]["Name"] = docker_id + "/labs26-citrics-ds-teama_web:latest"

f = open("Dockerrun.aws.json", "w")
json.dump(docker, f, indent=2)
f.close()

print(json.dumps(docker, indent=2))
