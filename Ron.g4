grammar Ron;

// --- Parser Rules ---

root
    : value EOF
    ;

value
    : option                    # OptionValue
    | ron_struct                # StructValue
    | ron_map                   # MapValue
    | ron_tuple                 # TupleValue
    | ron_list                  # ListValue
    | CHAR                      # CharValue
    | STRING                    # StringValue
    | INTEGER                   # IntValue
    | FLOAT                     # FloatValue
    | BOOLEAN                   # BoolValue
    ;

// Option: Some(val) or None
option
    : SOME '(' value ')'
    | NONE
    ;

// Structs: Unit (Name), Tuple-like (Name(a, b)), Named (Name(a:1, b:2))
ron_struct
    : IDENTIFIER ( '(' struct_body? ')' )?
    ;

struct_body
    : named_fields
    | unnamed_fields
    ;

named_fields
    : named_field (',' named_field)* ','?
    ;

named_field
    : IDENTIFIER ':' value
    ;

unnamed_fields
    : value (',' value)* ','?
    ;

// Maps: { key: value, ... }
ron_map
    : '{' map_entry (',' map_entry)* ','? '}'
    ;

map_entry
    : value ':' value
    ;

// Tuples: (a, b, c)
ron_tuple
    : '(' value (',' value)* ','? ')'
    ;

// Lists/Vectors: [a, b, c] - RON uses [] for arrays/vectors
ron_list
    : '[' (value (',' value)* ','?)? ']'
    ;

// --- Lexer Rules ---

// Keywords must come BEFORE generic Identifiers to win the precedence war
SOME    : 'Some';
NONE    : 'None';
BOOLEAN : 'true' | 'false';

IDENTIFIER
    : [a-zA-Z_] [a-zA-Z0-9_]*
    | 'r#' [a-zA-Z0-9_]+  // Raw identifier support
    ;

INTEGER
    : '-'? ( '0' | [1-9] [0-9]* )
    | '0x' [0-9a-fA-F]+
    | '0b' [01]+
    | '0o' [0-7]+
    ;

FLOAT
    : '-'? [0-9]+ '.' [0-9]+
    ;

STRING
    : '"' ( ~["\\] | '\\' . )* '"'
    | 'r' '#'* '"' .*? '"' '#'* // Raw string support
    ;

CHAR
    : '\'' ( ~['\\] | '\\' . ) '\''
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;
