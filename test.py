import argparse

# Ustawienia dla argumentów CLI
parser = argparse.ArgumentParser(description="Generate a Kubernetes Job to initialize data for nginx StatefulSet")
parser.add_argument('--replicas', type=int, required=True, help="Number of replicas for the StatefulSet")
args = parser.parse_args()

# Pobranie liczby replik z argumentu CLI
replicas = args.replicas

# Nagłówek YAML-a dla joba
job_yaml = """
apiVersion: batch/v1
kind: Job
metadata:
  name: setup-data-nginx
spec:
  template:
    spec:
      containers:
        - name: setup-container
          image: busybox
          command: ["/bin/sh", "-c"]
          args:
"""

# Generowanie args dla każdej instancji, usuwając '&&' z ostatniego polecenia
job_yaml += "            - |\n"
for i in range(replicas):
    job_yaml += f'              echo "Initializing data for nginx-{i}..." && \\\n'
    if i < replicas - 1:
        job_yaml += f'              echo "Data for nginx-{i}" > /mnt/nginx-data-{i}/index.html && \\\n'
    else:
        job_yaml += f'              echo "Data for nginx-{i}" > /mnt/nginx-data-{i}/index.html\n'

# Dodawanie volumeMounts z różnymi mountPath dla każdej instancji
job_yaml += "          volumeMounts:\n"
for i in range(replicas):
    job_yaml += f"            - name: nginx-data-{i}\n"
    job_yaml += f"              mountPath: /mnt/nginx-data-{i}\n"

# Dodawanie volumes dla każdej instancji
job_yaml += "      volumes:\n"
for i in range(replicas):
    job_yaml += f"        - name: nginx-data-{i}\n"
    job_yaml += f"          persistentVolumeClaim:\n"
    job_yaml += f"            claimName: nginx-data-nginx-{i}\n"

# Zakończenie spec Joba
job_yaml += """
      restartPolicy: Never
  backoffLimit: 4
"""

# Zapisujemy wygenerowany YAML do pliku jobs-nginx.yaml
with open("jobs-nginx.yaml", "w") as f:
    f.write(job_yaml)

print("Job YAML generated successfully.")
