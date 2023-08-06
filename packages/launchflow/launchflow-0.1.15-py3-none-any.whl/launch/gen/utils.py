import ast
import re
from dataclasses import dataclass
from typing import Any, Dict, Tuple, Type


@dataclass
class InspectionResult:
    source: str
    source_args: Dict[str, Tuple[Any, Type]]
    sink: str
    sink_args: Dict[str, Tuple[Any, Type]]

    def get_source(self):
        args = ", ".join([
            f"{k}={v[1].__name__}('{v[0]}')"
            for k, v in self.source_args.items()
        ])
        loc = {}
        code = f'_source = {self.source}({args})'
        exec(code, globals(), loc)
        _source = loc['_source']
        return _source

    def get_sink(self):
        args = ", ".join([
            f"{k}={v[1].__name__}('{v[0]}')"
            for k, v in self.sink_args.items()
        ])
        loc = {}
        exec(f'_sink = {self.sink}({args})', globals(), loc)
        _sink = loc['_sink']
        return _sink


class ObjectCallVisitor(ast.NodeVisitor):

    def __init__(self, method_names, class_name):
        self.method_names = method_names
        self.class_name = class_name
        self.assignments = {}
        self.flow_instances = {}
        self.sink = None
        self.sink_args = {}
        self.source = None
        self.source_args = {}
        self.processor_class_instances = []
        self.subclasses = {}
        self.current_subclass = None

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.assignments[target.id] = node.value
                if isinstance(node.value, ast.Call) and isinstance(
                        node.value.func,
                        ast.Name) and node.value.func.id == self.class_name:
                    self.flow_instances[target.id] = target.id
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        for base in node.bases:
            if (isinstance(base, ast.Attribute)
                    and base.value.id == 'buildflow'
                    and base.attr == 'Processor'):
                self.current_subclass = node.name
                self.subclasses[self.current_subclass] = {}
        self.generic_visit(node)
        self.current_subclass = None

    def visit_FunctionDef(self, node):
        if self.current_subclass and node.name in ['source', 'sink']:
            return_value = self.extract_return_value(node, node.name)
            self.subclasses[self.current_subclass][node.name] = return_value
        self.generic_visit(node)

    def extract_return_value(self, node, node_name: str):
        for subnode in node.body:
            if isinstance(subnode, ast.Return):
                if subnode.value:
                    if isinstance(subnode.value, ast.Call):
                        referenced_val = subnode.value.func.attr
                        # TODO: need to parse out arguments as well.
                        if node_name == 'sink':
                            self.sink = referenced_val
                        else:
                            self.source = referenced_val
                else:
                    return None
        return None

    def visit_Call(self, node):
        if (isinstance(node.func, ast.Attribute)
                and node.func.attr in self.method_names
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in self.flow_instances):
            # TODO: need to handle non keyword args
            for arg in node.keywords:
                if isinstance(arg.value,
                              ast.Name) and arg.value.id in self.assignments:
                    referenced_value = self.assignments[arg.value.id]
                    if isinstance(referenced_value, ast.Call):
                        if isinstance(referenced_value.func, ast.Attribute):
                            referenced_value = referenced_value.func.attr
                        elif isinstance(referenced_value.func, ast.Name):
                            referenced_value = referenced_value.func.id
                elif isinstance(arg.value, ast.Call):
                    if isinstance(arg.value.func, ast.Attribute):
                        referenced_value = arg.value.func.attr
                    elif isinstance(arg.value.func, ast.Name):
                        referenced_value = arg.value.func.id
                    else:
                        referenced_value = ast.dump(arg.value)
                elif isinstance(arg.value, ast.Constant):
                    referenced_value = arg.value.value
                else:
                    referenced_value = ast.dump(arg.value)
                if arg.arg == 'sink':
                    if self.sink:
                        raise Exception("Sink already defined")
                    self.sink = referenced_value
                    self.sink_args[arg.arg] = ast.dump(arg.value)
                elif arg.arg == 'source':
                    if self.source:
                        raise Exception("Source already defined")
                    self.source = referenced_value
                    self.source_args[arg.arg] = ast.dump(arg.value)

                if arg.arg in ['sink', 'source']:
                    arg_dict = (self.sink_args
                                if arg.arg == 'sink' else self.source_args)
                    if isinstance(
                            arg.value,
                            ast.Name) and arg.value.id in self.assignments:
                        value_node = self.assignments[arg.value.id]
                        if isinstance(value_node, ast.Str):
                            arg_value = (value_node.s, str)
                        elif isinstance(value_node, ast.Constant):
                            arg_value = (value_node.value,
                                         type(value_node.value))
                        else:
                            arg_value = (ast.dump(value_node),
                                         type(value_node))
                    else:
                        for keyword in arg.value.keywords:
                            if isinstance(
                                    keyword.value, ast.Name
                            ) and keyword.value.id in self.assignments:
                                value_node = self.assignments[keyword.value.id]
                                if isinstance(value_node, ast.Str):
                                    arg_value = (value_node.s, str)
                                elif isinstance(value_node, ast.Constant):
                                    arg_value = (value_node.value,
                                                 type(value_node.value))
                                else:
                                    arg_value = (ast.dump(value_node),
                                                 type(value_node))
                            elif isinstance(keyword.value, ast.Constant):
                                arg_value = (keyword.value.value,
                                             type(keyword.value.value))
                            else:
                                arg_value = (ast.dump(keyword.value),
                                             type(keyword.value))
                            arg_dict[keyword.arg] = arg_value

            # Remove the unwanted keys from the dictionaries
            self.sink_args.pop('sink', None)
            self.source_args.pop('source', None)
        # elif (isinstance(node.func, ast.Name)
        #         and node.func.attr == 'source'
        #         and isinstance(node.func.value, ast.Name)
        #         and node.func.value.id in self.flow_instances):
        #     pass
        else:
            self.generic_visit(node)

    def get_result(self):
        return InspectionResult(
            source=self.source,
            source_args=self.source_args,
            sink=self.sink,
            sink_args=self.sink_args,
        )


def inspect(file_path: str) -> InspectionResult:
    with open(file_path, 'r') as file:
        code = file.read()
        parsed_code = ast.parse(code)
        visitor = ObjectCallVisitor(['processor'], 'Flow')
        visitor.visit(parsed_code)
        return visitor.get_result()


def replace_class_references(file_path: str, old_class_ref: str,
                             new_class_ref: str, new_class_args: dict) -> str:
    with open(file_path, 'r') as file:
        code = file.read()

    # Define patterns for matching class references with arguments
    old_class_pattern = re.compile(rf"{old_class_ref}\((.*?)\)", re.DOTALL)

    # Prepare class_b arguments string
    new_class_args_str = ', '.join(
        [f"{key}={repr(value)}" for key, value in new_class_args.items()])

    # Replace class_a references with class_b and its arguments
    replaced_code = old_class_pattern.sub(
        f"{new_class_ref}({new_class_args_str})", code)

    return replaced_code


def print_schemas(result: InspectionResult):
    source = result.get_source()
    sink = result.get_sink()

    print('-' * 80)
    print(source)
    print(source.schema())
    print('-' * 80)
    print(sink)
    print(sink.schema())
    print('-' * 80)
