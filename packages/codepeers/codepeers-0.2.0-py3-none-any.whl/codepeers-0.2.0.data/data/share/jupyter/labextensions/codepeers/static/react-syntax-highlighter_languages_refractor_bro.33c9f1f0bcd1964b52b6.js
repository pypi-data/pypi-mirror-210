"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["react-syntax-highlighter_languages_refractor_bro"],{

/***/ "./node_modules/refractor/lang/bro.js":
/*!********************************************!*\
  !*** ./node_modules/refractor/lang/bro.js ***!
  \********************************************/
/***/ ((module) => {



module.exports = bro
bro.displayName = 'bro'
bro.aliases = []
function bro(Prism) {
  Prism.languages.bro = {
    comment: {
      pattern: /(^|[^\\$])#.*/,
      lookbehind: true,
      inside: {
        italic: /\b(?:TODO|FIXME|XXX)\b/
      }
    },
    string: {
      pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
      greedy: true
    },
    boolean: /\b[TF]\b/,
    function: {
      pattern: /(?:function|hook|event) \w+(?:::\w+)?/,
      inside: {
        keyword: /^(?:function|hook|event)/
      }
    },
    variable: {
      pattern: /(?:global|local) \w+/i,
      inside: {
        keyword: /(?:global|local)/
      }
    },
    builtin: /(?:@(?:load(?:-(?:sigs|plugin))?|unload|prefixes|ifn?def|else|(?:end)?if|DIR|FILENAME))|(?:&?(?:redef|priority|log|optional|default|add_func|delete_func|expire_func|read_expire|write_expire|create_expire|synchronized|persistent|rotate_interval|rotate_size|encrypt|raw_output|mergeable|group|error_handler|type_column))/,
    constant: {
      pattern: /const \w+/i,
      inside: {
        keyword: /const/
      }
    },
    keyword: /\b(?:break|next|continue|alarm|using|of|add|delete|export|print|return|schedule|when|timeout|addr|any|bool|count|double|enum|file|int|interval|pattern|opaque|port|record|set|string|subnet|table|time|vector|for|if|else|in|module|function)\b/,
    operator: /--?|\+\+?|!=?=?|<=?|>=?|==?=?|&&|\|\|?|\?|\*|\/|~|\^|%/,
    number: /\b0x[\da-f]+\b|(?:\b\d+\.?\d*|\B\.\d+)(?:e[+-]?\d+)?/i,
    punctuation: /[{}[\];(),.:]/
  }
}


/***/ })

}]);
//# sourceMappingURL=react-syntax-highlighter_languages_refractor_bro.33c9f1f0bcd1964b52b6.js.map