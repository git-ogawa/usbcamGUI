# Test page

This is a test page.


The page is generated from markdown with [myst](https://myst-parser.readthedocs.io/en/latest/index.html)

## admonition
:::{note}
This is note
:::

:::{tip}
This is tip
:::

:::{example}
This is example
:::

:::{warning}
This is warning
:::

:::{danger}
This is danger
:::


## math 
$$
a + b = c
$$

$$
i \hbar \frac{d\psi}{dt} = H \psi
$$


## table 
| a | b | 
| :-- | :-- |
| c | d |


## fenced code block
```{code-block} python
---
lineno-start: 1
emphasize-lines: 1, 3
caption: |
    This is my
    multi-line caption. It is *pretty nifty* ;-)
---
a = 2
print('my 1st line')
print(f'my {a}nd line')
```


```{code-block} python
---
lineno-start: 1
---
class Super():

    def __init_(self, var):
        self.var = var

    def show(self):
        print(self.var)

    @staticmethod
    def printer():
        print("this is a static method")
```