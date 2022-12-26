# L'intèrpret de funcions Funx

## Presentació del llenguatge

Funx és un llenguatge de programació orientat a expressions i funcions. Amb 
Funx podem definir funcions i acabar, opcionalment, amb una expressió.

A l'exemple següent es mostra una expressió final:

```
# expressions:

3 + 4 * 2
```

```
Out: 11
```

Com podeu veure, no es defineix cap funció i els comentaris es troben després
del símbol `#`. La sortida de l'intèrpret és el resultat de l'avaluació de 
l'expressió.

En Funx no podem definir programes, només funcions i una expressió final. Podem 
definir la llista de funcions sense que importi l'ordre.

Cada funció té un nom, paràmetres i un bloc associat. Els blocs es troben 
inscrits entre els símbols `{` i `}`.

Les funcions han de començar per una lletra majúscula. Les variables, en canvi, 
comencen amb una lletra minúscula.

Les funcions passen els paràmetres per còpia. Retornen el valor de qualsevol 
expressió que trobin en el seu bloc i en aquell precís instant. A continuació 
en teniu un exemple:

```
# funció que rep dos nombres enters i en torna la seva suma
Suma x y
{
  x + y
}

Suma (2 * 3) 4 
```

```
Out: 10
```

Això implica que si trobem més d'una expressió en una funció, tindrem més d'un punt de 
sortida de la funció. 

Com no podia ser d'altra manera, el llenguatge de programació Funx compta amb 
recursivitat. 

Mireu l'exemple següent:

```
Fibo n
{
    if n < 2 { n }
    (Fibo n-1) + (Fibo n-2)
}

Fibo 4
```

```
Out: 3
```

Les variables són locals a cada invocació de cada funció i les funcions es 
poden comunicar a través de paràmetres. Les funcions llisten els noms dels seus
paràmetres formals, però no inclouen els seus tipus. Els paràmetres es separen
amb blancs, com en Haskell.

Mireu l'exemple següent:

```
# funció que rep dos enters i en torna el seu maxim comu divisor

Euclides a b
{
  while a != b
  {
    if a > b 
    {
      a <- a - b
    }
    else
    {
      b <- b - a
    }
  }
  a
}

Euclides 6 8
```

```
Out: 2
```

Les variables no han de ser declarades, totes seran de tipus enter. No 
existeixen operacions de lectura ni d'escriptura.

L'operador de comparació per igualtat és `=` i per diferència és `!=`. 
L'assignació es fa amb la instrucció `<-`.

Les funcions poden no tenir paràmetres. 
Podem definir d'aquesta forma funcions constants:

Exemple:
  
```
DOS { 2 }
Suma2 x { DOS + x }
Suma2 3
```

```
Out: 5
``` 

Si una funció no té cap expressió no tornarà res.

# Especificació de Funx

Les instruccions de Funx són:

- l'assignació amb `<-`,
- la invocació de funcions,
- el condicional amb `if` i potser `else`,
- la iteració amb `while`,

Les instruccions escrites una rera l'altra s'executen seqüencialment.

## Assignació

L'assignació ha d'avaluar primer l'expressió a la part dreta del `<-` i 
emmagatzemar després el resultat a la variable local a la part esquerra. 

Exemple: `a <- a - b`. 

Fixeu-vos en que l'assignació no retorna res. 

## Condicional

La instrucció condicional té la semàntica habitual. El bloc del sinó és optatiu.

Exemples: `if x = y { z <- 1 }` i `if x = y { z <- 1 } else { z <- 2 }`. 

Fixeu-vos que els limitadors dels blocs sempre són obligatoris (tant als 
condicionals com als procediments i als `while`s).

Si la condició avaludada és buida (per exemple una crida a una funció que no retorna res)
s'interpreta com una condició falsa.

Com s'explica també a l'apartat d'extensions, també es pot utilitzar la
construcció `else if` per afegir condicions addicionals.

## Iteració amb `while`

La instrucció iterativa amb `while` té la semàntica habitual. 

Exemple: `while a > 0 { a <- a / 2 }`.

## Invocació de funció

La crida a una funció té la semàntica habitual.
Si el nombre de paràmetres passats no corresponen als declarats, es produeix un 
error. Les funcions es poden cridar recursivament. La sintàxi és sense parèntesis ni comes.

Exemple: `Suma x + y 2`.

## Expressions

Si una variable encara no ha rebut cap valor, el seu valor és zero. Els
operadors aritmètics són els habituals (`+`, `-`, `*`, `/`, `%`) i amb la
mateixa prioritat que en C. Evidentment, es poden usar parèntesis. Tots els
operadors aritmètics són d'enters, inclosa la divisió. 

El operadors relacionals (`=`, `!=`, `<`, `>`, `<=`, `>=`) retornen zero per fals i u per
cert.

## Àmbit de visibilitat

No importa l'ordre de declaració de les funcions. Les variables són locals a
cada invocació de cada procediment. No hi ha variables globals ni manera
d'accedir a variables d'altres procediments (només a través dels paràmetres).

A més, com s'explica a l'apartat d'extensions també es poden declarar funcions
aniudaes dins les altres de forma que només siguin visibles per aquestes.

## Errors i excepcions

Els errors que poden saltar durant l'execució són:
- `UndefinedFunction` quan s'intenta cridar una funció no definida
- `RedefinedFunction` quan s'intenta definir una funció ja definida
- `InvalidOperand` quan algun operand és buit en alguna expressió (es llença en crides a funcions, operadors no lògics i assignacions)
- `InvalidParams` quan el nombre de paràmetres en la crida a una funció no coincideix amb la definició
- `RepeatedParams` quan es repeteixen noms de paràmetres en la definició d'una funció
- `ZeroDivision` quan s'intenta dividir entre 0
- `SyntaxError` quan hi ha algun error de sintaxi

## Comentaris sobre la sintaxi

Una expressió s'ha de trobar sobre una mateixa línia i dues expressions
dins del mateix bloc han d'anar separades per (com a mínim) un salt de línia.

Els espais en blanc s'ignoren llevat de les següents situacions:
- Paràmetres en les declaracions i crides a funcions `F x y`
- Després de les sentències `if`, `else if` i `while`

Les condicions que segueixen a `if` i `while` s'han de trobar també sobre la mateixa línia.
Observem que en un `else if` les dues paraules clau poden anar separades tant per salts de línia
com per espais en blanc.

## Invocació de l'intèrpret

L'intèrpret s'ha d'invocar amb les comandes:

```bash
export FLASK_APP=funx
flask run
```

També es pot interpretar un arxiu:
```
python3 funx_interpreter.py file.funx
```

## Extensions

S'han implementat 3 extensions:
- Condicions addicionals amb `else if`, per exemple: `if a = 0 {10} else if a = 1 {11}`
- Definició de funcions aniuades que només siguin visibles dins la funció on es defineixen
- Operadors lògics `&&`, `||` i `!` (únics operadors que permeten aplicar-se a una expressió buida, que s'interpreta com falsa)
