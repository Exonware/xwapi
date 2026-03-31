// elasticsearch.monarch.ts
// Auto-generated Monaco language definition
export const elasticsearchLanguage = {
  "defaultToken": "",
  "tokenPostfix": ".elasticsearch",
  "operators": [
    "\n\n// Aggregation\naggregation_query: ",
    "\n\n// Bool query\nbool_query: ",
    "\n\n// Exists query\nexists_query: ",
    "\n\n// Nested query\nnested_query: ",
    "\n\n// Range query\nrange_query: ",
    "\n\n// Terminals\nIDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/\nSTRING: /",
    "\n\n// Wildcard query\nwildcard_query: ",
    "\n\nNULL: ",
    "\n\nagg_definition: STRING ",
    "\n\nagg_param: STRING ",
    "\n\nagg_params: ",
    "\n\nagg_type: ",
    "\n\nbool_clauses: bool_clause (",
    "\n\nfield_match: STRING ",
    "\n\nfield_value: STRING ",
    "\n\nfuzzy_options: fuzzy_option (",
    "\n\nmatch_options: match_option (",
    "\n\nmatch_query: ",
    "\n\nmulti_match_params: ",
    "\n\nquery_string_options: query_string_option (",
    "\n\nrange_condition: range_op ",
    "\n           | query\n\n// Multi-match query\nmulti_match_query: ",
    "\n        | ",
    " (",
    " (STRING | NUMBER)\n            | ",
    " (STRING | match_params)\n\nmatch_params: ",
    " NUMBER\n\n// Prefix query\nprefix_query: ",
    " NUMBER\n\nquery_array: ",
    " NUMBER\n            | ",
    " STRING\n\n// Fuzzy query\nfuzzy_query: ",
    " STRING\n\n// Term queries\nterm_query: ",
    " STRING\n                   | ",
    " STRING ",
    " STRING (",
    " STRING [",
    " STRING)* ",
    " [",
    " agg_definition (",
    " agg_definition)* ",
    " agg_param (",
    " agg_param)* ",
    " agg_params ",
    " agg_type ",
    " bool_clause)*\n\nbool_clause: ",
    " bool_clauses ",
    " field_match ",
    " field_value ",
    " fuzzy_option)*\n\nfuzzy_option: ",
    " fuzzy_options] ",
    " match_option)*\n\nmatch_option: ",
    " match_options]\n\n// Query string\nquery_string_query: ",
    " match_options] ",
    " multi_match_params ",
    " query ",
    " query (",
    " query)* ",
    " query_array\n           | ",
    " query_string_option)*\n\nquery_string_option: ",
    " query_string_options] ",
    " range_condition (",
    " range_condition)* ",
    " value\n\n// Values\nvalue: STRING | NUMBER | BOOLEAN_LITERAL | NULL\n\nBOOLEAN_LITERAL: ",
    " value\n\nrange_op: ",
    " value\n\nterms_query: ",
    " value (",
    " value)* ",
    " | ",
    ")\n                   | ",
    ")\n            | ",
    "AND\\",
    "OR\\",
    "\\",
    "]*",
    "aggs\\",
    "analyzer\\",
    "and\\",
    "avg\\",
    "bool\\",
    "cardinality\\",
    "date_histogram\\",
    "default_field\\",
    "default_operator\\",
    "exists\\",
    "field\\",
    "fields\\",
    "filter\\",
    "fuzziness\\",
    "fuzzy\\",
    "gt\\",
    "gte\\",
    "histogram\\",
    "lt\\",
    "lte\\",
    "match\\",
    "max\\",
    "min\\",
    "minimum_should_match\\",
    "multi_match\\",
    "must\\",
    "must_not\\",
    "nested\\",
    "operator\\",
    "or\\",
    "path\\",
    "prefix\\",
    "prefix_length\\",
    "query\\",
    "query_string\\",
    "range\\",
    "should\\",
    "stats\\",
    "sum\\",
    "term\\",
    "terms\\",
    "value\\",
    "wildcard\\",
    "{"
  ],
  "symbols": "\\ multi_match_params\\ |\\ range_condition\\ \\(|stats\\\\|\\ \\(|histogram\\\\|\\ NUMBER\\\n\\\n//\\ Prefix\\ query\\\nprefix_query:\\ |\\ agg_definition\\)\\*\\ |\\ field_value\\ |\\ STRING\\\n\\\n//\\ Fuzzy\\ query\\\nfuzzy_query:\\ |\\\n\\\n//\\ Range\\ query\\\nrange_query:\\ |\\ query_string_options\\]\\ |avg\\\\|\\ field_match\\ |wildcard\\\\|\\ \\(STRING\\ \\|\\ match_params\\)\\\n\\\nmatch_params:\\ |\\\n\\\nNULL:\\ |\\\n\\\nmatch_options:\\ match_option\\ \\(|\\ NUMBER\\\n\\\nquery_array:\\ |fuzziness\\\\|\\ agg_param\\)\\*\\ |\\ value\\ \\(|fuzzy\\\\|\\ agg_definition\\ \\(|minimum_should_match\\\\|\\ query\\ |\\ query_string_option\\)\\*\\\n\\\nquery_string_option:\\ |\\\n\\\nagg_type:\\ |multi_match\\\\|\\ match_options\\]\\ |\\ fuzzy_options\\]\\ |date_histogram\\\\|\\\n\\\n//\\ Aggregation\\\naggregation_query:\\ |gte\\\\|\\\n\\\nmulti_match_params:\\ |term\\\\|bool\\\\|field\\\\|match\\\\|\\ query\\ \\(|\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |\\ NUMBER\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |nested\\\\|must\\\\|fields\\\\|min\\\\|\\\n\\\nrange_condition:\\ range_op\\ |prefix_length\\\\|\\ agg_type\\ |cardinality\\\\|\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |value\\\\|max\\\\|\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ query\\\n\\\n//\\ Multi\\-match\\ query\\\nmulti_match_query:\\ |must_not\\\\|\\ STRING\\ \\(|\\\n\\\n//\\ Nested\\ query\\\nnested_query:\\ |exists\\\\|or\\\\|filter\\\\|\\ STRING\\\n\\\n//\\ Term\\ queries\\\nterm_query:\\ |should\\\\|\\\\|\\ bool_clauses\\ |\\\n\\\nagg_definition:\\ STRING\\ |\\ value\\\n\\\nterms_query:\\ |\\\n\\\nquery_string_options:\\ query_string_option\\ \\(|\\\n\\\nmatch_query:\\ |\\ bool_clause\\)\\*\\\n\\\nbool_clause:\\ |\\\n\\\nfield_value:\\ STRING\\ |\\ agg_param\\ \\(|\\ value\\\n\\\n//\\ Values\\\nvalue:\\ STRING\\ \\|\\ NUMBER\\ \\|\\ BOOLEAN_LITERAL\\ \\|\\ NULL\\\n\\\nBOOLEAN_LITERAL:\\ |range\\\\|\\\n\\\n//\\ Bool\\ query\\\nbool_query:\\ |OR\\\\|\\ STRING\\ |\\\n\\\n//\\ Terminals\\\nIDENTIFIER:\\ /\\[a\\-zA\\-Z_\\]\\[a\\-zA\\-Z0\\-9_\\]\\*/\\\nSTRING:\\ /|query\\\\|query_string\\\\|\\\n\\\n//\\ Exists\\ query\\\nexists_query:\\ |\\\n\\\nagg_params:\\ |\\\n\\\n//\\ Wildcard\\ query\\\nwildcard_query:\\ |lt\\\\|\\ \\(STRING\\ \\|\\ NUMBER\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |terms\\\\|\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |\\ range_condition\\)\\*\\ |\\ match_options\\]\\\n\\\n//\\ Query\\ string\\\nquery_string_query:\\ |\\ STRING\\)\\*\\ |\\\n\\\nfield_match:\\ STRING\\ |\\ fuzzy_option\\)\\*\\\n\\\nfuzzy_option:\\ |\\ value\\\n\\\nrange_op:\\ |\\{|\\ agg_params\\ |\\\n\\\nagg_param:\\ STRING\\ |\\ match_option\\)\\*\\\n\\\nmatch_option:\\ |AND\\\\|\\ query\\)\\*\\ |\\\n\\\nbool_clauses:\\ bool_clause\\ \\(|default_operator\\\\|default_field\\\\|\\ query_array\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |\\ STRING\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ |\\ value\\)\\*\\ |sum\\\\|analyzer\\\\|gt\\\\|\\ STRING\\ \\[|operator\\\\|\\ \\|\\ |\\ \\[|\\\n\\\nfuzzy_options:\\ fuzzy_option\\ \\(|aggs\\\\|lte\\\\|and\\\\|path\\\\|prefix\\\\|\\]\\*",
  "brackets": [
    {
      "open": "{",
      "close": "}",
      "token": "delimiter.curly"
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
        "/\\ value\\\n\\\n//\\ Values\\\nvalue:\\ STRING\\ \\|\\ NUMBER\\ \\|\\ BOOLEAN_LITERAL\\ \\|\\ NULL\\\n\\\nBOOLEAN_LITERAL:\\ /",
        "operator"
      ],
      [
        "/\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ query\\\n\\\n//\\ Multi\\-match\\ query\\\nmulti_match_query:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Terminals\\\nIDENTIFIER:\\ /\\[a\\-zA\\-Z_\\]\\[a\\-zA\\-Z0\\-9_\\]\\*/\\\nSTRING:\\ //",
        "operator"
      ],
      [
        "/\\ match_options\\]\\\n\\\n//\\ Query\\ string\\\nquery_string_query:\\ /",
        "operator"
      ],
      [
        "/\\ query_string_option\\)\\*\\\n\\\nquery_string_option:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nquery_string_options:\\ query_string_option\\ \\(/",
        "operator"
      ],
      [
        "/\\ \\(STRING\\ \\|\\ match_params\\)\\\n\\\nmatch_params:\\ /",
        "operator"
      ],
      [
        "/\\ NUMBER\\\n\\\n//\\ Prefix\\ query\\\nprefix_query:\\ /",
        "operator"
      ],
      [
        "/\\ STRING\\\n\\\n//\\ Fuzzy\\ query\\\nfuzzy_query:\\ /",
        "operator"
      ],
      [
        "/\\ STRING\\\n\\\n//\\ Term\\ queries\\\nterm_query:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Aggregation\\\naggregation_query:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Wildcard\\ query\\\nwildcard_query:\\ /",
        "operator"
      ],
      [
        "/\\ \\(STRING\\ \\|\\ NUMBER\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Nested\\ query\\\nnested_query:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Exists\\ query\\\nexists_query:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nmatch_options:\\ match_option\\ \\(/",
        "operator"
      ],
      [
        "/\\ fuzzy_option\\)\\*\\\n\\\nfuzzy_option:\\ /",
        "operator"
      ],
      [
        "/\\ match_option\\)\\*\\\n\\\nmatch_option:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nfuzzy_options:\\ fuzzy_option\\ \\(/",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Range\\ query\\\nrange_query:\\ /",
        "operator"
      ],
      [
        "/\\ bool_clause\\)\\*\\\n\\\nbool_clause:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nbool_clauses:\\ bool_clause\\ \\(/",
        "operator"
      ],
      [
        "/\\ STRING\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nrange_condition:\\ range_op\\ /",
        "operator"
      ],
      [
        "/\\\n\\\n//\\ Bool\\ query\\\nbool_query:\\ /",
        "operator"
      ],
      [
        "/\\ query_array\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nagg_definition:\\ STRING\\ /",
        "operator"
      ],
      [
        "/\\ query_string_options\\]\\ /",
        "operator"
      ],
      [
        "/\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\ NUMBER\\\n\\\nquery_array:\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nmulti_match_params:\\ /",
        "operator"
      ],
      [
        "/\\ NUMBER\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nfield_value:\\ STRING\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nfield_match:\\ STRING\\ /",
        "operator"
      ],
      [
        "/minimum_should_match\\\\/",
        "operator"
      ],
      [
        "/\\ value\\\n\\\nterms_query:\\ /",
        "operator"
      ],
      [
        "/\\ multi_match_params\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nagg_param:\\ STRING\\ /",
        "operator"
      ],
      [
        "/\\ range_condition\\)\\*\\ /",
        "operator"
      ],
      [
        "/\\ range_condition\\ \\(/",
        "operator"
      ],
      [
        "/\\ agg_definition\\)\\*\\ /",
        "operator"
      ],
      [
        "/\\ value\\\n\\\nrange_op:\\ /",
        "operator"
      ],
      [
        "/\\ agg_definition\\ \\(/",
        "operator"
      ],
      [
        "/default_operator\\\\/",
        "operator"
      ],
      [
        "/\\ match_options\\]\\ /",
        "operator"
      ],
      [
        "/\\ fuzzy_options\\]\\ /",
        "operator"
      ],
      [
        "/\\)\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/date_histogram\\\\/",
        "operator"
      ],
      [
        "/\\\n\\\nmatch_query:\\ /",
        "operator"
      ],
      [
        "/prefix_length\\\\/",
        "operator"
      ],
      [
        "/\\ bool_clauses\\ /",
        "operator"
      ],
      [
        "/\\\n\\\nagg_params:\\ /",
        "operator"
      ],
      [
        "/default_field\\\\/",
        "operator"
      ],
      [
        "/\\ field_value\\ /",
        "operator"
      ],
      [
        "/\\ field_match\\ /",
        "operator"
      ],
      [
        "/\\ agg_param\\)\\*\\ /",
        "operator"
      ],
      [
        "/query_string\\\\/",
        "operator"
      ],
      [
        "/\\\n\\\nagg_type:\\ /",
        "operator"
      ],
      [
        "/multi_match\\\\/",
        "operator"
      ],
      [
        "/cardinality\\\\/",
        "operator"
      ],
      [
        "/\\ agg_param\\ \\(/",
        "operator"
      ],
      [
        "/\\ agg_params\\ /",
        "operator"
      ],
      [
        "/\\\n\\ \\ \\ \\ \\ \\ \\ \\ \\|\\ /",
        "operator"
      ],
      [
        "/histogram\\\\/",
        "operator"
      ],
      [
        "/fuzziness\\\\/",
        "operator"
      ],
      [
        "/\\ agg_type\\ /",
        "operator"
      ],
      [
        "/\\ STRING\\)\\*\\ /",
        "operator"
      ],
      [
        "/wildcard\\\\/",
        "operator"
      ],
      [
        "/must_not\\\\/",
        "operator"
      ],
      [
        "/\\ STRING\\ \\(/",
        "operator"
      ],
      [
        "/\\ query\\)\\*\\ /",
        "operator"
      ],
      [
        "/\\ value\\)\\*\\ /",
        "operator"
      ],
      [
        "/analyzer\\\\/",
        "operator"
      ],
      [
        "/\\ STRING\\ \\[/",
        "operator"
      ],
      [
        "/operator\\\\/",
        "operator"
      ],
      [
        "/\\\n\\\nNULL:\\ /",
        "operator"
      ],
      [
        "/\\ value\\ \\(/",
        "operator"
      ],
      [
        "/\\ query\\ \\(/",
        "operator"
      ],
      [
        "/\\ STRING\\ /",
        "operator"
      ],
      [
        "/\\ query\\ /",
        "operator"
      ],
      [
        "/nested\\\\/",
        "operator"
      ],
      [
        "/fields\\\\/",
        "operator"
      ],
      [
        "/exists\\\\/",
        "operator"
      ],
      [
        "/filter\\\\/",
        "operator"
      ],
      [
        "/should\\\\/",
        "operator"
      ],
      [
        "/prefix\\\\/",
        "operator"
      ],
      [
        "/stats\\\\/",
        "operator"
      ],
      [
        "/fuzzy\\\\/",
        "operator"
      ],
      [
        "/field\\\\/",
        "operator"
      ],
      [
        "/match\\\\/",
        "operator"
      ],
      [
        "/value\\\\/",
        "operator"
      ],
      [
        "/range\\\\/",
        "operator"
      ],
      [
        "/query\\\\/",
        "operator"
      ],
      [
        "/terms\\\\/",
        "operator"
      ],
      [
        "/term\\\\/",
        "operator"
      ],
      [
        "/bool\\\\/",
        "operator"
      ],
      [
        "/must\\\\/",
        "operator"
      ],
      [
        "/aggs\\\\/",
        "operator"
      ],
      [
        "/path\\\\/",
        "operator"
      ],
      [
        "/avg\\\\/",
        "operator"
      ],
      [
        "/gte\\\\/",
        "operator"
      ],
      [
        "/min\\\\/",
        "operator"
      ],
      [
        "/max\\\\/",
        "operator"
      ],
      [
        "/AND\\\\/",
        "operator"
      ],
      [
        "/sum\\\\/",
        "operator"
      ],
      [
        "/lte\\\\/",
        "operator"
      ],
      [
        "/and\\\\/",
        "operator"
      ],
      [
        "/or\\\\/",
        "operator"
      ],
      [
        "/OR\\\\/",
        "operator"
      ],
      [
        "/lt\\\\/",
        "operator"
      ],
      [
        "/gt\\\\/",
        "operator"
      ],
      [
        "/\\ \\|\\ /",
        "operator"
      ],
      [
        "/\\ \\(/",
        "operator"
      ],
      [
        "/\\ \\[/",
        "operator"
      ],
      [
        "/\\]\\*/",
        "operator"
      ],
      [
        "/\\\\/",
        "operator"
      ],
      [
        "/\\{/",
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
export const elasticsearchLanguageConfig = {
  "brackets": [
    [
      "{",
      "}"
    ]
  ],
  "autoClosingPairs": [
    {
      "open": "{",
      "close": "}"
    }
  ],
  "surroundingPairs": [
    {
      "open": "{",
      "close": "}"
    }
  ]
};
// Register with Monaco Editor
export function registerElasticsearchLanguage(monaco: any) {
  monaco.languages.register({ id: 'elasticsearch' });
  monaco.languages.setMonarchTokensProvider('elasticsearch', elasticsearchLanguage);
  monaco.languages.setLanguageConfiguration('elasticsearch', elasticsearchLanguageConfig);
}
