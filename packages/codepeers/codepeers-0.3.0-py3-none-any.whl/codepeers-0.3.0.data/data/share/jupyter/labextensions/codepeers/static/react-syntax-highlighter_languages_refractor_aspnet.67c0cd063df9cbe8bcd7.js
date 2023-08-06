"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["react-syntax-highlighter_languages_refractor_aspnet"],{

/***/ "./node_modules/refractor/lang/aspnet.js":
/*!***********************************************!*\
  !*** ./node_modules/refractor/lang/aspnet.js ***!
  \***********************************************/
/***/ ((module) => {



module.exports = aspnet
aspnet.displayName = 'aspnet'
aspnet.aliases = []
function aspnet(Prism) {
  Prism.languages.aspnet = Prism.languages.extend('markup', {
    'page-directive tag': {
      pattern: /<%\s*@.*%>/i,
      inside: {
        'page-directive tag': /<%\s*@\s*(?:Assembly|Control|Implements|Import|Master(?:Type)?|OutputCache|Page|PreviousPageType|Reference|Register)?|%>/i,
        rest: Prism.languages.markup.tag.inside
      }
    },
    'directive tag': {
      pattern: /<%.*%>/i,
      inside: {
        'directive tag': /<%\s*?[$=%#:]{0,2}|%>/i,
        rest: Prism.languages.csharp
      }
    }
  }) // Regexp copied from prism-markup, with a negative look-ahead added
  Prism.languages.aspnet.tag.pattern = /<(?!%)\/?[^\s>\/]+(?:\s+[^\s>\/=]+(?:=(?:("|')(?:\\[\s\S]|(?!\1)[^\\])*\1|[^\s'">=]+))?)*\s*\/?>/i // match directives of attribute value foo="<% Bar %>"
  Prism.languages.insertBefore(
    'inside',
    'punctuation',
    {
      'directive tag': Prism.languages.aspnet['directive tag']
    },
    Prism.languages.aspnet.tag.inside['attr-value']
  )
  Prism.languages.insertBefore('aspnet', 'comment', {
    'asp comment': /<%--[\s\S]*?--%>/
  }) // script runat="server" contains csharp, not javascript
  Prism.languages.insertBefore(
    'aspnet',
    Prism.languages.javascript ? 'script' : 'tag',
    {
      'asp script': {
        pattern: /(<script(?=.*runat=['"]?server['"]?)[\s\S]*?>)[\s\S]*?(?=<\/script>)/i,
        lookbehind: true,
        inside: Prism.languages.csharp || {}
      }
    }
  )
}


/***/ })

}]);
//# sourceMappingURL=react-syntax-highlighter_languages_refractor_aspnet.67c0cd063df9cbe8bcd7.js.map