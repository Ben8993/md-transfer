Alright — here’s a clean one-page runbook for restoring SonarQube on AKS with Azure PostgreSQL Flexible Server. Copy this to your docs, GitOps repo, or Confluence.

⸻

📄 Runbook: Restore SonarQube on AKS (Azure PostgreSQL Flexible Server)

⸻

✅ Purpose

Restore SonarQube including:
	•	Projects & issues
	•	Groups, permission templates, users
	•	Tokens & settings (stored in DB)

⸻

✅ Scope
	•	SonarQube deployed via Helm on AKS
	•	PostgreSQL hosted on Azure Flexible Server
	•	DB backup available as .sql dump

⸻

✅ Steps

⸻

1️⃣ Scale down SonarQube

# Adjust namespace as needed
kubectl scale deployment sonarqube-sonarqube --replicas=0 -n <namespace>

👉 Prevents new writes during DB restore.

⸻

2️⃣ Restore PostgreSQL Flexible Server

Run locally or from a jump host that can connect to the DB.
Example using psql:

# Drop old DB
psql "host=<server>.postgres.database.azure.com port=5432 dbname=postgres user=<admin>@<server> sslmode=require" \
  -c "DROP DATABASE sonarqube;"

# Recreate DB
psql "host=<server>.postgres.database.azure.com port=5432 dbname=postgres user=<admin>@<server> sslmode=require" \
  -c "CREATE DATABASE sonarqube;"

# Restore from backup
psql "host=<server>.postgres.database.azure.com port=5432 dbname=sonarqube user=<admin>@<server> sslmode=require" \
  < backup.sql

✅ Notes:
	•	Replace <server> and <admin>.
	•	Always use sslmode=require.
	•	If you have a .dump instead of .sql, use pg_restore.

⸻

3️⃣ Scale SonarQube back up

kubectl scale deployment sonarqube-sonarqube --replicas=1 -n <namespace>

Or redeploy if configs changed:

helm upgrade <release-name> sonarqube/sonarqube -n <namespace> --reuse-values


⸻

4️⃣ Verify
	•	Login to SonarQube UI.
	•	Confirm:
	•	✅ Projects exist
	•	✅ Groups & permission templates match
	•	✅ Users & tokens restored

⸻

5️⃣ Tips

✅ For large restores:
	•	Use pg_restore with parallel jobs: pg_restore -j 4 ...
	•	Consider Azure’s point-in-time restore to spin up a clone instead of dropping live DB.

✅ Backup your Helm values.yaml for disaster recovery.

✅ Check DB version compatibility with your SonarQube version.

⸻

✅ Contact

Who	Contact
DBA	dba@company.com
DevOps	devops@company.com


⸻

📌 File: restore-sonarqube.md
Owner: Platform Engineering
Last Updated: <today’s date>

⸻

If you want, I can wrap this as a Markdown file with placeholders & comments — just say “yes, turn it into a file” and I’ll generate it instantly! 🚀