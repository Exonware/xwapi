# XWJSON Query Guide

## Overview

XWJSON supports powerful query capabilities through **xwquery integration**, providing access to **30+ query formats** including SQL, JSONPath, JMESPath, Cypher, GraphQL, and more.

## Installation

For full query support, install xwquery:

```bash
pip install exonware-xwjson[full]
# or
pip install exonware-xwquery
```

## Basic Usage

### Using XWJSONDataOperations

```python
from exonware.xwjson import XWJSONSerializer
from exonware.xwjson.operations import XWJSONDataOperations

# Create operations instance
ops = XWJSONDataOperations()

# Query with SQL (auto-detected)
results = await ops.query(
    "data.xwjson",
    "SELECT name, age FROM users WHERE age > 25"
)

# Query with JSONPath
results = await ops.query(
    "data.xwjson",
    "$.users[*].name"
)

# Query with JMESPath
results = await ops.query(
    "data.xwjson",
    "users[?age > `25`].name",
    query_format="jmespath"
)

# Query with Cypher (graph queries)
results = await ops.query(
    "data.xwjson",
    "MATCH (u:User) WHERE u.age > 25 RETURN u.name",
    query_format="cypher"
)
```

## Supported Query Formats

XWJSON supports all xwquery formats (30+ formats):

### SQL-like Queries
- **SQL**: Standard SQL syntax
- **XWQuery**: Extended SQL with graph support

### Path-based Queries
- **JSONPath**: `$.users[*].name`
- **XPath**: `/users/user[@age > 25]/name`
- **JMESPath**: `users[?age > `25`].name`
- **JSONPointer**: `/users/0/name`

### Graph Queries
- **Cypher**: `MATCH (u:User) WHERE u.age > 25 RETURN u`
- **Gremlin**: `g.V().has('age', gt(25)).values('name')`
- **SPARQL**: `SELECT ?name WHERE { ?u :age ?age . FILTER(?age > 25) }`
- **GraphQL**: `{ users(where: { age_gt: 25 }) { name } }`

### Functional Queries
- **LINQ**: `from u in users where u.age > 25 select u.name`
- **JSONiq**: `for $u in $users where $u.age > 25 return $u.name`
- **jq**: `.users[] | select(.age > 25) | .name`

### And 20+ more formats...

## Advanced Queries

### Get Full ExecutionResult

```python
# Get full ExecutionResult with metadata
result = await ops.query_advanced(
    "data.xwjson",
    "SELECT * FROM users WHERE age > 25"
)

# Access results
print(result.results)  # Query results
print(result.metadata)  # Query metadata
print(result.execution_time)  # Execution time
```

### Format-Specific Queries

```python
# Explicitly specify format
results = await ops.query(
    "data.xwjson",
    "users[?age > `25`]",
    query_format="jmespath"  # Explicit format
)
```

## Fallback Behavior

If xwquery is not installed, XWJSON falls back to **jsonpath-ng** for basic JSONPath queries:

```python
# Works with or without xwquery
results = await ops.query(
    "data.xwjson",
    "$.users[*].name"  # JSONPath - always supported
)
```

## Performance

- **xwquery**: Optimized execution with format-specific optimizations
- **jsonpath-ng**: Fast JSONPath-only queries (fallback)
- **Auto-detection**: Minimal overhead for format detection

## Examples

### Complex SQL Query

```python
results = await ops.query(
    "data.xwjson",
    """
    SELECT u.name, u.age, COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.age > 25
    GROUP BY u.id
    HAVING order_count > 5
    ORDER BY order_count DESC
    """
)
```

### Graph Query

```python
results = await ops.query(
    "data.xwjson",
    """
    MATCH (u:User)-[:PURCHASED]->(p:Product)
    WHERE u.age > 25 AND p.category = 'Electronics'
    RETURN u.name, p.name, p.price
    ORDER BY p.price DESC
    LIMIT 10
    """,
    query_format="cypher"
)
```

### Filtering with JMESPath

```python
results = await ops.query(
    "data.xwjson",
    "users[?age > `25` && city == 'NYC'].{name: name, email: email}",
    query_format="jmespath"
)
```

## Integration with xwnode

XWJSON queries can leverage xwnode for graph operations:

```python
# Queries automatically use xwnode when available for graph operations
results = await ops.query(
    "data.xwjson",
    "MATCH (u:User)-[:FRIENDS_WITH]->(f:User) RETURN u, f",
    query_format="cypher"
)
```

## See Also

- [xwquery Documentation](https://github.com/exonware/xwquery) - Complete xwquery guide
- [XWJSON API Reference](REF_API.md) - Full API documentation
- [XWJSON Usage Guide](GUIDE_USAGE.md) - General usage guide
