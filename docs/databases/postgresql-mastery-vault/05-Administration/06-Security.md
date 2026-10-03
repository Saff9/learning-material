---
tags: [postgresql, admin, security, ssl, rls]
---

# Security

## Authentication Methods

| Method | Security | Use Case |
|--------|----------|----------|
| `peer` | High (OS-level) | Local connections (same machine) |
| `scram-sha-256` | High (recommended) | Remote connections with password |
| `md5` | Medium (deprecated) | Legacy — migrate to scram-sha-256 |
| `trust` | None | Development only — never in production |
| `cert` | High (SSL client cert) | High-security environments |
| `oauth` | High (PG 18+) | SSO with Azure AD, Okta |

## SSL/TLS

```ini
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

```conf
# pg_hba.conf — force SSL
hostssl all all 0.0.0.0/0 scram-sha-256 clientcert=verify-full
```

## Security Checklist

> [!important] Production Security Checklist
> - [ ] Use `scram-sha-256` for all password auth (default since PG14)
> - [ ] Force SSL with `hostssl` and `clientcert=verify-full`
> - [ ] Never use `trust` authentication in production
> - [ ] Create dedicated roles per application (not `postgres` superuser)
> - [ ] Grant only needed privileges (principle of least privilege)
> - [ ] Enable Row-Level Security for multi-tenant data
> - [ ] Keep PostgreSQL updated (security patches)
> - [ ] Audit with `pg_stat_activity` and log connections
> - [ ] Back up `pg_hba.conf` and `postgresql.conf` securely
> - [ ] Use secrets management (not plaintext passwords in config files)

## Next

- [[06-Extensions/01-PostGIS|PostGIS]]
- [[07-Application-Integration/01-Python-psycopg2|Python Integration]]
