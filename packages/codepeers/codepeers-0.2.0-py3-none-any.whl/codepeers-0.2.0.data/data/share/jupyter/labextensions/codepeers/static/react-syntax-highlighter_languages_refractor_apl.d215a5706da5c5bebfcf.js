"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["react-syntax-highlighter_languages_refractor_apl"],{

/***/ "./node_modules/refractor/lang/apl.js":
/*!********************************************!*\
  !*** ./node_modules/refractor/lang/apl.js ***!
  \********************************************/
/***/ ((module) => {



module.exports = apl
apl.displayName = 'apl'
apl.aliases = []
function apl(Prism) {
  Prism.languages.apl = {
    comment: /(?:⍝|#[! ]).*$/m,
    string: {
      pattern: /'(?:[^'\r\n]|'')*'/,
      greedy: true
    },
    number: /¯?(?:\d*\.?\d+(?:e[+¯]?\d+)?|¯|∞)(?:j¯?(?:\d*\.?\d+(?:e[+¯]?\d+)?|¯|∞))?/i,
    statement: /:[A-Z][a-z][A-Za-z]*\b/,
    'system-function': {
      pattern: /⎕[A-Z]+/i,
      alias: 'function'
    },
    constant: /[⍬⌾#⎕⍞]/,
    function: /[-+×÷⌈⌊∣|⍳⍸?*⍟○!⌹<≤=>≥≠≡≢∊⍷∪∩~∨∧⍱⍲⍴,⍪⌽⊖⍉↑↓⊂⊃⊆⊇⌷⍋⍒⊤⊥⍕⍎⊣⊢⍁⍂≈⍯↗¤→]/,
    'monadic-operator': {
      pattern: /[\\\/⌿⍀¨⍨⌶&∥]/,
      alias: 'operator'
    },
    'dyadic-operator': {
      pattern: /[.⍣⍠⍤∘⌸@⌺]/,
      alias: 'operator'
    },
    assignment: {
      pattern: /←/,
      alias: 'keyword'
    },
    punctuation: /[\[;\]()◇⋄]/,
    dfn: {
      pattern: /[{}⍺⍵⍶⍹∇⍫:]/,
      alias: 'builtin'
    }
  }
}


/***/ })

}]);
//# sourceMappingURL=react-syntax-highlighter_languages_refractor_apl.d215a5706da5c5bebfcf.js.map