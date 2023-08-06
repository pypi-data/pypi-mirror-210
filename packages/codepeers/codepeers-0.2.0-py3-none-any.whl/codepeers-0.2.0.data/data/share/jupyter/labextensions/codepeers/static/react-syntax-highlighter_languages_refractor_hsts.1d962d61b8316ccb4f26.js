"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["react-syntax-highlighter_languages_refractor_hsts"],{

/***/ "./node_modules/refractor/lang/hsts.js":
/*!*********************************************!*\
  !*** ./node_modules/refractor/lang/hsts.js ***!
  \*********************************************/
/***/ ((module) => {



module.exports = hsts
hsts.displayName = 'hsts'
hsts.aliases = []
function hsts(Prism) {
  /**
   * Original by Scott Helme.
   *
   * Reference: https://scotthelme.co.uk/hsts-cheat-sheet/
   */
  Prism.languages.hsts = {
    directive: {
      pattern: /\b(?:max-age=|includeSubDomains|preload)/,
      alias: 'keyword'
    },
    safe: {
      pattern: /\d{8,}/,
      alias: 'selector'
    },
    unsafe: {
      pattern: /\d{1,7}/,
      alias: 'function'
    }
  }
}


/***/ })

}]);
//# sourceMappingURL=react-syntax-highlighter_languages_refractor_hsts.1d962d61b8316ccb4f26.js.map