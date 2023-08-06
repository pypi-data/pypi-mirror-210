# Backend OAuth Source API

## Local Development

1. Create a new virtual environment with Python 3.8:
```shell
python -m venv venv
source venv/bin/activate
```
2. Install testing dependencies:
```shell
make setup
```
3. Run the unit test suite:
```shell
make test_unit
```
4. Run the integration test suite:
```shell
make test_integration
```

## How to release
* Merge PR into main.
* Monitor release process in [Cloud Deploy](https://console.cloud.google.com/deploy/delivery-pipelines)

## Init a project in GKE with CI/CD based on this skeleton
1. Replace a sceleton project name with a new one. Do it twice with dashes and with underscores.
```bash
find ./ -type f -exec sed -i 's/OLD_REPO_NAME/NEW_REPO_NAME/g' {} \;
find ./ -type f -exec sed -i 's/OLD-REPO-NAME/NEW-REPO-NAME/g' {} \;
```

2. Setup infra resources
``` bash
gcloud config set project "magic-wand-ai"
gcloud auth application-default login
terraform -chdir=.google/deploy init
terraform -chdir=.google/deploy apply
```
3. Add `BACKEND_SA` GitHub repository secret with `.google/deploy/cred.json` content
