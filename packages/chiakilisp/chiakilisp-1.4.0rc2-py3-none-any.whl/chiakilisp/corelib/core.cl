;; this file is the ChiakiLisp core library, feel free to contribute
;; to omit loading this file append --coreless option to interpreter

(import json)
(import functools)          ;; <- import functools module for reduce
(def reduce
     functools/reduce)

(import chiakilisp.proxies.keyword)  ;; `keyword?` function requires

(import chiakilisp.lexer)
(import chiakilisp.parser)
(import chiakilisp.runtime)  ;; <- import ChiakiLisp module for eval

(defn slurp                  ;; <- read file and return its contents
  (path)
    (-> path (open "r") (.read)))

(defn slurp-json             ;; <- read json, and return parsed data
  (path)
    (-> path (open "r") json/load))

(defn identity (x)           ;; I.e.: (identity "foo") returns "foo"
  x)

(defn constantly (x)         ;; I.e.: returns a function returning x
  (fn () x))

(defn inc (x)                ;; Increments number by 1
  (+ x 1))
(defn dec (x)                ;; Decrements number by 1
  (- x 1))
(defn odd? (x)               ;; Returns true if number is odd
  (not (even? x)))
(defn even? (x)              ;; Returns true if number is even
  (= (mod x 2) 0))
(defn zero? (x)              ;; Returns true if number is equal to 0
  (= x 0))
(defn positive? (x)          ;; Returns true if number higher than 0
  (> x 0))

(defn nil? (x)               ;; Returns true if 'x' is a NoneType
  (= x nil))
(defn int? (x)               ;; Returns true if 'x' is an integer
  (isinstance x int))
(defn set? (x)               ;; Returns true if 'x' is a set
  (isinstance x set))
(defn str? (x)               ;; Returns true if 'x' is a string
  (and (not (keyword? x))
       (isinstance x str)))
(defn list? (x)              ;; Returns true if 'x' is a list
  (isinstance x list))
(defn dict? (x)              ;; Returns true if 'x' is a dictionary
  (isinstance x dict))
(defn bool? (x)              ;; Returns true if 'x' is a boolean
  (isinstance x bool))
(defn float? (x)             ;; Returns true if 'x' is a float number
  (isinstance x float))
(defn tuple? (x)             ;; Returns true if 'x' is a tuple
  (isinstance x tuple))
(defn keyword? (x)           ;; Returns true if 'x' is a keyword
  (isinstance x keyword/Keyword))

(defn not (x)                ;; Returns inverted boolean presentation
  (if x false true))

(defn = (first second)       ;; Returns whether both items do equal
  (.__eq__ first second))
(defn < (first second)       ;; Returns whether first item is less
  (.__lt__ first second))
(defn > (first second)       ;; Returns whether first item is greater
  (.__gt__ first second))
(defn <= (first second)      ;; Returns true if first item is less
  (.__le__ first second))    ;;                            or greater
(defn >= (first second)      ;; Returns true if first item is greater
  (.__ge__ first second))    ;;                               or less

(defn count (x)
  (.__len__ x))              ;; Returns a count of a collection items

(defn collection? (coll)     ;; Returns true if x conforms collection
  (or
    (str? coll) (set? coll) (list? coll) (dict? coll) (tuple? coll)))

(defn contains? (coll item)  ;; Whether collection contains the item?
  (when (collection? coll)
    (.__contains__ coll item)))

(defn get (& args)           ;; Safely get the item from a collection
 ; hint for the future: could not use destructuring in `get` function
 (when (>= (count args) 2)
  (let (coll (.__getitem__ args 0)
        item (.__getitem__ args 1))
   (cond (= 2 (count args)) (get coll item nil)
         (= 3 (count args))
         (let (default   (.__getitem__ args 2))
          (cond (set? coll) (when (contains? coll item) item)
                (and (or (str? coll) (list? coll) (tuple? coll))
                     (int? item))
                (try (.__getitem__ coll item)
                  (catch IndexError _ default))
                (dict? coll) (try (.__getitem__ coll item)
                                   (catch KeyError __ default))))))))

(defn first (coll)                 ;; Returns a first collection item
 (when (or (list? coll) (tuple? coll) (str? coll))
  (get coll 0)))
(defn second (coll)               ;; Returns a second collection item
 (when (or (list? coll) (tuple? coll) (str? coll))
  (get coll 1)))
(defn third (coll)                ;; Returns a third collection item
 (when (or (list? coll) (tuple? coll) (str? coll))
  (get coll 2)))
(defn last (coll)                 ;; Returns the last collection item
 (when (or (list? coll) (tuple? coll) (str? coll))
  (get coll -1))))

(defn rest (coll)                 ;; Returns the rest of a collection
 (when (and coll
            (or (list? coll)
                (tuple? coll)))
  (let (cast (cond (list? coll) list
                   (tuple? coll) tuple)   ;; preserve collection type
        new  (list coll)
        rev  (-> new reversed list))
   (.pop rev)
   (-> rev reversed cast))))

(defn get-in (& args)        ;; Goes through full path to get an item
 (when args
  (let ((coll path default) args)
        (cond (>= (count args) 2)
              (functools/reduce (fn (acc n)
                                  (get acc n default)) path coll)))))

(defn assoc                  ;; Behaves the same as assoc in Clojure
 (collection key value)
 (cond (and (int? key) (list? collection))
       (let (new (list collection))
        (.__setitem__ new key value) new)
       (and (int? key) (tuple? collection)
       (let (new (list collection))
        (.__setitem__ new key value) (tuple new))
       (dict? collection)
       (let (new (dict collection)) (.update new {key value}) new))))

(defn conj (& args)          ;; Behaves the same as conj from Clojure
 (when args
  (if (= 1 (count args))
   (first args)
   (let (coll (first args)
         items (rest args))
    (cond (set? coll)
          (let (new (list coll)) (.extend new items) (set new))
          (list? coll)
          (let (new (list coll)) (.extend new items) new)
          (tuple? coll)
          (let (new (list coll)) (.extend new items) (tuple new))
          (dict? coll)
          (let (new (dict coll)) (functools/reduce (fn (acc new)
                                                    (.update acc new)
                                                    acc)
                                  items new)))))))

(defn into (to from)         ;; Behaves the same as into from Clojure
 (reduce conj to from))

(defn juxt (& functions)     ;; Behaves the same as juxt from Clojure
 (fn (x) (map (fn (f) (f x)) functions)))

(defn select-keys (coll keys)  ;; Returns key-value pairs from a dict
 (when (and (dict? coll) (or (list? keys) (tuple? keys) (set? keys)))
  (->> coll
       (.items)
       (filter (fn (keyword-pair)
                 (let ((key __) keyword-pair) (contains? keys key))))
       dict)))

(defn eval (source)            ;; Evaluates ChiakiLisp piece of code.
 (let (lexer   (lexer/Lexer source "<eval>")
       _       (.lex lexer)
       parser  (parser/Parser (.tokens lexer))
       _       (.parse parser)
       environ {}
       _       (.update environ runtime/ENVIRONMENT))
  (->> (.wood parser)
       (map (fn (an-expression) (.execute an-expression environ))))))
