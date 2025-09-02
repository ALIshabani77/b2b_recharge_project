# Fix for recharge/models.py Issues

## Current Issues
1. [Pylance] "models" is not accessed
2. [Ruff] `django.db.models` imported but unused

## Analysis
The `recharge/models.py` file currently contains:
```python
from django.db import models

# Create your models here.
```

The import statement is unused because no actual models have been defined yet. This is causing both Pylance and Ruff warnings.

## Proposed Solutions

### Option 1: Remove Unused Import (Temporary Fix)
If no models are needed yet, we can remove the import:
```python
# Create your models here.
```

### Option 2: Add a Sample Model (Recommended)
Add a basic model to make use of the import and provide a foundation for future development:
```python
from django.db import models

class Recharge(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recharge: {self.amount}"
```

## Recommendation
Option 2 is recommended as it provides a useful starting point for the recharge app functionality while resolving the warnings.