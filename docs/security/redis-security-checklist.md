# Redis Security Checklist

This checklist should be used to verify Redis security settings before deploying to production and during regular security audits.

## Basic Security

- [ ] Redis runs with a non-default configuration file
- [ ] Authentication is enabled with a strong password
- [ ] Protected mode is enabled
- [ ] Redis is not running as root user
- [ ] Redis data directory has proper permissions (700 or 750)
- [ ] Redis is bound to specific interfaces only (not 0.0.0.0 without protection)
- [ ] Connection timeout is set appropriately (timeout 300)
- [ ] Max clients limit is set appropriately for the environment

## Network Security

- [ ] Redis port (6379) is not exposed publicly
- [ ] Firewall rules limit access to Redis port
- [ ] Network policy restricts pod-to-pod communication (in Kubernetes)
- [ ] TLS/SSL is configured for Redis connections when appropriate
- [ ] Redis is separated into its own network segment
- [ ] Regular network vulnerability scans include Redis ports

## Command Security

- [ ] Dangerous commands are renamed or disabled (FLUSHALL, FLUSHDB, CONFIG, etc.)
- [ ] Redis command audit logging is enabled
- [ ] ACLs are used to limit user permissions (Redis 6.0+)
- [ ] Memory limits are set to prevent DoS (maxmemory setting)

## Monitoring and Alerting

- [ ] Redis logs are collected and monitored
- [ ] Alerts are configured for authentication failures
- [ ] Alerts are configured for Cross Protocol Scripting attempts
- [ ] Redis metrics are monitored (memory, connections, commands)
- [ ] Unexpected use of sensitive commands triggers alerts

## Backup and Recovery

- [ ] Regular backups of Redis data are configured
- [ ] Backup integrity is verified regularly
- [ ] Recovery procedure is documented and tested
- [ ] Point-in-time recovery is possible through AOF if needed

## Compliance and Documentation

- [ ] Redis version is current and supported
- [ ] Redis security settings are documented
- [ ] Security configurations are version-controlled
- [ ] Change management process exists for Redis configuration changes

## Regular Maintenance

- [ ] Security patches are applied promptly
- [ ] Redis configuration is reviewed quarterly
- [ ] Redis security testing is performed with each major version upgrade
- [ ] Penetration testing includes Redis instances

---

**Validation Frequency**: This checklist should be completed:
- Before initial production deployment
- After any significant Redis configuration change
- Quarterly as part of regular security reviews
- After any Redis-related security incident
