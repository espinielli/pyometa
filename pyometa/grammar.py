"""
Public interface to OMeta, as well as the grammars used to compile grammar
definitions.
"""
from .builder import TreeBuilder, moduleFromGrammar
from .boot import BootOMetaGrammar
from .bootbase import BootBaseTraits
from .runtime import OMetaBase
import string

class OMeta(OMetaBase):
    """
    Base class for grammar definitions.
    """
    metagrammarClass = BootOMetaGrammar
    def makeGrammar(cls, grammar, globals, name="Grammar"):
        """
        Define a new subclass with the rules in the given grammar.

        @param grammar: A string containing a PyOMeta grammar.
        @param globals: A dict of names that should be accessible by this
        grammar.
        @param name: The name of the class to be generated.
        """
        g = cls.metagrammarClass(grammar)
        tree = g.parseGrammar(name, TreeBuilder)
        return moduleFromGrammar(tree, name, cls, globals)

    makeGrammar = classmethod(makeGrammar)

ometaGrammar = r"""
hspace = (' ' | '\t')
vspace = ("\r\n" | '\r' | '\n')
emptyline = hspace* vspace
indentation = emptyline* hspace+
noindentation = emptyline* ~hspace

number = spaces ('-' barenumber:x -> self.builder.exactly(-x)
                    |barenumber:x -> self.builder.exactly(x))
barenumber = '0' (('x'|'X') hexdigit*:hs -> int(''.join(hs), 16)
                    |octaldigit*:ds -> int('0'+''.join(ds), 8))
               |digit+:ds -> int(''.join(ds))
octaldigit = :x ?(x in string.octdigits) -> x
hexdigit = :x ?(x in string.hexdigits) -> x

escapedChar = '\\' ('n' -> "\n"
                     |'r' -> "\r"
                     |'t' -> "\t"
                     |'b' -> "\b"
                     |'f' -> "\f"
                     |'"' -> '"'
                     |'\'' -> "'"
                     |'\\' -> "\\")

character = token("'") (escapedChar | ~('\'') anything)*:c token("'") -> self.builder.exactly(''.join(c))

character2 = token("'") <(escapedChar | ~('\'') anything)*>:c token("'") -> c

range = character2:c1 token("..") character2:c2 ?(c1 < c2) -> self.builder.range(c1, c2)

string = token('"') (escapedChar | ~('"') anything)*:c token('"') -> self.builder.match_string(''.join(c))

name = letter:x letterOrDigit*:xs !(xs.insert(0, x)) -> ''.join(xs)

application = indentation? name:name
                  ('(' !(self.applicationArgs()):args
                    -> self.builder.apply(name, self.name, *args)
                  | -> self.builder.apply(name, self.name))

expr1 = application
          |ruleValue
          |semanticPredicate
          |semanticAction
          |number
          |range
          |character
          |string
          |token('(') expr:e token(')') -> e
          |token('[') expr:e token(']') -> self.builder.listpattern(e)
          |token('<') expr:e token('>') -> self.builder.consumedby(e)
          |token('@<') expr:e token('>') -> self.builder.index_consumedby(e)

expr2 = token('~') (token('~') expr2:e -> self.builder.lookahead(e)
                       |expr2:e -> self.builder._not(e))
          |expr1

expr3 = (expr2:e ('*' -> self.builder.many(e)
                      |'+' -> self.builder.many1(e)
                      |'?' -> self.builder.optional(e)
                      | -> e)):r
           (':' name:n -> self.builder.bind(r, n)
           | -> r)
          |token(':') name:n
           -> self.builder.bind(self.builder.apply("anything", self.name), n)

expr4 :ne = ?(ne) expr3+:es -> self.builder.sequence(es)
          | ?(not ne) expr3*:es -> self.builder.sequence(es)

expr5 :ne = interleavePart:e (token("&&") interleavePart)+:es !(es.insert(0, e))
          -> self.builder.interleave(es)
        | expr4(ne)

interleavePart = token("(") expr4(True):e token(")") -> ["1", e]
 | expr4(True):part modedIPart(part):x -> x

modedIPart = ['Many' :part]     -> ["*", part, None]
           | ['Many1' :part]    -> ["+", part, None]
           | ['Optional' :part] -> ["?", part, None]
           | ['Bind' :name :part]:e modedIPart(part):newpart -> newpart[:2] + [name]
           | ['And' :part] modedIPart(part):newpart -> newpart
           | :part                      -> ["1", part, None]

expr = expr5(True):e (token('|') expr5(True))+:es !(es.insert(0, e))
          -> self.builder._or(es)
      | expr5(True):e (token('||') expr5(True))+:es !(es.insert(0, e))
          -> self.builder._xor(es)
      | expr5(False)

ruleValue = token("->") -> self.ruleValueExpr()

semanticPredicate = token("?(") -> self.semanticPredicateExpr()

semanticAction = token("!(") -> self.semanticActionExpr()

rulePart :requiredName = noindentation name:n ?(n == requiredName)
                            !(setattr(self, "name", n))
                            expr5(False):args
                            (token("=") expr:e
                               -> self.builder.sequence([args, e])
                            |  -> args)
rule = noindentation ~~(name:n) rulePart(n):r
          (rulePart(n)+:rs -> self.builder.rule(n, self.builder._or([r] + rs))
          |                     -> self.builder.rule(n, r))

grammar = rule*:rs spaces -> self.builder.makeGrammar(rs)
"""

class OMetaGrammar(BootBaseTraits, OMeta.makeGrammar(ometaGrammar, globals())):
    """
    The base grammar for parsing grammar definitions.
    """

OMeta.metagrammarClass = OMetaGrammar

nullOptimizationGrammar = r"""

opt = ( ['Apply' :ruleName :codeName [anything*:exprs]] -> self.builder.apply(ruleName, codeName, *exprs)
      | ['Exactly' :expr]       -> self.builder.exactly(expr)
      | ['MatchString' :expr]       -> self.builder.match_string(expr)
      | ['Many' opt:expr]       -> self.builder.many(expr)
      | ['Many1' opt:expr]      -> self.builder.many1(expr)
      | ['Optional' opt:expr]   -> self.builder.optional(expr)
      | ['Or' [opt*:exprs]]     -> self.builder._or(exprs)
      | ['And' [opt*:exprs]]    -> self.builder.sequence(exprs)
      | ['Not' opt:expr]        -> self.builder._not(expr)
      | ['Lookahead' opt:expr]  -> self.builder.lookahead(expr)
      | ['Bind' :name opt:expr] -> self.builder.bind(expr, name)
      | ['Predicate' opt:expr]  -> self.builder.pred(expr)
      | ['Action' :code]        -> self.builder.action(code)
      | ['Python' :code]        -> self.builder.expr(code)
      | ['List' opt:exprs]      -> self.builder.listpattern(exprs)
      | ['ConsumedBy' opt:expr] -> self.builder.consumedby(expr)
      | ['IndexConsumedBy' opt:expr] -> self.builder.index_consumedby(expr)
      | ['Range' :c1 :c2]       -> self.builder.range(c1, c2)
      | ['Interleave' opt:exprs] -> self.builder.interleave(exprs)
      )
grammar = ['Grammar' :name [rulePair*:rs]] -> self.builder.makeGrammar(rs)
rulePair = ['Rule' :name opt:rule] -> self.builder.rule(name, rule)

"""

NullOptimizer = OMeta.makeGrammar(nullOptimizationGrammar, {}, name="NullOptimizer")
