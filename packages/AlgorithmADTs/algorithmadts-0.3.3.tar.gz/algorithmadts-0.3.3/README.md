# Algorithm Abstract Data Types
Finlay's package for Abstract Data Types written for Algorithmics class

## Installation
Run the following command in your terminal: 
`pip install AlgorithmADTs --force-reinstall`

AlgorithmADTs can now be imported into your python scripts! 

I recommend `from AlgorithmADTs import *` to include all functionality, but you can also import from `AlgorithmADTs.AbstractDataTypes` or `AlgorithmADTs.GraphAlgorithms` 

## ADTS:
```
Array
    create: Integer -> Array
    set: Array x Integer x Element -> Array
    get: Array x Integer -> Element

```

```
List 
    create: None -> List
    is_empty: Array -> Boolean
    set: Array x Integer x Element -> List
    get: Array x Integer -> Element
    append: Array x Element -> List
```
```
Stack
    create: None -> Stack
    push: Stack x Element -> Stack
    pop: Stack -> Stack
    is_empty: Stack -> Boolean
    head: Stack -> Element
```
```
Queue
    create: None -> Queue
    enqueue: Queue x Element -> Queue
    dequeue: Queue -> Queue
    is_empty: Queue -> Boolean
    head: Queue -> Element
```
```
PriorityQueue
    create: None -> Priority Queue
    enqueue: Priority Queue x Element x Integer -> Priority Queue
    dequeue: Priority Queue -> Priority Queue
    is_empty: Priority Queue -> Boolean
    head: Priority Queue -> Element
```
```
Dictionary
    create: None -> Dictionary 
    get: Dictionary x Element -> Element
    set: Dictionary x Element x Element -> Dictionary 
    add: Dictionary x Element x Element -> Dictionary
    remove: Dictionary x Element -> Dictionary 
    has_key: Dictionary x Element -> Boolean
    is_empty: Dictionary -> Boolean
```
```
Graph
    create: None -> Graph
    add_node: Graph x Element -> Graph
    add_edge: Graph x Element x Element -> Graph
    adjacent: Graph x Element x Element -> Boolean
    neighbours: Graph x Element -> List
```
Multiple nodes and edges can now be added at one time with `add_nodes` and `add_edges`, using an iterable
```
WeightedGraph (inherits from Graph)
    create: None -> Graph
    add_node: Graph x Element -> Graph
    add_edge: Graph x Element x Element -> Graph
    adjacent: Graph x Element x Element -> Boolean
    neighbours: Graph x Element -> List
    get_weight: Graph x Element x Element -> integer
```


Note that there is no restriction in these classes that elements be hashable, unlike some Python data types
e.g. a Python `dict` requires keys to be hashable.

It also defines a variable `infinity`, set equal to `float('inf')`

The following magic methods are supported:
- `__getitem__` and `__setitem__` for classes with a 'get' and 'set' function.
    This allows you to call `instance[key]` and `instance[key] = value`.
- `__iter__` for Array and List, which operates as expected. Dictionary iter returns an iterable of keys.
    This enables iterating through a class like `for elem in instance`
- `__str__` and `__repr__` are defined for all classes except graphs and allow for classes to be easily viewed through printing
    Note that only the head element is visible for a stack or queue, so it is the only information that can be returned by these methods
- Numerical magic methods (e.g. `__add__`) are defined for matrices
- `__len__` is defined for Array, List and Dictionary 

## Graph Algorithms
Currently, the following graph algorithms are defined:
- Prim's algorithm for computing the Minimal Spanning Tree of a weighted, undirected graph
- Dijkstra's algorithm for finding the single source shortest path in a weighted graph 
- The Bellman-Ford algorithm which extends the functionality of Dijkstra's algorithm to allow for negative weights
- The two variants of the Floyd-Warshall algorithm to calculate shortest path between all nodes and transitive closure of an unweighted graph
- The PageRank algorithm for determining the relative importance of nodes in an unweighted graph

## Version things 
To implement:
- ALLOW `List([1,3,34])` rather than having to stupidly define every value separately.
- Allow default value for Arrays
- Optional hashing for graphs?
- Search methods like DPS BFS
- LEn of dict