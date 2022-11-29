import io
from itertools import zip_longest

try:
    from IPython.display import SVG
except ImportError:
    SVG = None

try:
    import pygraphviz as viz
except ImportError:
    viz = None


def make_graph(datatree, fontname="Arial", fontsize=12):
    if viz is None:
        raise ModuleNotFoundError("pygraphviz is not installed")

    small = f"{fontsize * .7:.1f}"
    g = viz.AGraph(rankdir="LR", strict=False, fontname=fontname, fontsize=fontsize)

    g_nodes = {}
    if len(datatree._graph.nodes):
        if datatree.root_node_name:
            g_nodes[datatree.root_node_name] = {
                "dims": list(datatree.subspaces[datatree.root_node_name].dims),
                "vars": set(),
            }
        for k in datatree._graph.nodes:
            if k == datatree.root_node_name:
                continue
            g_nodes[k] = {
                "dims": list(datatree.subspaces[k].dims),
                "vars": set(),
            }
    for e in datatree._graph.edges:
        rel = datatree._get_relationship(e)
        # print(f"- {rel!r}")
        g_nodes[rel.parent_data]["vars"].add(rel.parent_name)

    def node_label_simple(k, v):
        dim_names = [f"<dim{i}>{i}" for i in v["dims"]]
        dim_defs = "|".join(dim_names)
        var_names = [f"<var{i}>{i}" for i in v["vars"]]
        var_defs = "|".join(var_names)
        out = f"<f0>{k}|{{{{Dimensions|{dim_defs}}}||{{Variables|{var_defs}}}}}"
        # print(out)
        return out

    def node_label(k, v):
        cells = []
        if len(v["dims"]) > 0 and len(v["vars"]) > 0:
            cells.append(
                f"""
            <TR>
            <TD SIDES="L"><FONT COLOR="#999999" POINT-SIZE="{small}">DIMENSIONS</FONT></TD>
            <TD SIDES="R"><FONT COLOR="#999999" POINT-SIZE="{small}">VARIABLES</FONT></TD>
            </TR>
            """
            )
            for _d, _v in zip_longest(v["dims"], v["vars"], fillvalue=""):
                if _d == "":
                    cells.append(
                        f"""
                    <TR>
                    <TD BORDER="0"></TD>
                    <TD PORT="var{_v}" BGCOLOR="gray95">{_v}</TD>
                    </TR>
                    """
                    )
                elif _v == "":
                    cells.append(
                        f"""
                    <TR>
                    <TD PORT="dim{_d}" BGCOLOR="gray95">{_d}</TD>
                    <TD BORDER="0"></TD>
                    </TR>
                    """
                    )
                else:
                    cells.append(
                        f"""
                    <TR>
                    <TD PORT="dim{_d}" BGCOLOR="gray95">{_d}</TD>
                    <TD PORT="var{_v}" BGCOLOR="gray95">{_v}</TD>
                    </TR>
                    """
                    )
        elif len(v["dims"]) > 0 and len(v["vars"]) == 0:
            cells.append(
                f"""
            <TR>
            <TD SIDES="LR"><FONT COLOR="#999999" POINT-SIZE="{small}">DIMENSIONS</FONT></TD>
            </TR>
            """
            )
            for _d in v["dims"]:
                cells.append(
                    f"""
                <TR>
                <TD PORT="dim{_d}" BGCOLOR="gray95">{_d}</TD>
                </TR>
                """
                )

        # dim_names = [f"""<TR><TD PORT="dim{i}">{i}</TD></TR>""" for i in v['dims']]
        # dim_defs = "".join(dim_names)
        # # if dim_defs:
        # #     dim_defs = f"<TABLE>{dim_defs}</TABLE>"
        # var_names = [f"""<TR><TD PORT="var{i}">{i}</TD></TR>""" for i in v['vars']]
        # var_defs = "".join(var_names)
        # # if var_defs:
        # #     var_defs = f"<TABLE>{var_defs}</TABLE>"
        out = f"""< <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" >
        <TR><TD PORT="f0" COLSPAN="2" BGCOLOR="gray80"><B>{k}</B></TD></TR>
        {''.join(cells)}
        </TABLE> >"""
        # print(out)
        return out

    if len(datatree._graph.nodes):
        for k, v in g_nodes.items():
            g.add_node(
                k,
                # label=f'<<B>{k}</B> |{dim_defs}>',
                label=node_label(k, v),
                shape="plaintext",
                fontname=fontname,
                fontsize=fontsize,
            )

    for e in datatree._graph.edges:
        rel = datatree._get_relationship(e)
        # print(f"- {rel!r}")
        # print(f"dim{rel.child_name}")
        g.add_edge(
            rel.parent_data,
            rel.child_data,
            key=repr(rel),
            tailport=f"var{rel.parent_name}",
            headport=f"dim{rel.child_name}",
            dir="forward",
            arrowhead="odiamond" if rel.indexing == "label" else "normal",
        )

    return g


def display_svg(graph):
    """
    Render a pygraphviz AGraph as SVG.

    Parameters
    ----------
    graph : pygraphviz.agraph.AGraph

    Returns
    -------
    IPython.core.display.SVG
    """
    pyg_imgdata = io.BytesIO()
    graph.draw(pyg_imgdata, format="svg", prog="dot")
    return SVG(pyg_imgdata.getvalue())
