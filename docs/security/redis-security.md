# Redis Security Configuration Guide

## Overview
This document outlines the security configuration implemented for Redis instances in the Summiva project, addressing potential security vulnerabilities like Cross Protocol Scripting (XPS) attacks.

## Security Measures Implemented

### 1. Protected Mode and Authentication
- **Protected Mode**: Enabled by default to prevent connections from outside the loopback interface
- **Password Authentication**: Required for all connections
- **Connection Timeout**: Set to prevent hanging connections

### 2. Network Security
- **Bind Address**: Configured to only allow connections from specified networks
- **Port Configuration**: Standard port 6379, but with enhanced security controls

### 3. Command Restrictions
- **Dangerous Commands Disabled**: FLUSHALL, FLUSHDB, CONFIG, DEBUG commands have been disabled
- **Resource Limits**: Max memory and client connections are capped to prevent DoS attacks

### 4. SSL/TLS Support
- Optional SSL/TLS encryption for Redis connections

## How to Apply Configuration

### Docker Compose
Redis configuration is applied through:
- A mounted `redis.conf` file at `/usr/local/etc/redis/redis.conf`
- Environment variable `REDIS_PASSWORD` for authentication

### Kubernetes
Redis configuration is applied through:
- A ConfigMap containing the Redis configuration
- A Secret containing the Redis password

## Warning Signs to Watch For

If you see a log message like:
```
Possible SECURITY ATTACK detected. It looks like somebody is sending POST or Host: commands to Redis.
```

This indicates a potential Cross Protocol Scripting (XPS) attack attempt. Redis automatically blocks these attempts when configured correctly.

## Troubleshooting

If Redis fails to start after applying these security settings:
1. Check that the configuration file is correctly mounted
2. Verify that environment variables are correctly set
3. Check Redis logs for specific error messages

## References
- [Redis Security Documentation](https://redis.io/topics/security)
- [Redis Protected Mode](https://redis.io/topics/security#protected-mode)
- [Cross Protocol Scripting](https://www.exploit-db.com/docs/english/47655-redis---ssrf-to-get-remote-code-execution.pdf)
