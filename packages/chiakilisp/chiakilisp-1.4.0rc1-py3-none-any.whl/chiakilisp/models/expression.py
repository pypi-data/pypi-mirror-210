# pylint: disable=fixme
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-locals
# pylint: disable=arguments-renamed
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements

import importlib
from copy import deepcopy
from typing import List, Any, Callable
from chiakilisp.models.token import Token
import chiakilisp.spec as s
from chiakilisp.spec import rules
from chiakilisp.models.literal import\
    Literal, NotFound, Nil
from chiakilisp.models.forward import\
    ExpressionType, CommonType
from chiakilisp.utils import get_assertion_closure, pairs


class ArityError(SyntaxError):

    """Stub class to display that there is an arity error"""


NE_ASSERT = get_assertion_closure(NameError)  # <--------- raises NameError
TE_ASSERT = get_assertion_closure(TypeError)  # <--------- raises TypeError
SE_ASSERT = get_assertion_closure(SyntaxError)  # <----- raises SyntaxError
RE_ASSERT = get_assertion_closure(RuntimeError)  # <--- raises RuntimeError


def IDENTIFIER_ASSERT(lit: Literal, message: str) -> None:

    """Handy shortcut to make assertion that Literal is Identifier"""

    SE_ASSERT(lit.token().position(), lit.token().is_identifier(), message)


def TAIL_IS_VALID(tail: list, rule: str, where: tuple, m_tmpl: str) -> int:

    """
    Validates tail with a certain rule, throws SyntaxError or returns arity
    """

    valid, arity, why = rules.get(rule).valid(tail)
    SE_ASSERT(where, valid, m_tmpl.format(why=why))
    return arity


class Expression(ExpressionType):

    """
    Expression is the class that indented to be used to calculate something
    """

    _nodes: list
    _is_inline_fn: bool = False

    def __init__(self, nodes: list, **props) -> None:

        """Initialize Expression instance"""

        self._nodes = nodes
        self._is_inline_fn = props.get('is_inline_fn', False)

    def nodes(self) -> list:

        """Returns expression nodes"""

        return self._nodes

    def dump(self, indent: int) -> None:

        """Dumps an entire expression with all its nodes"""

        # There is no need to annotate types, or assert() them

        nodes = self.nodes()
        if nodes:
            first, *rest = nodes
            first.dump(indent)
            for argument in rest:
                argument.dump(indent + 1)   # increment indent

    @staticmethod
    def _is_identifier_matching(
            node: CommonType, name: str) -> bool:

        """Returns true it the given node is
        an Identifier and its value matches the {name}"""

        return (isinstance(node, Literal)
                and node.token().type() == Token.Identifier
                and node.token().value() == name)

    def _assert_even_number_of_dict_literals(self) -> None:

        """Asserts that there is an even number of dict literals"""

        if (self.nodes()
                and isinstance(self.nodes()[0], Literal)
                and self.nodes()[0].token().type() == Token.Identifier
                and self.nodes()[0].token().value() == 'dicty'):
            is_even = len(self.nodes()[1:]) % 2 == 0
            position = self.nodes()[0].token().position()
            SE_ASSERT(position, is_even, 'Dictionary key literal must be followed by a value')

    @staticmethod
    def _parse_function_and_create_a_handle(  # pylint: disable=too-many-arguments
            domain_: str, where: tuple, environ: dict, name: str, parameters: 'Expression', body: list):

        """
        Takes necessary parameters like position in the source code and current environment
        And also takes function name, its parameters and the body, parses them and returns a function handle
        """

        names = []
        nodes = parameters.nodes()

        ampersand_found = tuple(filter(lambda p: p[1].token().value() == '&', enumerate(nodes)))  # find the &
        ampersand_position: int = ampersand_found[0][0] if ampersand_found else -1  # exact ampersand position
        positional_parameters = nodes[:ampersand_position] if ampersand_found else nodes
        positional_parameters_length = len(positional_parameters)  # build a list of the positional parameters

        for parameter in positional_parameters:
            parameter: Literal
            names.append(parameter.token().value())  # build a list of the function positional parameter names
        can_take_extras = False      # by default function can't take extra arguments (no ampersand was found)

        if ampersand_found:
            can_take_extras = True   # however, if we found ampersand, validate signature, then alter the flag
            SE_ASSERT(where,
                      len(nodes) - 1 != ampersand_position,
                      f'Expression[execute]: {domain_}: can only mention one alias for extra arguments tuple')
            SE_ASSERT(where,
                      len(nodes) - 2 == ampersand_position,
                      f'Expression[execute]: {domain_}: have to mention alias name for extra arguments tuple')
            names.append(nodes[-1].token().value())  # when signature is valid, remember extra arguments alias

        if not body:
            body = [Nil]  # if there is no function body, let the function to just return a simple nil literal

        integrity_spec_rule = s.Rule(s.Arity(s.AtLeast(positional_parameters_length)
                                             if can_take_extras else s.Exactly(positional_parameters_length)))

        def handle(*c_arguments, **kwargs):

            """User-function handle object"""

            fn_valid, _, fn_why = integrity_spec_rule.valid(c_arguments)  # first, validate function integrity
            SE_ASSERT(where, fn_valid,                                                    f'{name}: {fn_why}')

            if can_take_extras:
                if len(c_arguments) > positional_parameters_length:
                    e_arguments = c_arguments[positional_parameters_length:]
                    c_arguments = c_arguments[:positional_parameters_length] + (e_arguments,)  # new args list
                else:
                    c_arguments = c_arguments + (tuple(),)  # <- if extras are possible but missing, set to ()

            fn = {}  # <----------------------------------------------- initialize new computation environment
            fn.update(environ)  # <--------------------------------------------- update it with the global one
            fn.update(dict(zip(names, c_arguments)))  # <-------------- associate parameters with their values
            fn.update({'kwargs': kwargs})  # <---------------------- update environment with keyword arguments
            return [node.execute(fn, False) for node in body][-1]  # then return the last _computation_ result

        return handle  # <-------- return the closure that will be a good handle for the user defined function

    def execute(self, environ: dict, top: bool = True) -> Any:

        """Execute here - is to return Python 3 value related to the expression: string, number, and vice versa"""

        head: Literal

        assert self.nodes(),              'Expression[execute]: current expression is empty, unable to execute it'

        get = environ.get('get')  # <------- some features like destructing or keyword-as-fn will require core/get
        first = environ.get('first')  # <----- some feature like inline function or others will require core/first

        head, *tail = self.nodes()

        where = head.token().position()  # <------------ when make assertions on expression head, this can be used

        if head.token().type() == Token.Keyword:
            RE_ASSERT(where, get,   "Expression[execute]: unable to use keyword as a function without `core/get`")
            SE_ASSERT(where, len(tail) >= 1,  'Expression[execute]: keyword must be followed by at least one arg')
            SE_ASSERT(where, len(tail) <= 2,   'Expression[execute]: keyword can be followed by at most two args')
            collection, default = tail if len(tail) == 2 else (tail[0], Nil)  # <--- define collection and default
            return get(
                collection.execute(environ, False), head.execute(environ, False), default.execute(environ, False))

        if self._is_inline_fn:  # <--- if this expression is actually an inline function: i.e.: #(prn "Hello," %1)

            RE_ASSERT(where, first,     'Expression[execute]: unable to use inline function without `core/first`')

            def handler(*args, **kwargs):   # <---------------------- then construct an anonymous function handler

                ifn = {}  # <----------------------------------------- start with an empty computation environment
                ifn.update(environ)  # <-------------------------------------------- update it with the global one
                ifn.update({'%': first(args)})  # <-------------------------- make an alias for the first argument
                ifn.update({'kwargs': kwargs})  # <----------------------- make an alias for the keyword arguments
                # env.update({'%&': ...})  # TODO: implement %& parameter, probably, requires body functon parsing
                ifn.update({f'%{argument_index +1}': args[argument_index] for argument_index in range(len(args))})

                return [every_body_node.execute(ifn, False) for every_body_node in [Expression(self.nodes())]][-1]

            handler.x__custom_name__x = '<anonymous function>'  # <------- give an anonymous function its own name
            return handler  # <------------------------------------------------------------ and return its handler

        assert isinstance(head, Literal),        'Expression[execute]: head of the expression should be a Literal'
        IDENTIFIER_ASSERT(head,             'Expression[execute]: head of the expression should be an Identifier')

        if head.token().value() == 'do':
            result = None  # first, assign the result as nil, if block is empty, we just return nil, and it's safe
            for node in tail:
                result = node.execute(environ, False)  # each time we execute() the next node, replace last result
            return result  # <------------------------ when we have no more nodes to execute... return last result

        if head.token().value() == 'or':
            if not tail:
                return None  # <-------------------------- if there are no arguments given to the form, return nil
            result = None  # <----------------------------------------------- set result to the null pointer first
            for cond in tail:  # <-------------------------------------------- for each condition in the arguments
                result = cond.execute(environ, False)  # <------------------------------------- compute the result
                if result:
                    return result  # <------------------------------------ and if there is truthy value, return it
            return result  # <------- if all conditions have been evaluated to falsy ones, return the last of them

        if head.token().value() == 'and':
            if not tail:
                return True  # <------------------------- if there are no arguments given to the form, return true
            result = None  # <----------------------------------------------- set result to the null pointer first
            for cond in tail:  # <-------------------------------------------- for each condition in the arguments
                result = cond.execute(environ, False)  # <------------------------------------- compute the result
                if not result:
                    return result  # <------------------------------------- and if there is falsy value, return it
            return result  # <------ if all conditions have been evaluated to truthy ones, return the last of them

        if head.token().value() == 'try':
            TAIL_IS_VALID(tail, 'try', where,                                   'Expression[execute]: try: {why}')
            main: CommonType = tail[0]  # <------------------ assign main block or literal as a type of CommonType
            catch: Expression = tail[1]  # <--------------------------- assign catch block as a type of Expression
            TAIL_IS_VALID(catch.nodes(), 'catch', where,                      'Expression[execute]: catch: {why}')
            klass: Literal = catch.nodes()[1]  # <---------------------- assign klass literal as a type of Literal
            alias: Literal = catch.nodes()[2]  # <---------------------- assign alias literal as a type of Literal
            block: List[CommonType] = catch.nodes()[3:]  # <---------------- assign block as a list of CommonTypes
            obj = klass.execute(environ, False)  # <------------------------------ get the actual exception object
            closure = {}  # <----------------------------------------------------- init a new try-form environment
            closure.update(environ)  # <-------------------------------------------- update it with the global one
            try:
                return main.execute(environ, False)  # <-------------------------------- try to execute main block
            except obj as exception:  # <------------------------------------------ if exception has been occurred
                closure[alias.token().value()] = exception  # <-- associate exception instance with a chosen alias
                return [expr.execute(closure, False) for expr in block][-1]  # <- return exception handling result

        if head.token().value() == '->':
            if not tail:
                return None  # <------------------------------------------------- if there are no tail, return nil

            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            tail = deepcopy(tail)  # <--------- it could be slow when tail if really complex nested data structure

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Literal):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].nodes().insert(1, target)  # <---- in case of first-threading-macro, insert as the 1st arg
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value() == '->>':
            if not tail:
                return None  # <------------------------------------------------- if there are no tail, return nil

            if len(tail) == 1:
                return tail[-1].execute(environ, False)  # <------------ if there is only one argument, execute it

            tail = deepcopy(tail)  # <--------- it could be slow when tail if really complex nested data structure

            target, *rest = tail  # <------- split tail for the first time to initialize target and rest variables
            while len(tail) > 1:  # <-- do not leave the loop while there is at least one element left in the tail
                _ = rest[0]
                if isinstance(_, Literal):
                    rest[0] = Expression([_])  # <-------- each argument except first should be cast to Expression
                rest[0].nodes().append(target)  # <---- in case of last-threading-macro, append to the end of args
                tail = [rest[0]] + rest[1:]  # <- override tail: modified expression and the tail rest with offset
                target, *rest = tail  # <--------------------------- do the same we did before entering while-loop

            return target.execute(environ, False)  # <----- at the end, return target' expression execution result

        if head.token().value().startswith('.') and not head.token().value() == '...':   # it could be an Ellipsis
            SE_ASSERT(where,
                      len(head.token().value()) > 1,    'Expression[execute]: dot-form: method name is mandatory')
            TAIL_IS_VALID(tail,                         'dot-form', where, 'Expression[execute]: dot-form: {why}')
            handle_name: Literal  # <------------------------------------- assign handle name as a type of Literal
            handle_name, *method_args = tail  # <------------------------ parse dot-form handle name and arguments
            method_name = head.token().value()[1:]  # <------------------ parse handle name from the first literal
            handle_instance = handle_name.execute(environ, False)  # <--- get the handle instance from environment
            SE_ASSERT(where,
                      hasattr(handle_instance, '__class__'),
                      'Expression[execute]: dot-form: use object/method, module/method to invoke a static method')
            handle_alias = handle_instance.__class__.__name__  # <------------- get the actual instance class name
            handle_method: Callable = getattr(handle_instance, method_name, NotFound)  # <-- get the method handle
            NE_ASSERT(where,
                      handle_method is not NotFound,
                      f"Expression[execute]: dot-form: the '{handle_alias}' object has no method '{method_name}'")
            return handle_method(*(node.execute(environ, False) for node in method_args))  # <- return last result

        if head.token().value() == 'if':
            arity = TAIL_IS_VALID(tail, 'if', where,                             'Expression[execute]: if: {why}')
            cond, true, false = (tail if arity == 3 else tail + [Nil])  # <-- tolerate missing false-branch for if
            return true.execute(environ, False) if cond.execute(environ, False) else false.execute(environ, False)

        if head.token().value() == 'when':
            TAIL_IS_VALID(tail, 'when', where,                                 'Expression[execute]: when: {why}')
            cond, *extras = tail  # <-------------------------- false branch is always equals to nil for when-form
            return [true.execute(environ, False) for true in extras][-1] if cond.execute(environ, False) else None

        if head.token().value() == 'cond':
            if not tail:
                return None  # <------------------------------------------ if nothing has been passed, return None
            TAIL_IS_VALID(tail, 'cond', where,                                 'Expression[execute]: cond: {why}')
            for cond, expr in pairs(tail):
                if cond.execute(environ, False):
                    return expr.execute(environ, False)
            return None  # <------------------------------------------------------ if nothing is true, return None

        if head.token().value() == 'let':
            TAIL_IS_VALID(tail, 'let', where,                                   'Expression[execute]: let: {why}')
            bindings, *body = tail  # <------------------------------------------ parse let form bindings and body
            let = {}  # <---------------------------------------------------------- initialize a local environment
            let.update(environ)  # <------------------------------------------------ update it with the global one
            for raw, value in pairs(bindings.nodes()):  # <-------------------------------- for the each next pair

                computed_right_hand_side = value.execute(let, False)  # <------- compute the right-hand-side value

                if isinstance(raw, Expression):  # <--------------------- if the left-hand-side seems to be a coll
                    RE_ASSERT(where, get,  "Expression[execute]: let: destructuring requires `core/get` function")

                    get_by_idx = True
                    skip_first = False
                    if (raw.nodes() and
                            self._is_identifier_matching(raw.nodes()[0], 'dicty')):  # <- dictionary destructuring
                        skip_first = True
                        get_by_idx = False

                    for idx, k_alias in enumerate(map(lambda v: v.token().value(),
                                                      raw.nodes()[1:] if skip_first else raw.nodes())):
                        let.update({k_alias: get(computed_right_hand_side, idx if get_by_idx else k_alias, None)})

                else:  # <---------------------------------------- if the left-hand-side seems to be an identifier
                    let.update({raw.token().value(): computed_right_hand_side})  # <- directly assign computed rhs

            if not body:
                body = [Nil]  # <---------- if there is no 'let' block body, let's just return a simple nil literal

            return [node.execute(let, False) for node in body][-1]  # <---------------------- return computed value

        if head.token().value() == 'fn':
            TAIL_IS_VALID(tail, 'fn', where,                                     'Expression[execute]: fn: {why}')
            parameters, *body = tail  # <---------------------------- parse anonymous function parameters and body

            handle = self._parse_function_and_create_a_handle(
                'fn', where, environ, '<anonymous function>', parameters, body  # let the shortcut do all the work
            )

            handle.x__custom_name__x = '<anonymous function>'  # set the function name to the <anonymous function>
            return handle  # <-------------------------------------------------- return the function handle object

        if head.token().value() == 'def':
            SE_ASSERT(where, top,   'Expression[execute]: def: can only use (def) form at the top of the program')
            TAIL_IS_VALID(tail, 'def', where,                                   'Expression[execute]: def: {why}')
            name: Literal  # <--------------------------------------------------- assign name as a type of Literal
            name, value = tail  # <-------------------------------------------------- assign value as a CommonType
            computed = value.execute(environ, False)  # <-------------------------------- store the computed value
            environ.update({name.token().value(): computed})  # <------------------- assign it to its binding name
            return computed   # <----------------------------------------------------------- return computed value

        if head.token().value() == 'def?':
            SE_ASSERT(where, top, 'Expression[execute]: def?: can only use (def?) form at the top of the program')
            TAIL_IS_VALID(tail, 'def?', where,                                 'Expression[execute]: def?: {why}')
            name: Literal  # <--------------------------------------------------- assign name as a type of Literal
            name, value = tail  # <-------------------------------------------------- assign value as a CommonType
            from_env = environ.get(name.token().value()) if (name.token().value() in environ.keys()) else NotFound
            computed = value.execute(environ, False) if from_env is NotFound else from_env  # try to find existing
            environ.update({name.token().value(): computed})  # assign existing/computed value to its binding name
            return computed   # <----------------------------------------------------------- return computed value

        if head.token().value() == 'defn':
            SE_ASSERT(where, top, 'Expression[execute]: defn: can only use (defn) form at the top of the program')
            TAIL_IS_VALID(tail, 'defn', where,                                 'Expression[execute]: defn: {why}')
            name, parameters, *body = tail  # <-------------------- parse named function name, parameters and body

            handle = self._parse_function_and_create_a_handle(
                'defn', where, environ, name.token().value(), parameters, body  # let the shortcut do all the work
            )

            handle.x__custom_name__x = name.token().value()  # set the function name to whatever a user decided to
            environ.update({name.token().value(): handle})   # update environment to access defined function later
            return handle  # <-------------------------------------------------- return the function handle object

        if head.token().value() == 'defn?':
            SE_ASSERT(where, top, 'Expression[execute]: defn?: can only use defn? form at the top of the program')
            TAIL_IS_VALID(tail, 'defn?', where,                               'Expression[execute]: defn?: {why}')
            name, parameters, *body = tail  # <-------------------- parse named function name, parameters and body

            if environ.get(name.token().value()):   # if there is a function with exact same name already exists...
                return environ.get(name.token().value())  # ...then just grab its handle from the env and return it

            handle = self._parse_function_and_create_a_handle(
                'defn', where, environ, name.token().value(), parameters, body  # let the shortcut do all the work
            )

            handle.x__custom_name__x = name.token().value()  # set the function name to whatever a user decided to
            environ.update({name.token().value(): handle})   # update environment to access defined function later
            return handle  # <-------------------------------------------------- return the function handle object

        if head.token().value() == 'for':
            TAIL_IS_VALID(tail, 'for', where,                                   'Expression[execute]: for: {why}')
            RE_ASSERT(where, get,               'Expression[execute]: for: for-loop requires `core/get` function')
            bindings, body = tail  # <------------------------------------------- parse for-loop bindings and body
            env: dict = {}  # <--(for some reason this type hint is necessary)----- initialize a local environment
            env.update(environ)  # <------------------------------------------------ update it with the global one
            max_length = 0  # <- as we go through all given collections, we need to define maximum number of steps
            gathered_binding_aliases = []  # <- as go through all the coll element aliases, we need to gather them
            for alias, collection in pairs(bindings.nodes()):  # for each next coll element alias and collection..
                computed_collection = collection.execute(environ, False)  # we first compute collection from input
                computed_collection_length = len(computed_collection)  # then store its length to compare bellow |
                max_length = computed_collection_length if computed_collection_length > max_length else max_length
                gathered_binding_aliases.append(alias.token().value())  # and then we append the alias to the list
                env.update({f'$_{alias.token().value()}': collection.execute(environ, False)})  # should be hidden
            for element_idx in range(max_length):  # for each next index (remember we computed maximum length) ...
                current_collection_element_temporary_env = {}  # create a current collection temporary environment
                current_collection_element_temporary_env.update(env)  # <------------ update it with the local one
                for alias in gathered_binding_aliases:  # for each next alias (remember we have a hidden variable)
                    current_collection = env.get(f'$_{alias}')  # get computed collection via that hidden variable
                    current_collection_element_temporary_env.update({alias: get(current_collection, element_idx)})
                body.execute(current_collection_element_temporary_env, False)  # <------- and finally compute body
            return None  # <--------------------- behave as imperative loop where there is no return value but nil

        if head.token().value() == 'while':
            TAIL_IS_VALID(tail, 'while', where,                               'Expression[execute]: while: {why}')
            condition, body = tail  # <---------------------------------------- parse while-loop bindings and body
            while condition.execute(environ, False):  # <--- while while-loop condition is evaluates to truthy one
                control = body.execute(environ, False)  # <- execute while-loop and guarantee that we give control
                if control == '$control:break':      # <---- and in case of the '$control:break' we break the loop
                    break
                if control == '$control:continue':   # and in case of the '$control:continue' we continue the loop
                    continue
            return None  # <--------------------- behave as imperative loop where there is no return value but nil

        if head.token().value() == 'import':
            SE_ASSERT(where, top,   'Expression[execute]: import: you should place all Python 3 (import)s on top')
            TAIL_IS_VALID(tail, 'import', where,                             'Expression[execute]: import: {why}')
            alias: str = tail[0].token().value()  # <------------------------------- assign alias a type of string
            environ[alias.split('.')[-1]] = importlib.import_module(alias)  # <-------- assign to unqualified path
            return None  # <----------------------------------------------------------------------- and return nil

        if head.token().value() == 'require':
            SE_ASSERT(where, top,      'Expression[execute]: require: you should place all (require)ments on top')
            TAIL_IS_VALID(tail, 'require', where,                           'Expression[execute]: require: {why}')
            alias: str = tail[0].token().value()  # <---------------------------- assign alias as a type of string
            environ[alias.split('/')[-1]] = environ.get('__require__')(alias)  # <----- assign to unqualified path
            return None  # <----------------------------------------------------------------------- and return nil

        handle = head.execute(environ, False)  # resolve handle object by its name, this could raise a 'NameError'

        self._assert_even_number_of_dict_literals()  # verify literals form arity before dictionary initialization

        return handle(*tuple(map(lambda argument: argument.execute(environ,  False),  tail)))  # return the result
