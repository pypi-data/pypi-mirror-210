# JobSync API-Quota-Manager Library
### To install
```bash
pip install apiquotamanager
```
---
## Quota Management
### To import
```python
from apiquotamanager.taleo_quota_manager import QuotaManager
```
### Example
```python
from apiquotamanager.taleo_quota_manager import QuotaManager
obj_q = QuotaManager('taleo-enterprise-api')
obj_q.calculate_requests_quota(total_quota=2000, used_quota=500, qtime='1 minute')
obj_q.calculate_requests_quota(total_quota=2000, used_quota=500, qtime='1 hour')
obj_q.calculate_requests_quota(total_quota=2000, used_quota=500, qtime='1 day')
obj_q.calculate_requests_quota(total_quota=2000, used_quota=500, qtime='1 month')
obj_q.calculate_requests_quota(total_quota=2000, used_quota=500, qtime='1 year')
```
