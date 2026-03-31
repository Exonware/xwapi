// sql.monarch.ts
// Auto-generated Monaco language definition
export const sqlLanguage = {
  "defaultToken": "",
  "tokenPostfix": ".sql",
  "ignoreCase": true,
  "keywords": [
    "ALL",
    "BLOB",
    "BOOL",
    "BOOLEAN",
    "CHAR",
    "CROSS",
    "DATE",
    "DATETIME",
    "DECIMAL",
    "DISTINCT",
    "DOUBLE",
    "FLOAT",
    "FULL",
    "INNER",
    "INT",
    "INTEGER",
    "LEFT",
    "NUMERIC",
    "RIGHT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "TOP",
    "VARCHAR"
  ],
  "operators": [
    "!=",
    "%",
    "(",
    ")",
    "*",
    "+",
    ",",
    "-",
    ".",
    "/",
    "/\n\n// Keywords (case-insensitive)\nSELECT: ",
    "<",
    "<=",
    "<>",
    "=",
    ">",
    ">=",
    "[^",
    "]+",
    "i\n\n// Terminals\nQUOTED_IDENTIFIER: /`[^`]+`/ | /\\[[^\\]]+\\]/ | /",
    "i\nADD: ",
    "i\nALTER: ",
    "i\nAND: ",
    "i\nAS: ",
    "i\nASC: ",
    "i\nBETWEEN: ",
    "i\nBOOLEAN: ",
    "i\nBY: ",
    "i\nCHECK: ",
    "i\nCOLUMN: ",
    "i\nCREATE: ",
    "i\nDATABASE: ",
    "i\nDELETE: ",
    "i\nDESC: ",
    "i\nDROP: ",
    "i\nFOREIGN_KEY: ",
    "i\nFROM: ",
    "i\nGROUP: ",
    "i\nHAVING: ",
    "i\nIN: ",
    "i\nINDEX: ",
    "i\nINSERT: ",
    "i\nINTO: ",
    "i\nIS: ",
    "i\nJOIN: ",
    "i\nLIKE: ",
    "i\nLIMIT: ",
    "i\nMODIFY: ",
    "i\nNOT: ",
    "i\nNOT_NULL: ",
    "i\nNULL: ",
    "i\nOFFSET: ",
    "i\nON: ",
    "i\nOR: ",
    "i\nORDER: ",
    "i\nPRIMARY_KEY: ",
    "i\nSET: ",
    "i\nTABLE: ",
    "i\nUNIQUE: ",
    "i\nUPDATE: ",
    "i\nVALUES: ",
    "i\nVIEW: ",
    "i\nWHERE: ",
    "i ",
    "i | "
  ],
  "symbols": "i\\\n\\\n//\\ Terminals\\\nQUOTED_IDENTIFIER:\\ /`\\[\\^`\\]\\+`/\\ \\|\\ /\\\\\\[\\[\\^\\\\\\]\\]\\+\\\\\\]/\\ \\|\\ /|i\\\nIS:\\ |i\\\nOFFSET:\\ |\\-|i\\\nLIKE:\\ |i\\\nLIMIT:\\ |i\\\nNOT:\\ |!=|/|%|i\\\nFROM:\\ |i\\\nCREATE:\\ |i\\\nVALUES:\\ |i\\\nDATABASE:\\ |i\\\nPRIMARY_KEY:\\ |<>|i\\\nUNIQUE:\\ |\\*|i\\\nCHECK:\\ |\\[\\^|i\\\nDELETE:\\ |i\\\nDESC:\\ |i\\\nDROP:\\ |i\\\nTABLE:\\ |\\(|i\\\nJOIN:\\ |i\\\nWHERE:\\ |i\\\nAS:\\ |i\\\nINDEX:\\ |i\\\nNULL:\\ |i\\\nSET:\\ |i\\\nBOOLEAN:\\ |>|i\\\nVIEW:\\ |i\\\nIN:\\ |,|i\\\nCOLUMN:\\ |i\\\nHAVING:\\ |/\\\n\\\n//\\ Keywords\\ \\(case\\-insensitive\\)\\\nSELECT:\\ |i\\\nUPDATE:\\ |i\\\nADD:\\ |i\\\nNOT_NULL:\\ |i\\\nORDER:\\ |=|i\\\nALTER:\\ |i\\\nOR:\\ |i\\\nON:\\ |<=|i\\ |i\\\nINTO:\\ |i\\\nMODIFY:\\ |\\+|i\\\nBY:\\ |i\\\nBETWEEN:\\ |>=|i\\\nAND:\\ |\\)|\\.|i\\\nFOREIGN_KEY:\\ |<|i\\\nINSERT:\\ |i\\\nASC:\\ |i\\ \\|\\ |\\]\\+|i\\\nGROUP:\\ ",
  "brackets": [
    {
      "open": "(",
      "close": ")",
      "token": "delimiter.parenthesis"
    }
  ],
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
        "/i\\\n\\\n//\\ Terminals\\\nQUOTED_IDENTIFIER:\\ /`\\[\\^`\\]\\+`/\\ \\|\\ /\\\\\\[\\[\\^\\\\\\]\\]\\+\\\\\\]/\\ \\|\\ //",
        "operator"
      ],
      [
        "//\\\n\\\n//\\ Keywords\\ \\(case\\-insensitive\\)\\\nSELECT:\\ /",
        "operator"
      ],
      [
        "/i\\\nPRIMARY_KEY:\\ /",
        "operator"
      ],
      [
        "/i\\\nFOREIGN_KEY:\\ /",
        "operator"
      ],
      [
        "/i\\\nDATABASE:\\ /",
        "operator"
      ],
      [
        "/i\\\nNOT_NULL:\\ /",
        "operator"
      ],
      [
        "/i\\\nBOOLEAN:\\ /",
        "operator"
      ],
      [
        "/i\\\nBETWEEN:\\ /",
        "operator"
      ],
      [
        "/i\\\nOFFSET:\\ /",
        "operator"
      ],
      [
        "/i\\\nCREATE:\\ /",
        "operator"
      ],
      [
        "/i\\\nVALUES:\\ /",
        "operator"
      ],
      [
        "/i\\\nUNIQUE:\\ /",
        "operator"
      ],
      [
        "/i\\\nDELETE:\\ /",
        "operator"
      ],
      [
        "/i\\\nCOLUMN:\\ /",
        "operator"
      ],
      [
        "/i\\\nHAVING:\\ /",
        "operator"
      ],
      [
        "/i\\\nUPDATE:\\ /",
        "operator"
      ],
      [
        "/i\\\nMODIFY:\\ /",
        "operator"
      ],
      [
        "/i\\\nINSERT:\\ /",
        "operator"
      ],
      [
        "/i\\\nLIMIT:\\ /",
        "operator"
      ],
      [
        "/i\\\nCHECK:\\ /",
        "operator"
      ],
      [
        "/i\\\nTABLE:\\ /",
        "operator"
      ],
      [
        "/i\\\nWHERE:\\ /",
        "operator"
      ],
      [
        "/i\\\nINDEX:\\ /",
        "operator"
      ],
      [
        "/i\\\nORDER:\\ /",
        "operator"
      ],
      [
        "/i\\\nALTER:\\ /",
        "operator"
      ],
      [
        "/i\\\nGROUP:\\ /",
        "operator"
      ],
      [
        "/i\\\nLIKE:\\ /",
        "operator"
      ],
      [
        "/i\\\nFROM:\\ /",
        "operator"
      ],
      [
        "/i\\\nDESC:\\ /",
        "operator"
      ],
      [
        "/i\\\nDROP:\\ /",
        "operator"
      ],
      [
        "/i\\\nJOIN:\\ /",
        "operator"
      ],
      [
        "/i\\\nNULL:\\ /",
        "operator"
      ],
      [
        "/i\\\nVIEW:\\ /",
        "operator"
      ],
      [
        "/i\\\nINTO:\\ /",
        "operator"
      ],
      [
        "/i\\\nNOT:\\ /",
        "operator"
      ],
      [
        "/i\\\nSET:\\ /",
        "operator"
      ],
      [
        "/i\\\nADD:\\ /",
        "operator"
      ],
      [
        "/i\\\nAND:\\ /",
        "operator"
      ],
      [
        "/i\\\nASC:\\ /",
        "operator"
      ],
      [
        "/i\\\nIS:\\ /",
        "operator"
      ],
      [
        "/i\\\nAS:\\ /",
        "operator"
      ],
      [
        "/i\\\nIN:\\ /",
        "operator"
      ],
      [
        "/i\\\nOR:\\ /",
        "operator"
      ],
      [
        "/i\\\nON:\\ /",
        "operator"
      ],
      [
        "/i\\\nBY:\\ /",
        "operator"
      ],
      [
        "/i\\ \\|\\ /",
        "operator"
      ],
      [
        "/!=/",
        "operator"
      ],
      [
        "/<>/",
        "operator"
      ],
      [
        "/\\[\\^/",
        "operator"
      ],
      [
        "/<=/",
        "operator"
      ],
      [
        "/i\\ /",
        "operator"
      ],
      [
        "/>=/",
        "operator"
      ],
      [
        "/\\]\\+/",
        "operator"
      ],
      [
        "/\\-/",
        "operator"
      ],
      [
        "///",
        "operator"
      ],
      [
        "/%/",
        "operator"
      ],
      [
        "/\\*/",
        "operator"
      ],
      [
        "/\\(/",
        "operator"
      ],
      [
        "/>/",
        "operator"
      ],
      [
        "/,/",
        "operator"
      ],
      [
        "/=/",
        "operator"
      ],
      [
        "/\\+/",
        "operator"
      ],
      [
        "/\\)/",
        "operator"
      ],
      [
        "/\\./",
        "operator"
      ],
      [
        "/</",
        "operator"
      ],
      [
        "/[()[\\]{}]/",
        "@brackets"
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
export const sqlLanguageConfig = {
  "brackets": [
    [
      "(",
      ")"
    ]
  ],
  "autoClosingPairs": [
    {
      "open": "(",
      "close": ")"
    },
    {
      "open": "'",
      "close": "'"
    }
  ],
  "surroundingPairs": [
    {
      "open": "(",
      "close": ")"
    },
    {
      "open": "'",
      "close": "'"
    }
  ]
};
// Register with Monaco Editor
export function registerSqlLanguage(monaco: any) {
  monaco.languages.register({ id: 'sql' });
  monaco.languages.setMonarchTokensProvider('sql', sqlLanguage);
  monaco.languages.setLanguageConfiguration('sql', sqlLanguageConfig);
}
