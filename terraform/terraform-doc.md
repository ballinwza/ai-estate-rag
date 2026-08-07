# CI/CD workflow Terraform & Github Action & GCloud Run & GCloud Artifact Registry

```
[ Developer ]
│
├─► Step 1: รัน Terraform ───► สร้าง Infrastructure บน GCP (SA, WIF, Artifact Registry)
│
├─► Step 2: Push Git Tag ────► กระตุ้น GitHub Actions Workflow
|   Example : git tag v0.0.1 -> git push origin v0.0.1
│
▼
[ GitHub Actions ]
│
├─► Step 3: OIDC Authentication (ผ่าน Workload Identity Federation)
├─► Step 4: Build & Push Docker Image ไปยัง Artifact Registry
└─► Step 5: Deploy Image ขึ้น Cloud Run (--allow-unauthenticated)
```

---

## Terraform

### Use Guide

### Manualy

1. Install Terraform follow this command:
   - Windows
     - By Chocolatey `choco install terraform`
     - By Winget (recommend) `winget install HashiCorp.Terraform`
   - MacOS
     - Homebrew `brew tap hashicorp/tap` and `brew install hashicorp/tap/terraform`

2. Checking Terraform version `terraform -v`

3. `cd ./terraform`
4. `terraform init` -> Must generate "Terraform has been successfully initialized!"

#### Or using Make command after 2

`make terra-init`

---

### Apply Guide first time run GCloud service (Optional)

- `terrform plan` check status
- `terraform apply`
- `terraform validate`
