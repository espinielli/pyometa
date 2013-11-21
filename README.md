# PyOMeta - A Pattern-Matching Language in Python

## Summary

PyOMeta is an implementation of [OMeta2][ometa2], an object-oriented pattern-matching language
developed by [Alessandro Warth][AWarth] (http://www.cs.ucla.edu/~awarth/ometa/).
PyOMeta provides a compact syntax based on [Parsing Expression Grammars][PEG] for common lexing,
parsing and tree-transforming activities in a way that's easy to reason about for [Python][python]
programmers.


## How It Works

PyOMeta compiles a grammar to a Python class, with the rules as methods. The
rules specify parsing expressions, which consume input and return values if
they succeed in matching.

### Basic syntax

`foo ::= ....`
:   Define a rule named `foo`.

`expr1 expr2`
:   Match `expr1` and then match `expr2` if it succeeds, returning the value of
    `expr2`. Like Python's `and`.

`expr1 | expr2`
:   Try to match `expr1` --- if it fails, match `expr2` instead. Like Python's `or`.

`expr*`
:   Match `expr` zero or more times, returning a list of matches.

`expr+`
:   Match `expr` one or more times, returning a list of matches.

`expr?`
:   Try to match `expr`. Returns `None` if it fails to match.

`~expr`
:   Fail if the next item in the input matches `expr`.

`ruleName`
:   Call the rule `ruleName`.

`'x'`
:   Match the literal character 'x'.

`expr:name`
:   Bind the result of `expr` to the local variable `name`.

`-> pythonExpression`
:   Evaluate the given Python expression and return its result.

`!(pythonExpression)`
:   Evaluate the given Python expression and return its result (this is used in the rule
    definition part).

`# this is a comment`
:   Comments are like Python comments, they start with `#` and extend to the end of the line.

`<expr>`
:   _Consumed-by_ operator returns a sub-sequence of the input that contains the elements
    matched by the enclosed expression `expr`

`@<expr>`
:    _Index-consumed-by_ operator returns an array with the start and end indices of the
     elements consumed by the enclosed expression `expr`

### Summary Table (TODO: verify and complete)

| "kind of thing"    | PyOMeta      | Note |
|--------------------|--------------|------|
| boolean            | `true`       |      |
| number             | `123`        |      |
| character          | `'x'`        |      |
| string             | `"foo"`      |      |
| rule application   | `expr`       |      |
|                    | `r(x, y)`    | 1    |
|                    | `^digit`     | 4    |
| list               | `['x' 1]`    |      |
| grouping           | `(foo bar)`  |      |
| negation           | `~'x'`       |      |
| look-ahead         | `~~'x'`      |      |
| semantic predicate | `?(x > y)`   | 3    |
| semantic action    | `-> (x + y)` | 3    |
|                    | `!(x + y)`   | 3    |
| binding            | `expr:x`     |      |
|                    | `:x`         |      |


Note 1: the arguments do not necessarily have to be statement expressions -
        they can be any Python expression.

Note 2: not yet in the grammar, only via Python subclassing.

Note 3: semantic predicates and actions are written in Python. More specifically,
        they are either primary expressions, e.g.,
            123
            x
            foo.bar()
        or something called "statement expressions", which have the form
            "{" <statement>* <expr> "}"
        For example,
            { x += 2; y = "foo"; f(x) }
        The value of a statement expression is equal to that of its last expression.

Note 4: "super" is just like any other rule (not a special form), so you have to
        quote the rule name that you pass in as an argument, e.g., both `^r(1, 2)`
        and `super("r", 1, 2)` are valid super-sends.


## Interface

The starting point for defining a new grammar is `pyometa.grammar.OMeta.makeGrammar`,
which takes a grammar definition and a dict of variable bindings for its embedded expressions
and produces a Python class.

Grammars can be subclassed as usual, and makeGrammar can be called on these classes to override
rules and provide new ones. To invoke a grammar rule, call ``grammarObject.apply()`` with its name.


## Example Usage

~~~~~{#usage .python}
>>> from pyometa.grammar import OMeta
>>> exampleGrammar = """
ones = '1' '1' -> 1  # comment
twos = '2' '2' -> 2
stuff = (ones | twos)+
"""
>>> Example = OMeta.makeGrammar(exampleGrammar, {})
>>> g = Example("11221111")
>>> result, error = g.apply("stuff")
>>> result
[1, 2, 1, 1]
~~~~~~~~~~~~~


## References
* [Parsing Expression Grammars][PEG]
* [Alessandro Warth's Home Page][AWarth]
* [OMeta2][ometa2]
* [Python, of course!][python]

[PEG]: <http://bford.info/packrat/> "Parsing Expression Grammar"
[AWarth]: <http://www.tinlizzie.org/~awarth/> "Alessandro Warth"
[ometa2]: <http://www.tinlizzie.org/~awarth/ometa/ometa2.html> "OMeta2"
[python]: <http://www.python.org> "Python Home Page"