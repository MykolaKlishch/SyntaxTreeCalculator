import sys

OPERATORS = {
    '+': float.__add__,
    '-': float.__sub__,
    '*': float.__mul__,
    '/': float.__truediv__,
}


class SyntaxTreeNode:

    def __init__(self, expression: str):
        self.raw_expr = expression.replace(' ', '')
        if not self.raw_expr:
            self.raw_expr = '0'
        self.token = None
        self.children = []

    def _split_near_brackets(self, operator):
        """
        If self.raw_expr starts or ends with brackets, try to split by the
        operator considering these brackets. If self.raw_expr both starts and
        ends with brackets, remove them for further parsing
        """
        split_expr = [self.raw_expr]
        while (
                self.raw_expr.startswith('(')
                and self.raw_expr.endswith(')')
                and self.raw_expr.find('(', 1, -1) <= self.raw_expr.find(')', 1, -1)
        ):
            self.raw_expr = self.raw_expr[1:-1]
        if self.raw_expr.startswith('('):
            split_expr = self.raw_expr.rsplit(')' + operator, maxsplit=1)
            if len(split_expr) == 2:
                split_expr[0] += ')'
        elif self.raw_expr.endswith(')'):
            split_expr = self.raw_expr.split('(' + operator, maxsplit=1)
            if len(split_expr) == 2:
                split_expr[1] += '('
        return split_expr

    @staticmethod
    def _validate_split(left: str, right: str):
        """Ensure that both parts of split expression do not have unpaired brackets"""
        return (
            left.count(')') == left.count('(')
            and right.count(')') == right.count('(')
        )

    def _validate_split_and_parse_children(self, split_expr, operator):
        """
        If the split is valid (see _validate_split method documentation),
        then parse net nodes recursively
        """
        left, right = split_expr
        valid_split = self._validate_split(left, right)
        if valid_split:
            self.token = operator
            self.children = [
                SyntaxTreeNode(left).parse_recursively(),
                SyntaxTreeNode(right).parse_recursively()
            ]
        return valid_split

    def parse_recursively(self):
        """
        Performs parsing of raw expression. Combines
        the functionality of both lexer and parser.
        """
        for operator in OPERATORS:
            split_expr = self._split_near_brackets(operator)
            if len(split_expr) == 1:
                split_expr = self.raw_expr.split(operator, maxsplit=1)
            if len(split_expr) == 2:
                valid_split = self._validate_split_and_parse_children(split_expr, operator)
                if valid_split:
                    break
                elif self.raw_expr.count(operator) > 1:
                    fully_split_expr = self.raw_expr.split(operator, maxsplit=-1)
                    for split_pos in range(1, self.raw_expr.count(operator)):
                        split_expr = [
                            operator.join(fully_split_expr[:split_pos+1]),
                            operator.join(fully_split_expr[split_pos+1:])
                        ]
                        valid_split = self._validate_split_and_parse_children(split_expr, operator)
                        if valid_split:
                            break
        else:
            self.token = self.raw_expr
        return self

    def print_syntax_tree(self, prefix='', index=1, root=True):
        print(f"{prefix}{(' ├──', ' └──', '')[index + root]}[{self.token}]")
        prefix += (' │  ', '    ', '')[index + root]
        for child_index, child in enumerate(self.children):
            child.print_syntax_tree(
                prefix=prefix,
                index=child_index,
                root=False
            )


def calculate_recursively(node: SyntaxTreeNode):
    if not node.children and node.token not in OPERATORS:
        return float(node.token)
    else:
        value_1 = calculate_recursively(node.children[0])
        value_2 = calculate_recursively(node.children[1])
        calc_method = OPERATORS[node.token]
        return calc_method(value_1, value_2)


if __name__ == '__main__':
    expr = sys.argv[1]
    tree = SyntaxTreeNode(expr)
    try:
        tree.parse_recursively()
        print('\nSyntax Tree:')
        tree.print_syntax_tree()
        result = calculate_recursively(tree)
        result = round(result, 15)
        try:
            if result == int(result):
                result = int(result)
        except ValueError:
            pass
        print('\nCalculation Result:')
        print(result)
    except Exception as e:
        print(': '.join(('Invalid expression', str(e))))
