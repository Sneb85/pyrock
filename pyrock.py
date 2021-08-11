from TM1py import TM1Service
from mdxpy import MdxBuilder, Member, MdxHierarchySet


def cube_view_create_mdx_statement(
        tm1: TM1Service,
        cube_name: str,
        cube_filter: str,
        dimension_delimiter: str = '&',
        hierarchy_delimiter: str = '|',
        element_delimiter: str = '+',
        element_start_delimiter: str = ':') -> str:
    """ Returns MDX statement for cube view based on bedrock filter string
    """

    # convert filter string into dictionary
    filter_dictionary = {}
    for part in cube_filter.split(dimension_delimiter):
        if not part:
            continue

        dimension_part = part.split(element_start_delimiter)[0]
        hierarchy_delimiter_position = dimension_part.find(hierarchy_delimiter)
        if hierarchy_delimiter_position < 0:
            dimension_name = hierarchy_name = dimension_part
        else:
            dimension_name, hierarchy_name = dimension_part.split(hierarchy_delimiter)

        dimension_filter_dictionary = {"Hierarchy": hierarchy_name}
        elements_part = part.split(element_start_delimiter)[1]
        element_delimiter_pos = elements_part.find(element_delimiter)
        element_names = []
        if element_delimiter_pos > 0:
            element_names.extend(elements_part.split(element_delimiter))

        else:
            element_names.append(elements_part)
        dimension_filter_dictionary["Elements"] = element_names
        filter_dictionary[dimension_name] = dimension_filter_dictionary

    # Build MDX statement
    query = MdxBuilder.from_cube(cube=cube_name)
    for dimension_name in filter_dictionary:
        filter_dim_body = filter_dictionary[dimension_name]
        hierarchy_name = filter_dim_body["Hierarchy"]
        element_names = filter_dim_body["Elements"]

        mdx_hierarchy_sets = []
        for element in element_names:
            # ToDo: should filter by level 0 perhaps be optional?
            mdx_set = MdxHierarchySet.descendants(Member.of(dimension_name, hierarchy_name, element)).filter_by_level(0)
            mdx_hierarchy_sets.append(mdx_set)

        hierarchy_set: MdxHierarchySet = mdx_hierarchy_sets[0]
        for element_set in mdx_hierarchy_sets[1:]:
            hierarchy_set = hierarchy_set.union(element_set)

        query = query.add_hierarchy_set_to_column_axis(hierarchy_set)

    # Build MDX for remainder of the dimensions
    cube_dimensions = tm1.cubes.get_dimension_names(cube_name=cube_name)
    for dimension in cube_dimensions:

        if dimension in filter_dictionary:
            continue

        mdx_set = MdxHierarchySet.all_leaves(dimension)
        query = query.add_hierarchy_set_to_column_axis(mdx_hierarchy_set=mdx_set)

    query.columns_non_empty()
    return query.to_mdx()
