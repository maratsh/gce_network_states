# Several states for managing network GCE


## gce_address 

Creates static address

```yaml
firewall-rule:
  new_address:
    - present
    - name: new_address
```    

## gce_firewall

Creates new firewall rule

```yaml

firewall-rule:
 gce_firewall:
  - present
  - name: firewall-rule
  - provider: gce-provider
  - network: newnet
  - allow: 10.0.0.0/24
  - src_tags: web
  - dst_tags: base
  - src_range: 10.0.0.1/24
  - require:
    - gce_network: newnet

```

# gce_nwteork

Creates new network

```yaml

newnet:
  gce_network:
    - present
    - name: newnet
    - cidr: 10.0.0.0/24
    - provider:  gce-provider
