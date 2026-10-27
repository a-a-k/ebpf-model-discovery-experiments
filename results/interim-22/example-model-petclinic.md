# Observed calibration graph: petclinic

Deterministically selected absent seed 0, [run 40335553492](https://github.com/a-a-k/ebpf-model-discovery-experiments/actions/runs/40335553492). This is the validated parsing view of retained eBPF calibration observations. Observed protocol labels are preserved; an edge is not independent proof of correctness. The original model and forecast remain unchanged.

```mermaid
flowchart LR
  n0["visits-service | guest b | visits-b"]
  n1["mysql 192.168.76.11:13306"]
  n2["visits-proxy | guest a | visits-proxy.petclinic-a-visits-proxy-1"]
  n3["database | guest a | database.petclinic-a-database-1"]
  n4["customers-service | guest a | customers-a"]
  n5["mysql 172.28.11.20:3306"]
  n6["vets-service | guest a | vets-a"]
  n7["visits-service | guest a | visits-a"]
  n8["api-gateway | guest a | gateway-a"]
  n8 -->|observed_parent_id| n4
  n8 -->|observed_parent_id| n6
  n8 -->|observed_parent_id| n2
  n4 -->|database_client_span| n5
  n4 -->|observed_parent_id| n3
  n6 -->|database_client_span| n5
  n6 -->|observed_parent_id| n3
  n2 -->|observed_parent_id| n7
  n2 -->|observed_parent_id| n0
  n7 -->|database_client_span| n5
  n7 -->|observed_parent_id| n3
  n0 -->|database_client_span| n1
```
