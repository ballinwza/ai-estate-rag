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
