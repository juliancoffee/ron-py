grammar Ron;

// --- Parser Rules ---

root
    : value EOF
    ;

value
    : option                    # OptionValue
    | ron_struct                # StructValue
    | ron_anon_struct           # StructValue
    | ron_map                   # MapValue
    | ron_tuple                 # TupleValue
    | ron_list                  # ListValue
    | CHAR                      # CharValue
    | STRING                    # StringValue
    | FLOAT                     # FloatValue
    | INTEGER                   # IntValue
    | BOOLEAN                   # BoolValue
    ;

// Option: Some(val) or None
option
    : SOME '(' value ')'
    | NONE
    ;

// Anon Structs: (a: 5, b: 7)
ron_anon_struct
    : IDENTIFIER? ( '(' strict_struct_body ')' )
    ;

strict_struct_body
    : named_fields
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
    : '{' (map_entry (',' map_entry)* ','?)? '}'
    ;

map_entry
    : value ':' value
    ;

// Tuples: (a, b, c)
ron_tuple
    : '(' (value (',' value)* ','?)? ')'
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

FLOAT
    : '-'? [0-9]* '.' [0-9]+ ([eE] [+-]? [0-9]+)?
    | '-'? [0-9]+ '.' ([eE] [+-]? [0-9]+)?
    | '-'? [0-9]+ [eE] [+-]? [0-9]+
    | '-'? [0-9]+ '.' [0-9]+
    ;

INTEGER
    : '-'? ( '0' | [1-9] [0-9]* )
    | '0x' [0-9a-fA-F]+
    | '0b' [01]+
    | '0o' [0-7]+
    ;

STRING
    : 'r' '######"' .*? '"######'
    | 'r' '#####"'  .*? '"#####'
    | 'r' '####"'   .*? '"####'
    | 'r' '###"'    .*? '"###'
    | 'r' '##"'     .*? '"##'
    | 'r' '#"'      .*? '"#'
    | 'r"'          .*? '"'
    | '"' ( ~["\\] | '\\' . )* '"'
    ;

// A bit more permissive, allows more than one symbol
CHAR
    : '\'' ( ~['\\] | '\\' . )* '\''
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
