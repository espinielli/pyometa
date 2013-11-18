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

`<ruleName>`
:   Call the rule `ruleName`.

`'x'`
:   Match the literal character 'x'.

`expr:name`
:   Bind the result of `expr` to the local variable `name`.

`=> pythonExpression`
:   Evaluate the given Python expression and return its result.

Comments are like Python comments, they start with `#` and extend to the end of the line.


## Interface

The starting point for defining a new grammar is `pyometa.grammar.OMeta.makeGrammar`,
which takes a grammar definition and a dict of variable bindings for its embedded expressions
and produces a Python class.

Grammars can be subclassed as usual, and makeGrammar can be called on these classes to override
rules and provide new ones. To invoke a grammar rule, call ``grammarObject.apply()`` with its name.


## Example Usage

~~~~~{#usage .python}
>>> from pymeta.grammar import OMeta
>>> exampleGrammar = """
ones ::= '1' '1' => 1
twos ::= '2' '2' => 2
stuff ::= (<ones> | <twos>)+
"""
>>> Example = OMeta.makeGrammar(exampleGrammar, {})
>>> g = Example("11221111")
>>> result, error = g.apply("stuff")
>>> result
[1, 2, 1, 1]
~~~~~~~~~~~~~


## References

[^PEG]: http://bford.info/packrat/ "Parsing Expression Grammar"
[^AWarth]: http://www.tinlizzie.org/~awarth/ "Alessandro Warth"
[^ometa2]: http://www.tinlizzie.org/~awarth/ometa/ometa2.html "OMeta2"
[^python]: http://www.python.org "Python Home Page"