### Intro

Indecro is a simple framework for job scheduling

All parts are designed to be replaceable.

Main ideas are:

* Task creator doesn't need to know how tasks are implemented or executed
* Persistence may be implemented
* You can choose how jobs will be parallelized and whether they will be parallelized at all
* Not only time-based scheduling rules! Magic filters and bool-based rules is available

Currently project is in the design stage and any APIs are to be changed


### How to install:

#### Install using pip
```bash
pip install indecro
```

### How to use:

Create scheduler

```python
from indecro import Scheduler
from indecro.executor import Executor
from indecro.storage.memory_storage import MemoryStorage

scheduler = Scheduler(
    executor=Executor(),
    storage=MemoryStorage()
)
```

Schedule job using decorator-based shortcut (custom job name can be provided for compatibility)

```python
from datetime import timedelta

from indecro.rules import RunOnce


# Rule, theft control time when scheduled task would be executed
@scheduler.job(rule=RunOnce(after=timedelta(seconds=10)))
async def some_job():
    print('Executing some job..')
```

Schedule job using direct function

```python
async def some_another_job():
    print('Executing some another job..')


scheduler.add_job(
    some_another_job,
    rule=RunOnce(after=timedelta(seconds=20))
)
```

Run scheduler:

```python
await scheduler.run()
```

More examples of using framework you can find in examples directory

```bash
cd examples
ls
```
