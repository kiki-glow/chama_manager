# Chama Manager

Chama Manager is a Python application for managing a savings group (chama). It provides a reusable core for members, contributions, balances, loans, repayments, and loan schedules, plus a FastAPI service for accessing those features over HTTP.

The API currently keeps its data in memory. All members, contributions, and loans are reset when the server restarts.

## Requirements

- Python 3.10 or later

## Setup

Create and activate a virtual environment, then install the development dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

For running the API without development tools, install only the application dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the API

From the project root:

```powershell
python -m uvicorn api.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. Interactive API documentation is at <http://127.0.0.1:8000/docs>.

The server starts with an in-memory chama named **Umoja Savers**, configured for KES 1,000 monthly contributions, a five-day grace period, a KES 50 late fine, and reducing-balance loans at 5% monthly interest. The demo endpoint can add sample data to an empty chama:

```text
POST /demo/seed
```

## API overview

- `GET /summary` — group totals and current settings
- `GET`, `POST /members` — list or register members
- `GET /members/{member_id}` — retrieve a member
- `GET`, `POST /members/{member_id}/contributions` — view or record contributions
- `GET /members/{member_id}/balance` — check a member's balance for a period
- `GET`, `POST /loans` — list or issue loans
- `GET /loans/{loan_id}` — retrieve a loan and its schedule
- `POST /loans/{loan_id}/repayments` — record a repayment

See `/docs` for request and response schemas.

## Run the tests

```powershell
python -m unittest discover -v
```

## Type-check (optional)

`mypy` is included in the development requirements:

```powershell
mypy --strict chama_manager tests
```

## Core library example

```python
from datetime import date
from decimal import Decimal

from chama_manager import Chama, ChamaRules, FlatInterest

rules = ChamaRules(
    Decimal("1000"),
    monthly_interest_percent=Decimal("10"),
    interest_strategy=FlatInterest(),
)
chama = Chama("Umoja Savers", rules)

member = chama.add_member("Kinya", "0712 345 678")
chama.record_contribution(member.id, 2000, date(2026, 1, 3))

loan = chama.issue_loan(member.id, 1500, 3, date(2026, 1, 10))
print(loan.total_repayable)
```

## Author

**Kinya Glory**  
GitHub: <https://github.com/kiki-glow>
