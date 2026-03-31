// xslt.monarch.ts
// Auto-generated Monaco language definition
export const xsltLanguage = {
  "defaultToken": "",
  "tokenPostfix": ".xslt",
  "operators": [
    "\n\nattribute: IDENTIFIER ",
    "\n\nxsl_apply_templates: ",
    "\n\nxsl_choose: ",
    "\n\nxsl_for_each: ",
    "\n\nxsl_if: ",
    "\n\nxsl_otherwise: ",
    "\n\nxsl_when: ",
    " (attribute)* ",
    " (content)* ",
    " (xsl_when)* (xsl_otherwise)? ",
    " /[^",
    " IDENTIFIER ",
    " IDENTIFIER (attribute)* (",
    " attribute_value\n\nattribute_value: ",
    " | ",
    ")\n\ncontent: xsl_element | literal_element | text | xsl_value_of | xsl_for_each | xsl_if | xsl_choose | xsl_apply_templates\n\nxsl_value_of: ",
    ")\n\nliteral_element: ",
    "/\n\nstylesheet_element: xsl_element | literal_element\n\nxsl_element: ",
    "<?xml",
    "?>",
    "[^",
    "\\"
  ],
  "symbols": "\\)\\\n\\\nliteral_element:\\ |\\\n\\\nxsl_otherwise:\\ |\\)\\\n\\\ncontent:\\ xsl_element\\ \\|\\ literal_element\\ \\|\\ text\\ \\|\\ xsl_value_of\\ \\|\\ xsl_for_each\\ \\|\\ xsl_if\\ \\|\\ xsl_choose\\ \\|\\ xsl_apply_templates\\\n\\\nxsl_value_of:\\ |\\[\\^|\\ IDENTIFIER\\ |\\ \\(attribute\\)\\*\\ |\\\n\\\nattribute:\\ IDENTIFIER\\ |\\ attribute_value\\\n\\\nattribute_value:\\ |\\?>|\\ \\|\\ |\\ IDENTIFIER\\ \\(attribute\\)\\*\\ \\(|\\ \\(content\\)\\*\\ |<\\?xml|\\\n\\\nxsl_if:\\ |\\\\|\\\n\\\nxsl_choose:\\ |\\ /\\[\\^|\\\n\\\nxsl_for_each:\\ |\\ \\(xsl_when\\)\\*\\ \\(xsl_otherwise\\)\\?\\ |\\\n\\\nxsl_apply_templates:\\ |/\\\n\\\nstylesheet_element:\\ xsl_element\\ \\|\\ literal_element\\\n\\\nxsl_element:\\ |\\\n\\\nxsl_when:\\ ",
  "tokenizer": {
    "root": [
      {
        "include": "@whitespace"
      },
      [
        "/\\d+(\\.\\d+)?([eE][+-]?\\d+)?/",
        "number"
      ],
      [
        "/\"([^\"\\\\]|\\\\.)*\"/",
        "string"
      ],
      [
        "/'([^'\\\\]|\\\\.)*'/",
        "string"
      ],
      [
        "/[a-zA-Z_][\\w]*/",
        {
          "cases": {
            "@keywords": "keyword",
            "@default": "identifier"
          }
        }
      ],
      [
        "/\\)\\\n\\\ncontent:\\ xsl_element\\ \\|\\ literal_element\\ \\|\\ text\\ \\|\\ xsl_value_of\\ \\|\\ xsl_for_each\\ \\|\\ xsl_if\\ \\|\\ xsl_choose\\ \\|\\ xsl_apply_templates\\\n\\\nxsl_value_of:\\ /",
        "operator"
      ],
      [
        "//\\\n\\\nstylesheet_element:\\ xsl_element\\ \\|\\ literal_element\\\n\\\nxsl_element:\\ /",
        "operator"
      ],
      [
        "/\\ attribute_value\\\n\\\nattribute_value:\\ /",
        "operator"
      ],
      [
        "/\\ \\(xsl_when\\)\\*\\ \\(xsl_otherwise\\)\\?\\ /",
        "operator"
      ],
      [
        "/\\ IDENTIFIER\\ \\(attribute\\)\\*\\ \\(/",
        "operator"
      ],
      [
        "/\\\n\\\nattribute:\\ IDENTIFIER\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_apply_templates:\\ /",
        "operator"
      ],
      [
        "/\\)\\\n\\\nliteral_element:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_otherwise:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_for_each:\\ /",
        "operator"
      ],
      [
        "/\\ \\(attribute\\)\\*\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_choose:\\ /",
        "operator"
      ],
      [
        "/\\ IDENTIFIER\\ /",
        "operator"
      ],
      [
        "/\\ \\(content\\)\\*\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_when:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nxsl_if:\\ /",
        "operator"
      ],
      [
        "/<\\?xml/",
        "operator"
      ],
      [
        "/\\ /\\[\\^/",
        "operator"
      ],
      [
        "/\\ \\|\\ /",
        "operator"
      ],
      [
        "/\\[\\^/",
        "operator"
      ],
      [
        "/\\?>/",
        "operator"
      ],
      [
        "/\\\\/",
        "operator"
      ],
      [
        "/[;,.]/",
        "delimiter"
      ]
    ],
    "whitespace": [
      [
        "/[ \\t\\r\\n]+/",
        ""
      ],
      [
        "/--.*$/",
        "comment"
      ],
      [
        "/\\/\\/.*$/",
        "comment"
      ],
      [
        "/\\/\\*/",
        "comment",
        "@comment"
      ]
    ],
    "comment": [
      [
        "/[^/*]+/",
        "comment"
      ],
      [
        "/\\*\\//",
        "comment",
        "@pop"
      ],
      [
        "/[/*]/",
        "comment"
      ]
    ]
  }
};
export const xsltLanguageConfig = {};
// Register with Monaco Editor
export function registerXsltLanguage(monaco: any) {
  monaco.languages.register({ id: 'xslt' });
  monaco.languages.setMonarchTokensProvider('xslt', xsltLanguage);
  monaco.languages.setLanguageConfiguration('xslt', xsltLanguageConfig);
}
