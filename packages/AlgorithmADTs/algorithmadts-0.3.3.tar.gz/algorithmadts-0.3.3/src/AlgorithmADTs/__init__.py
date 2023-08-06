from AlgorithmADTs.AbstractDataTypes import (
    infinity,
    Array,
    Matrix,
    List,
    Stack,
    Queue,
    PriorityQueue,
    Dictionary,
    Graph,
    WeightedGraph,
)
from AlgorithmADTs.GraphAlgorithms import (
    Prims,
    Dijkstras,
    BellmanFord,
    FloydWarshall,
    FloydWarshallTC,
    PageRank,
)

__all__ = [
    "infinity",
    "Array",
    "Matrix",
    "List",
    "Stack",
    "Queue",
    "PriorityQueue",
    "Dictionary",
    "Graph",
    "WeightedGraph",
    "Prims",
    "Dijkstras",
    "BellmanFord",
    "FloydWarshall",
    "FloydWarshallTC",
    "PageRank",
]

from importlib.metadata import version
__version__ = version("AlgorithmADTs")

def __check_version__():
    print("Checking version...", end='\t')
    import requests 
    import xml.etree.ElementTree as ET
    page = requests.get("https://pypi.org/rss/project/algorithmadts/releases.xml")

    if page.status_code != 200:
        print("Connection error")
        return ValueError()
    
    element_tree = ET.fromstring(page.text)

    channel = element_tree.find('channel')
    try:
        item = channel.find('item') #type: ignore
        version = item.find('title').text # type: ignore

        if version == __version__:
            print("All up to date!")
            return True
        else:
            print(f"There is a new version of AlgorithmADTs available! Try updating to version {version}")
            return False

    except:
        print("Parsing error")
        return ValueError()
