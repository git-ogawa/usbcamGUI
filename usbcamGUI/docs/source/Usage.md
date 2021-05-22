# Welcome to MkDocs

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## code block

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.


# test

https://github.com/git-ogawa/usbcamGUI


## level2

### lebel3

#### level4


- list
- list

# admonition

!!! info

    information


!!! warning 

    warn


## definition list
define
:   list1
:   list2



# code
```python
def main(*args):
    for i in args:
        print(i)
    return True
```

## macro


:::{note}
tihs is note
:::

:::{danger}
    ddddd
:::


# def
term 1
:   def1

term2
: def2


- [ ] an item
- [x] an items  


\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}


$$
    a + b = \sigma
$$


```plantuml
bob -> alice
alice -> bob
```