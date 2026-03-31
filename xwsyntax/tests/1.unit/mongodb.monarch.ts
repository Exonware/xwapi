// mongodb.monarch.ts
// Auto-generated Monaco language definition
export const mongodbLanguage = {
  "defaultToken": "",
  "tokenPostfix": ".mongodb",
  "keywords": [
    "Date",
    "ISODate",
    "ObjectId",
    "aggregate",
    "countDocuments",
    "db",
    "deleteMany",
    "deleteOne",
    "false",
    "find",
    "insertMany",
    "insertOne",
    "new",
    "null",
    "project",
    "replaceOne",
    "true",
    "updateMany",
    "updateOne"
  ],
  "operators": [
    "$addFields",
    "$addToSet",
    "$all",
    "$and",
    "$bucket",
    "$count",
    "$elemMatch",
    "$eq",
    "$exists",
    "$facet",
    "$graphLookup",
    "$group",
    "$gt",
    "$gte",
    "$in",
    "$inc",
    "$limit",
    "$lookup",
    "$lt",
    "$lte",
    "$match",
    "$mul",
    "$ne",
    "$nin",
    "$nor",
    "$not",
    "$or",
    "$pop",
    "$project",
    "$pull",
    "$push",
    "$regex",
    "$rename",
    "$replaceRoot",
    "$set",
    "$size",
    "$skip",
    "$sort",
    "$text",
    "$type",
    "$unset",
    "$unwind",
    "$where",
    "(",
    ")",
    ",",
    ".",
    "/ | /",
    "0",
    "1",
    ":",
    "[",
    "[^",
    "]",
    "]*",
    "{",
    "}"
  ],
  "symbols": "\\$all|\\$facet|\\$project|\\$nor|\\$set|\\]|\\$not|\\$limit|\\$push|\\$ne|\\$group|\\$unset|\\[\\^|\\$where|\\$count|\\(|\\$pop|1|\\$pull|\\$graphLookup|\\$and|\\$size|\\$unwind|,|\\$or|\\[|\\$exists|\\}|\\$addToSet|\\$type|\\$nin|\\$lt|\\$replaceRoot|\\$match|\\$gte|/\\ \\|\\ /|\\$text|\\$elemMatch|\\{|\\$mul|\\$rename|\\$regex|\\$sort|\\$lte|\\)|\\.|\\$in|0|\\$addFields|\\$eq|\\$inc|\\$gt|\\$bucket|\\$lookup|:|\\$skip|\\]\\*",
  "brackets": [
    {
      "open": "(",
      "close": ")",
      "token": "delimiter.parenthesis"
    },
    {
      "open": "[",
      "close": "]",
      "token": "delimiter.square"
    },
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
        "/\\$graphLookup/",
        "operator"
      ],
      [
        "/\\$replaceRoot/",
        "operator"
      ],
      [
        "/\\$elemMatch/",
        "operator"
      ],
      [
        "/\\$addFields/",
        "operator"
      ],
      [
        "/\\$addToSet/",
        "operator"
      ],
      [
        "/\\$project/",
        "operator"
      ],
      [
        "/\\$unwind/",
        "operator"
      ],
      [
        "/\\$exists/",
        "operator"
      ],
      [
        "/\\$rename/",
        "operator"
      ],
      [
        "/\\$bucket/",
        "operator"
      ],
      [
        "/\\$lookup/",
        "operator"
      ],
      [
        "/\\$facet/",
        "operator"
      ],
      [
        "/\\$limit/",
        "operator"
      ],
      [
        "/\\$group/",
        "operator"
      ],
      [
        "/\\$unset/",
        "operator"
      ],
      [
        "/\\$where/",
        "operator"
      ],
      [
        "/\\$count/",
        "operator"
      ],
      [
        "/\\$match/",
        "operator"
      ],
      [
        "/\\$regex/",
        "operator"
      ],
      [
        "/\\$push/",
        "operator"
      ],
      [
        "/\\$pull/",
        "operator"
      ],
      [
        "/\\$size/",
        "operator"
      ],
      [
        "/\\$type/",
        "operator"
      ],
      [
        "//\\ \\|\\ //",
        "operator"
      ],
      [
        "/\\$text/",
        "operator"
      ],
      [
        "/\\$sort/",
        "operator"
      ],
      [
        "/\\$skip/",
        "operator"
      ],
      [
        "/\\$all/",
        "operator"
      ],
      [
        "/\\$nor/",
        "operator"
      ],
      [
        "/\\$set/",
        "operator"
      ],
      [
        "/\\$not/",
        "operator"
      ],
      [
        "/\\$pop/",
        "operator"
      ],
      [
        "/\\$and/",
        "operator"
      ],
      [
        "/\\$nin/",
        "operator"
      ],
      [
        "/\\$gte/",
        "operator"
      ],
      [
        "/\\$mul/",
        "operator"
      ],
      [
        "/\\$lte/",
        "operator"
      ],
      [
        "/\\$inc/",
        "operator"
      ],
      [
        "/\\$ne/",
        "operator"
      ],
      [
        "/\\$or/",
        "operator"
      ],
      [
        "/\\$lt/",
        "operator"
      ],
      [
        "/\\$in/",
        "operator"
      ],
      [
        "/\\$eq/",
        "operator"
      ],
      [
        "/\\$gt/",
        "operator"
      ],
      [
        "/\\[\\^/",
        "operator"
      ],
      [
        "/\\]\\*/",
        "operator"
      ],
      [
        "/\\]/",
        "operator"
      ],
      [
        "/\\(/",
        "operator"
      ],
      [
        "/1/",
        "operator"
      ],
      [
        "/,/",
        "operator"
      ],
      [
        "/\\[/",
        "operator"
      ],
      [
        "/\\}/",
        "operator"
      ],
      [
        "/\\{/",
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
        "/0/",
        "operator"
      ],
      [
        "/:/",
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
export const mongodbLanguageConfig = {
  "brackets": [
    [
      "(",
      ")"
    ],
    [
      "[",
      "]"
    ],
    [
      "{",
      "}"
    ]
  ],
  "autoClosingPairs": [
    {
      "open": "(",
      "close": ")"
    },
    {
      "open": "[",
      "close": "]"
    },
    {
      "open": "{",
      "close": "}"
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
      "open": "[",
      "close": "]"
    },
    {
      "open": "{",
      "close": "}"
    },
    {
      "open": "'",
      "close": "'"
    }
  ]
};
// Register with Monaco Editor
export function registerMongodbLanguage(monaco: any) {
  monaco.languages.register({ id: 'mongodb' });
  monaco.languages.setMonarchTokensProvider('mongodb', mongodbLanguage);
  monaco.languages.setLanguageConfiguration('mongodb', mongodbLanguageConfig);
}
