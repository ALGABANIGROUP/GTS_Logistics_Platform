# Integration Profile

Last updated: 2026-03-28

## Environments
| Environment | Base URL | Auth method | Notes |
|---|---|---|---|
| dev | https://dev-api.gtsdispatcher.com | API key or OAuth2 | Sandbox for internal testing |
| staging | https://staging-api.gtsdispatcher.com | API key or OAuth2 | Pre-production validation |
| prod | https://api.gtsdispatcher.com | API key or OAuth2 | Live production traffic |

## Rate Limits (Default)
| Provider Type | Default Rate Limit | Notes |
|---|---|---|
| loadboard | 60 req/min | 1 request per second |
| carrier | 120 req/min | Burst up to 2 requests per second |
| payment | 30 req/min | Lower limit for financial operations |
| tracking | 300 req/min | Higher limit for real-time updates |
| webhook | 500 req/min | High volume from external systems |

## Reference
For the full operational profile and checklist, see docs/operations/GTS_INTEGRATION_PROFILE.md.