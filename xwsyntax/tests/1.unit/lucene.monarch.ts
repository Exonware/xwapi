// lucene.monarch.ts
// Auto-generated Monaco language definition
export const luceneLanguage = {
  "defaultToken": "",
  "tokenPostfix": ".lucene",
  "operators": [
    "\n\nWORD: /[^\\s",
    "\n\nphrase_content: WORD (WS WORD)*\n\ngroup: ",
    "\n\nrange: ",
    "\n\nrange_end: WORD | ",
    "\n\nrange_start: WORD | ",
    "\n\nwildcard: WORD (",
    "\n     | ",
    " (NUMBER)?\n\nboost: clause ",
    " NUMBER\n\nfield_query: FIELD_NAME ",
    " clause\n\nboolean_op: ",
    " phrase_content ",
    " query ",
    " range_end ",
    " range_start ",
    " | ",
    ")+\n\nfuzzy: WORD ",
    "\\"
  ],
  "symbols": "\\\\|\\\n\\\nrange_start:\\ WORD\\ \\|\\ |\\\n\\\nphrase_content:\\ WORD\\ \\(WS\\ WORD\\)\\*\\\n\\\ngroup:\\ |\\ \\|\\ |\\)\\+\\\n\\\nfuzzy:\\ WORD\\ |\\ NUMBER\\\n\\\nfield_query:\\ FIELD_NAME\\ |\\\n\\ \\ \\ \\ \\ \\|\\ |\\\n\\\nwildcard:\\ WORD\\ \\(|\\ clause\\\n\\\nboolean_op:\\ |\\\n\\\nrange:\\ |\\ \\(NUMBER\\)\\?\\\n\\\nboost:\\ clause\\ |\\\n\\\nWORD:\\ /\\[\\^\\\\s|\\ range_end\\ |\\ range_start\\ |\\\n\\\nrange_end:\\ WORD\\ \\|\\ |\\ phrase_content\\ |\\ query\\ ",
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
        "/\\\n\\\nphrase_content:\\ WORD\\ \\(WS\\ WORD\\)\\*\\\n\\\ngroup:\\ /",
        "operator"
      ],
      [
        "/\\ NUMBER\\\n\\\nfield_query:\\ FIELD_NAME\\ /",
        "operator"
      ],
      [
        "/\\ \\(NUMBER\\)\\?\\\n\\\nboost:\\ clause\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nrange_start:\\ WORD\\ \\|\\ /",
        "operator"
      ],
      [
        "/\\ clause\\\n\\\nboolean_op:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nrange_end:\\ WORD\\ \\|\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nwildcard:\\ WORD\\ \\(/",
        "operator"
      ],
      [
        "/\\)\\+\\\n\\\nfuzzy:\\ WORD\\ /",
        "operator"
      ],
      [
        "/\\ phrase_content\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nWORD:\\ /\\[\\^\\\\s/",
        "operator"
      ],
      [
        "/\\ range_start\\ /",
        "operator"
      ],
      [
        "/\\ range_end\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nrange:\\ /",
        "operator"
      ],
      [
        "/\\\n\\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\ query\\ /",
        "operator"
      ],
      [
        "/\\ \\|\\ /",
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
export const luceneLanguageConfig = {};
// Register with Monaco Editor
export function registerLuceneLanguage(monaco: any) {
  monaco.languages.register({ id: 'lucene' });
  monaco.languages.setMonarchTokensProvider('lucene', luceneLanguage);
  monaco.languages.setLanguageConfiguration('lucene', luceneLanguageConfig);
}
