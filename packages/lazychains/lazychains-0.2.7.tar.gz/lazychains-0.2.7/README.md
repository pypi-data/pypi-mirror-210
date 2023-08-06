# Package Description

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/sfkleach/lazychains/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/sfkleach/lazychains/tree/main) [![Documentation Status](https://readthedocs.org/projects/lazychains/badge/?version=latest)](https://lazychains.readthedocs.io/en/latest/?badge=latest)

A Python library to provide "chains", which are Lisp-like singly linked lists 
that support the lazy expansion of iterators. For example, we can construct a 
Chain of three characters from the iterable "abc" and it initially starts as 
unexpanded, shown by the three dots:

```py
>>> from lazychains import lazychain
>>> c = lazychain( "abc")
>>> c
chain([...])
```

We can force the expansion of *c* by performing (say) a lookup or by forcing the whole
chain of items by calling expand:

```py
>>> c[1]                   # Force the expansion of the next 2 elements.
True
>>> c
chain(['a','b',...])
>>> c.expand()             # Force the expansion of the whole chain.
chain(['a','b','c'])
```

Chain are typically a lot less efficient than using ordinary arrays. So,
almost all the time you should carry on using ordinary arrays and/or tuples.
But Chains have a couple of special features that makes them the 
perfect choice for some problems.

   * Chains are immutable and hence can safely share their trailing segments.
   * Chains can make it easy to work with extremely large (or infinite) 
     sequences.

Expanded or Unexpanded
----------------------

When you construct a chain from an iterator, you can choose whether or not
it should be immediately expanded by calling chain rather than lazychain.
The difference between the two is pictured below. First we can see what happens
in the example given above where we create the chain using lazychain on 
"abc".

![chain](https://user-images.githubusercontent.com/1164439/215340284-4b7b44a7-df32-4b90-b925-f0a395694805.png)

By contrast, we would immediately go to a fully expanded chain if we were to
simply apply chain:

```py
>>> from lazychains import chain
>>> c = chain( "abc" )
>>> c
chain(['a','b','c'])
>>> 
```

![lazychain](https://user-images.githubusercontent.com/1164439/215340294-1667798e-dcad-402e-bccb-e0423f1e8ed9.png)

