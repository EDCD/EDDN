"""Inform the invoker they ran `pytest` in the wrong place."""
print('You must run `pytest` from inside the `src/` directory')
assert False
