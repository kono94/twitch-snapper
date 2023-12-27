### Deployment Strategy

We utilize GitOps (as Dirk calls it) to deploy on the remote server. The deployment is kicked of when a new tag is pushed to the git repository. The Github Action Ci pipeline will just call the `deployment/update_via_ci.sh` script in the repo, everything will be built on the remote server. Hence, the process will look like this:

First, on the remote server, we have to `git clone` this repository and place the `age` private key in the `deployment/` folder. Then, for every tag pushed to this repository, the `deployment/update_via_ci.sh` is called from within the github pipeline on the remote server via ssh (a private ssh key is stored in the secrets on github for the `snapper` user that just has the permissions to call this specific script via the setuid-bit). The first argument for the script is the current tag, extracted by the pipeline. This tag is also used to build a docker container for the application. Additionally, `age` will decrypt the secrets for the `docker.env` and `.env.compose` which includes all secrets for the database and twitchAPI. Finally, `docker compose up -d` restarts the whole application.

#### Encrypt

```bash
cat deployment/docker.env | age -r age1r55yqzcf0qahgn54g3n6y7wncqxx9d80f024l3ck4kn36adw8gfspcnp4e | base64 > deployment/docker.env.encrypted
```

#### Decrypt

```bash
cat deployment/.env.compose.encrypted | base64 -d | age --decrypt -i key.txt > deployment/.env.compose
```

### Database Handling

Using phpMyAdmin:

```bash
ssh -L 8099:localhost:8099 <remote_host>
```
