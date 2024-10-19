#
# Copyright (c) 2024, Arkadiusz Netczuk <dev.arnet@gmail.com>
# All rights reserved.
#
# This source code is licensed under the BSD 3-Clause license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import logging

import math

from showgraph.graphviz import Graph, get_node_label, unquote_name
from clocdirtree.io import prepare_filesystem_name

# from showgraph.io import prepare_filesystem_name


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

_LOGGER = logging.getLogger(__name__)


def generate_graph(cloc_dict) -> Graph:
    dot_graph = Graph()
    dot_graph.setEngine("neato")
    base_graph = dot_graph.base_graph
    base_graph.set_type("digraph")
    #     base_graph.set_rankdir( 'LR' )

    lines_dict = {}
    for key, val in cloc_dict.items():
        if isinstance(val, tuple):
            lines_dict[key] = val[0]
        else:
            lines_dict[key] = val

    max_val = -1
    for key, val in lines_dict.items():
        max_val = max(max_val, val)
    if max_val < 1:
        return dot_graph

    MAX_SIZE = 8
    width_dict = {}
    for key, val in lines_dict.items():
        #### make circles areas proportional
        ## val / max = PI*r^2 / PI*R^2
        ## val / max = r^2 / R^2
        ## val / max = (2w)^2 / (2W)^2
        ## val / max = 4*w^2 / 4*W^2
        ## val / max = w^2 / W^2
        ## val / max = (w/W)^2
        ## sqrt( val / max ) = w / W
        ## w = sqrt( val / max ) * W
        factor = float(val) / max_val
        new_val = math.sqrt(factor) * MAX_SIZE
        width_dict[key] = new_val

    ## generate main graph
    for name, lines_num in lines_dict.items():
        node = dot_graph.addNode(name, shape="circle")
        node.set("label", f"{name}\n{lines_num}")
        # node  = dot_graph.addNode( f"{name}\n{lines_num}", shape="circle" )
        width = width_dict[name]
        node.set("width", width)
        node.set("fixedsize", "true")
        node.set("color", "gray")

    return dot_graph


def store_graph_to_html(graph: Graph, output_dir):
    if graph.empty():
        ## empty graph -- do not store
        return
    graph_name = graph.getName()
    item_filename = prepare_filesystem_name(graph_name)

    # data_out = os.path.join( output_dir, item_filename + ".gv.txt" )
    # graph.writeRAW( data_out )
    data_out = os.path.join(output_dir, item_filename + ".png")
    graph.writePNG(data_out)
    data_out = os.path.join(output_dir, item_filename + ".map")
    graph.writeMap(data_out)


def set_node_html_attribs(graph, local_dir, filter_nodes=None):
    all_nodes = graph.getNodesAll()
    for node_obj in all_nodes:
        node_name = node_obj.get_name()
        raw_name = unquote_name(node_name)
        if filter_nodes is not None:
            if raw_name not in filter_nodes:
                continue
        node_label = get_node_label(node_obj)
        node_obj.set("tooltip", "node: " + node_label)
        node_filename = prepare_filesystem_name(raw_name)
        node_url = local_dir + node_filename + ".html"
        node_obj.set("href", node_url)


def split_to_multi_dict(data_dict, split_string="/"):
    def add_to_dict(container_dict, key_list, value):
        if not key_list:
            return

        front_key = key_list.pop(0)
        key_data = container_dict.get(front_key)
        if key_data is None:
            key_data = [None, {}]
            container_dict[front_key] = key_data

        if not key_list:
            # bottom
            key_data[0] = value
        else:
            sub_dict = key_data[1]
            add_to_dict(sub_dict, key_list, value)

    ret_dict = {}
    for key, val in data_dict.items():
        key_split = key.split(split_string)
        add_to_dict(ret_dict, key_split, val)
    return ret_dict


def split_to_level_dict(data_dict, split_string="/"):
    ret_dict = {}
    for key, val in data_dict.items():
        key_split = key.split(split_string)
        level = len(key_split)

        level_dict = ret_dict.get(level)
        if level_dict is None:
            level_dict = {}
            ret_dict[level] = level_dict
        level_dict[key] = val
    return ret_dict


def reduce_dict(data_dict):
    path_prefix = os.path.commonprefix(list(data_dict.keys()))
    prefix_len = len(path_prefix)
    if prefix_len > 0:
        data_dict = {key[prefix_len:]: val for key, val in data_dict.items()}
    return data_dict, path_prefix
