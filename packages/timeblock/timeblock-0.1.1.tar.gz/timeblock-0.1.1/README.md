# 🕐 timeblock

Helpful snippet for timing blocks, basically [contexttimer](https://github.com/brouberol/contexttimer) with a few tweaks / forked.

```bash
pip install timeblock==0.1.1
```

```python
from timeblock import Timer

with Timer() as timer:
    sleep(1)

print(timer.elapsed) # 1s

with Timer(output=True):
    sleep(1)

# logger.debug(f"Elapsed time: {timer.elapsed}"

with Timer("sleepy time", output=print):
    sleep(1)

# print("sleepy time took {:.3f} seconds".format(timer.elapsed))
```
