class BaseAnalyzer(object):
    def __init__(self, filename, actual_code):
        pass

    def process(self):
        return {}

    def _count_elements(self, node, types):
        count = 0
        for c in node.children:
            count += self._count_elements(c, types)
        if node.type in types:
            count += 1
        return count

    def _get_max_nested_conditional(self, node):
        return (1 if node.type in self.condition_statements else 0) + max(
            (self._get_max_nested_conditional(x) for x in node.children), default=0
        )

    def _get_complexity_metrics(self, body_node):
        number_conditions = self._count_elements(
            body_node,
            self.condition_statements,
        )
        return {
            "conditions": number_conditions,
            "mccabe_cyclomatic_complexity": number_conditions + 1,
            "returns": self._count_elements(body_node, ["return_statement"]),
            "max_nested_conditional": self._get_max_nested_conditional(body_node),
        }

    def _get_name(self, node):
        name_node = node.child_by_field_name("name")
        actual_name = self.actual_code[
            name_node.start_byte : name_node.end_byte
        ].decode()
        try:
            wrapping_class = next(
                x for x in self._get_parent_chain(node) if x.type in self.wrappers
            )
        except StopIteration:
            wrapping_class = None
        if wrapping_class is not None:
            class_name_node = wrapping_class.child_by_field_name("name")
            class_name = self.actual_code[
                class_name_node.start_byte : class_name_node.end_byte
            ].decode()
            return f"{class_name}::{actual_name}"
        return actual_name

    def _get_parent_chain(self, node):
        cur = node.parent
        while cur:
            yield cur
            cur = cur.parent

    def get_import_lines(self, root_node, imports_query):
        import_lines = set()
        for (a, _) in imports_query.captures(root_node):
            import_lines.add((a.start_point[0] + 1, a.end_point[0] - a.start_point[0]))
        return import_lines
