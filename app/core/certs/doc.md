```
# 2. สร้าง CA Key & Cert (บังคับ Encoding เป็น ASCII)
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=MyLocalCA/O=MyCompany"

# 3. สร้าง Server Key & CSR
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=localhost/O=MyCompany"

# 4. สร้างไฟล์ SAN Config (ต้องใช้ Out-File แบบ ascii เพื่อไม่ให้ติด BOM)
@"
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
"@ | Out-File -FilePath server_ext.cnf -Encoding ascii

# 5. ให้ CA เซ็น Server Cert
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -extfile server_ext.cnf

# 6. สร้าง Client Key, CSR และเซ็น Client Cert
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=grpc-client/O=MyCompany"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365
```

```
openssl verify -CAfile ca.crt server.crt
# server.crt: OK
```

```
Remove-Item server.csr, client.csr, server_ext.cnf, ca.srl -Force
```

# Key

_.key
_.srl
\*.csr
