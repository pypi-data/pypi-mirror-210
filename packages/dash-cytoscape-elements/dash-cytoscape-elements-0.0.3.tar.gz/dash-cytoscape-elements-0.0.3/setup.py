# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dash_cytoscape_elements']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.10.4,<2.0.0']

setup_kwargs = {
    'name': 'dash-cytoscape-elements',
    'version': '0.0.3',
    'description': 'Python object for dash-cytoscape elements',
    'long_description': '# dash-cytoscape-elements\n[![test](https://github.com/minefuto/dash-cytoscape-elements/actions/workflows/test.yml/badge.svg)](https://github.com/minefuto/dash-cytoscape-elements/actions/workflows/test.yml)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dash-cytoscape-elements)\n![PyPI](https://img.shields.io/pypi/v/dash-cytoscape-elements)\n![GitHub](https://img.shields.io/github/license/minefuto/dash-cytoscape-elements)\n\nThis is a Python object for [Dash Cytoscape](https://github.com/plotly/dash-cytoscape) Elements.\n\n## Features\n- Add/Remove/Get/Filter Element(Node/Edge) on Python object.\n- Convert Python object from/to Dash Cytoscape format \n- Convert Python object from/to json(Cytoscape.js format)\n\n## Install\n```\npip install dash-cytoscape-elements\n```\n\n## Usage\n### Example1\nCreate Elements object & using on Dash Cytoscape  \n```python\nimport dash\nimport dash_cytoscape as cyto\nfrom dash import html\nfrom dash_cytoscape_elements import Elements\n\ne = Elements()\ne.add(id="one", label="Node 1", x=50, y=50)\ne.add(id="two", label="Node 2", x=200, y=200)\ne.add(source="one", target="two", label="Node 1 to 2")\n\napp = dash.Dash(__name__)\napp.layout = html.Div([\n    cyto.Cytoscape(\n        id=\'cytoscape\',\n        elements=e.to_dash(),\n        layout={\'name\': \'preset\'}\n    )\n])\n\nif __name__ == \'__main__\':\n    app.run_server(debug=True)\n```\n### Example2\nEdit json file of Elements.\n```python\nfrom dash_cytoscape_elements import Elements\n\ne = Elements.from_file("elements.json")\ne.remove(id="node2")\ne.remove(source="node1", target="node2")\n\nwith open("elements.json", mode=\'w\') as f:\n    f.write(e.to_json())\n```\n### Supported Parameters\nThis package supports the following parameters of [Dash Cytoscape](https://github.com/plotly/dash-cytoscape) Element.  \n\n| Parameter | Type | Element |\n| --------- | ---- | ------- |\n| id |  str | Node, Edge |\n| parent | str | Node |\n| source | str | Edge |\n| target | str | Edge |\n| label | str | Node, Edge |\n| source_label | str | Edge |\n| target_label | str | Edge |\n| x | float | Node |\n| y | float | Node |\n| classes | str | Node, Edge |\n| selected | str | Node, Edge |\n| selectable | str | Node, Edge |\n| locked | str | Node, Edge |\n| grabbable | str | Node, Edge |\n| pannable | str | Node, Edge |\n| scratch | dict | Node, Edge |\n\nexample output:\n```python\n>>> e = Elements()\n>>> e.add(id="node1", parent="parent1", label="node_label1", x=1, y=1, classes="class1")\n>>> e.add(source="node1", target="node2", label="edge_label1", source_label="source_label1", target_label="target_label1", classes="class1")\n>>> print(e.to_json())\n[\n    {\n        "group": "nodes",\n        "classes": "class1",\n        "data": {\n            "id": "node1",\n            "parent": "parent1",\n            "label": "node_label1"\n        },\n        "position": {\n            "x": 1.0,\n            "y": 1.0\n        }\n    },\n    {\n        "group": "edges",\n        "classes": "class1",\n        "data": {\n            "id": "49082bcd-dcbb-4db7-b369-29e3bf8f74e2",\n            "source": "node1",\n            "target": "node2",\n            "label": "edge_label1",\n            "source-label": "source_label1",\n            "target-label": "target_label1"\n        }\n    }\n]\n```\nHow to add your own parameters:\n```python\nfrom typing import List, Set\nfrom dash_cytoscape_elements import GenericElements\nfrom dash_cytoscape_elements.element import Edge, EdgeData, Node, NodeData\n\n\nclass CustomNodeData(NodeData):\n    custom_str1: str = ""\n\nclass CustomNode(Node):\n    data: CustomNodeData = CustomNodeData()\n    custom_str2: str = ""\n    custom_list: List[str] = []\n\nclass CustomEdgeData(EdgeData):\n    custom_str1: str = ""\n\nclass CustomEdge(Edge):\n    data: CustomEdgeData = CustomEdgeData()\n    custom_str2: str = ""\n    custom_set: Set[str] = set()\n\ne = GenericElements[CustomNode, CustomEdge]()\ne.add(id="node1", custom_str1="str1", custom_str2="str2", custom_list=["list1", "list2"])\ne.add(id="edge1", source="node1", target="node2", custom_str1="str1", custom_str2="str2", custom_set={"set1", "set2"})\n\nprint(e.to_json())\n# [\n#     {\n#         "group": "nodes",\n#         "data": {\n#             "id": "node1",\n#             "custom_str1": "str1"\n#         },\n#         "custom_str2": "str2",\n#         "custom_list": [\n#             "list1",\n#             "list2"\n#         ]\n#     },\n#     {\n#         "group": "edges",\n#         "data": {\n#             "id": "edge1",\n#             "source": "node1",\n#             "target": "node2",\n#             "custom_str1": "str1"\n#         },\n#         "custom_str2": "str2",\n#         "custom_set": [\n#             "set1",\n#             "set2"\n#         ]\n#     }\n# ]\n```\n\nPlease see the [Documentation](https://minefuto.github.io/dash-cytoscape-elements/) for details.\n',
    'author': 'minefuto',
    'author_email': 'minefuto@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minefuto/dash-cytoscape-elements',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
