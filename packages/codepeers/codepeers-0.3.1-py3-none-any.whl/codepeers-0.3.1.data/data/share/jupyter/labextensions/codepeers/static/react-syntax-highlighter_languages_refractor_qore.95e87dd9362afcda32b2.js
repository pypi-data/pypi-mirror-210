"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["react-syntax-highlighter_languages_refractor_qore"],{

/***/ "./node_modules/refractor/lang/qore.js":
/*!*********************************************!*\
  !*** ./node_modules/refractor/lang/qore.js ***!
  \*********************************************/
/***/ ((module) => {



module.exports = qore
qore.displayName = 'qore'
qore.aliases = []
function qore(Prism) {
  Prism.languages.qore = Prism.languages.extend('clike', {
    comment: {
      pattern: /(^|[^\\])(?:\/\*[\s\S]*?\*\/|(?:\/\/|#).*)/,
      lookbehind: true
    },
    // Overridden to allow unescaped multi-line strings
    string: {
      pattern: /("|')(\\[\s\S]|(?!\1)[^\\])*\1/,
      greedy: true
    },
    variable: /\$(?!\d)\w+\b/,
    keyword: /\b(?:abstract|any|assert|binary|bool|boolean|break|byte|case|catch|char|class|code|const|continue|data|default|do|double|else|enum|extends|final|finally|float|for|goto|hash|if|implements|import|inherits|instanceof|int|interface|long|my|native|new|nothing|null|object|our|own|private|reference|rethrow|return|short|soft(?:int|float|number|bool|string|date|list)|static|strictfp|string|sub|super|switch|synchronized|this|throw|throws|transient|try|void|volatile|while)\b/,
    number: /\b(?:0b[01]+|0x[\da-f]*\.?[\da-fp\-]+|\d*\.?\d+e?\d*[df]|\d*\.?\d+)\b/i,
    boolean: /\b(?:true|false)\b/i,
    operator: {
      pattern: /(^|[^.])(?:\+[+=]?|-[-=]?|[!=](?:==?|~)?|>>?=?|<(?:=>?|<=?)?|&[&=]?|\|[|=]?|[*\/%^]=?|[~?])/,
      lookbehind: true
    },
    function: /\$?\b(?!\d)\w+(?=\()/
  })
}


/***/ })

}]);
//# sourceMappingURL=react-syntax-highlighter_languages_refractor_qore.95e87dd9362afcda32b2.js.map