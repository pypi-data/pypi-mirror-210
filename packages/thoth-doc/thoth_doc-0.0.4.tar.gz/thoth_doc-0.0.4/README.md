# Thoth doc: Dependency-free, lightweight docstring parser
![Thoth image](Thoth.svg.png)


## Installation
```bash
pip install thoth-doc
```

## Usage
```python
# code.py

def foo(bar: int, baz: str = "qux") -> None:
    """This is a docstring"""
    pass


class Foo:
    """This is a class docstring"""

    def bar(self, bar: int, baz: str = "qux") -> None:
        """This is a method docstring"""
        pass
```


```python
from thoth_doc import get_docstring

docstring = get_docstring("code.py", "foo")  # find docstring of foo in code.py
print(docstring)  # "This is a docstring"

docstring = get_docstring("code.py", "Foo")  # find docstring of Foo class in code.py
docstring = get_docstring("code.py", "Foo.bar")  # find docstring of Foo.bar method in code.py
```


## License
[MIT License](LICENSE)
