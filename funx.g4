grammar funx;

root: b=block EOF ;

block: (NEWLINE | WS)* (ins+=expr ((NEWLINE | WS)* NEWLINE (NEWLINE | WS)* ins+=expr)* (NEWLINE | WS)*)? ;

expr:   <assoc=right> op=('+'|'-') WS? e=expr #unaryOpExpr
    |   <assoc=right>'!' WS? e=expr #not
    |   left=expr WS? op=('*'|'/'|'%') WS? right=expr #opExpr
    |   left=expr WS? op=('+'|'-') WS? right=expr #opExpr
    |   left=expr WS? op=('<'|'>'|'<='|'>=') WS? right=expr #opExpr
    |   left=expr WS? op=('='|'!=') WS? right=expr #opExpr
    |   left=expr WS? '&&' WS? right=expr #and
    |   left=expr WS? '||' WS? right=expr #or
    |   atom=INT #atom
    |   '(' WS? inner=expr WS? ')' #parentExpr
    |   var=VAR #var
    |   fun=FUN (WS params+=expr)* #funcall
    |   dst=VAR WS? '<-' WS? src=expr #assignment
    |   ifb=ifblock #if
    |   'while' WS cond=expr (NEWLINE | WS)* '{' b=block '}' #while
    |   fun=FUN (WS params+=VAR)* (NEWLINE | WS)* '{' b=block '}' #fundef
    ;

ifblock: 'if' WS cond=expr (NEWLINE | WS)* '{' trueb=block '}' (NEWLINE | WS)* 'else' (NEWLINE | WS)+ elseif=ifblock #ifelseif
    |    'if' WS cond=expr (NEWLINE | WS)* '{' trueb=block '}' ((NEWLINE | WS)* 'else' (NEWLINE | WS)* '{' falseb=block '}')? #ifelse
    ;

NEWLINE : [\r\n]+ ;
WS      : [ \t]+ ;
INT     : [0-9]+ ;
VAR     : [a-z][a-zA-Z0-9_]* ;
FUN     : [A-Z][a-zA-Z0-9_]* ;
COMMENT : [#]~[\r\n]* -> channel(HIDDEN);
