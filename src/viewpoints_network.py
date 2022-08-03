import networkx as nx
from matplotlib import pyplot as plt
import copy


class ViewpointsNetwork:
    def __init__(self, summary_descriptors, director=None):
        self.director = director
        self.g = nx.Graph()
        self.count = 0
        self.gestures = {}
        self.most_central_node = None
        self.highest_degree_node = None
        self.weighted_edges = []
        self.summary_descriptors = summary_descriptors
        self.secondary_node_names = {}

    def add_gesture(self, viewpoints_gesture):
        self.count += 1
        gesture_summary = viewpoints_gesture.get_gesture_summary()
        self.gestures[self.count] = {
            viewpoints_gesture.summary_descriptors[i]: viewpoint_value
            for i, viewpoint_value in enumerate(gesture_summary)
        }

        id = copy.copy(self.count)
        self.g.add_node(id)
        viewpoints = ["tempo", "duration", "shape", "gesture"]
        for i, descriptor in enumerate(viewpoints):
            """
            each node has a secondary node weighted by its viewpoint value
            """
            node_name = f"{descriptor}-{id}"
            self.g.add_node(node_name)
            # self.g[node_name]["weight"] = gesture_summary[i]
            # keep track of it for bookkeeping
            self.secondary_node_names[node_name] = gesture_summary[i]
            # connect to parent node
            self.g.add_edge(id, node_name, label=descriptor, weight=gesture_summary[i])
            nx.set_node_attributes(
                self.g, {node_name: gesture_summary[i]}, name="weight"
            )
        self.compute_edges()

    def compute_edges(self):
        # TODO just taking a rough first stab at this...
        thresholds = {
            "tempo": 0.15,
            # "repetition": 1,
            # "kr": 0.5,
            "duration": 0.05,
            "shape": 0.05,
            "gesture": 0.05,
        }
        if self.count <= 1:
            return
        for i in self.secondary_node_names.keys():
            for j in self.secondary_node_names.keys():
                if (i != j) and (i.split("-")[0] == j.split("-")[0]):
                    node_a = self.g.nodes[i]
                    node_b = self.g.nodes[j]
                    for k, v in thresholds.items():
                        diff = abs(node_a["weight"] - node_b["weight"])
                        viewpoint = i.split("-")[0]
                        if diff < thresholds[viewpoint]:
                            # print("drawing edge", node_a, node_b)
                            self.g.add_edge(i, j, weight=diff, label=viewpoint)
        self.highest_degree_node = sorted(
            self.g.degree, key=lambda x: x[1], reverse=True
        )[0]
        centralities = nx.eigenvector_centrality(self.g)
        k = list(centralities.keys())
        v = list(centralities.values())
        max_centrality = k[v.index(max(v))]
        self.most_central_node = (max_centrality, centralities[max_centrality])
        self.weighted_edges = sorted(
            self.g.edges(data=True), key=lambda x: x[2]["weight"], reverse=True
        )

    def get_weighted_edges(self):
        """
        from the weighted edge list, get the non-self connections between nodes with weights
        returns [(node1, node2,{"label":"gesture", "weight":1.333})]
        """
        edges = []
        if not edges:
            return
        for edge in self.weighted_edges:
            node1 = edge[0]
            node2 = edge[1]
            if type(node1) == str:
                node1 = node1.split("-")[1]
            if type(node2) == str:
                node2 = node2.split("-")[1]
            if node1 == node2:
                # Don't care if it's the same gesture/node
                continue
            else:
                edges.append((node1, node2, edge[2]))
        return edges

    def get_highest_degree_node(self):
        """
        Returns the node with the hightest degree
        (viewpoints index, viewpoint, degree)
        """
        if not self.highest_degree_node:
            return
        node = self.highest_degree_node
        if type(node[0]) == str:
            viewpoints_gesture_index = node[0].split("-")[1]
            viewpoints_gesture_viewpoint = node[0].split("-")[0]
            degree = node[1]
            return (viewpoints_gesture_index, viewpoints_gesture_viewpoint, degree)
        else:
            return (node[0], None, node[1])

    def get_most_central_node(self):
        """
        Returns the latest-computed node with highest eigenvector centrality
        Gives the node, its "viewpoint"
        (viewpoints index, viewpoint, centrality)
        """
        if not self.most_central_node:
            return
        node = self.most_central_node
        if type(node[0]) == str:
            centrality = node[1]
            viewpoints_gesture_index = node[0].split("-")[1]
            viewpoints_gesture_viewpoint = node[0].split("-")[0]
            return (viewpoints_gesture_index, viewpoints_gesture_viewpoint, centrality)
        else:
            return (node[0], None, node[1])

    def clear_network(self):
        plt.clf()

    def draw_network(self):
        options = {
            "node_color": "#A0CBE2",
            "width": 0.5,
            "with_labels": True,
        }
        pos = nx.spring_layout(self.g, seed=63)  # Seed layout for reproducibility
        # Update position for node from each group
        plt.clf()
        plt.title("Viewpoints Gesture Network")
        nx.draw_networkx(self.g, pos, with_labels=True)
        for edge in self.g.edges(data="weight"):
            nx.draw_networkx_edges(self.g, pos, edgelist=[edge], width=(edge[2] / 4))
        # nx.draw(self.g, pos, **options)
        # nx.draw_networkx_nodes(self.g, pos)
        # nx.draw_networkx_edges(self.g, pos, connectionstyle="arc3,rad=0.1")
        plt.show()
