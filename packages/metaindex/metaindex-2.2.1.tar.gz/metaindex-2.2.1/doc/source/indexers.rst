Indexers
========

To see all available indexers, run ``metaindex --list``. None of the
built-in indexers require or have any configuration options except for the
``rule-based`` indexer.

Some indexers might have special features though.

Sidecar files, for example, can override otherwise detected values (see above).


OCR indexing and sidecar files
------------------------------

If OCR (optical character recognition) is enabled, you may give the OCR software
a hint about the language of the document that it will process by adding a ``language``
metadata tag to the sidecar file.

For example, suppose you have scanned a contract ``contract.jpg`` that’s in dutch,
you might create a sidecar file ``contract.json`` with the ``language`` field set
to the dutch language code::

  {
    'language': 'nld'
  }

You can also provide more language tags, as long as one of them is the
`ISO 639 <https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes>`_ code
(two or three letters) of the language you want (for example, for dutch
all codes work: ``nld``, ``dut``, and ``nl``)::

  {
    'language': [
      'dutch',
      'nld'
    ]
  }

If you have the option for YAML sidecar files, these work too, of course::

  language:
    - dutch
    - nl

This feature is subject to what languages your OCR actually understands, of course.
If you don’t have a maori language packet, you can still specify the language as
``mao``, but the OCR won’t work as expected.


Rule Based Indexer
------------------

The rule based indexer is used to determine metadata tags from the fulltext
of an indexed document. For example a scanned bill might contain a date or
transaction number. Or a PDF document might contain an account number.

To function at all the rule based indexer requires that the
``ocr.fulltext`` metadata tag contains the fulltext of the document.
That means you will have to enable the ``fulltext`` configuration option.
The ``ocr`` configuration option is also required if you wish to run this
indexer on images (e.g. scanned documents).

Example
~~~~~~~

Suppose the full text of such a scanned document looks like this::

    Invoice #12345

    2012-04-13

    Big Corp Inc.   Your Money Is Our Future


    Dear customer,
    Thank you for ordering at Big Corp. Please pay us now this ridiculous
    amount of money by 2012-05-30: $500.20.

    Thanks,
     Big Corp CEO Whatstheirname

You could write a rule file like below and save it as ``big-corp.txt``::

    match /Big Corp Inc/ and /Invoice/
      set date /([0-9]{4}-[01][0-9]-[0-3][0-9])/
      set invoicenr /Invoice #([0-9]+)/
      set issuer "Big Corp Inc."
      final

See below for the full syntax of a rule file.

Now you tell metaindex about the rule file by adding it to your
configuration file::

    # snippet of the metaindex configuration file
    [Indexer:rule-based]
    some-rules = ~/big-corp.txt

You will have to provide the full path to the rule file, otherwise
metaindexer will likely not find it.

Now you are ready to go! Next time you run the metaindexer, it will add the
``issuer`` and ``invoicenr`` to the meta data of the scanned document
automatically.


Common patterns
~~~~~~~~~~~~~~~

When working with scanned documents, don’t rely on spaces being just one space character.
To find "Big Corp", don’t just match ``/big corp/i``, but instead assume that there can be
many spaces between the two words::

    match /big[\s]+corp/i
        set issuer "Big Corp Inc."


When matching dates, various documents can use various styles of writing dates. To correct
their mistakes, it's a common pattern to match for the day, month, and year parts separately.
Here is an example of how to turn a ``MM/DD/YYYY`` style date into ``YYYY-MM-DD``::

    find day /[\s]+[01][0-9].([0-2][0-9]).[0-9]{4}[\s]+/
    find month /[\s]+([01][0-9]).[0-2][0-9].[0-9]{4}[\s]+/
    find year /[\s]+[01][0-9].[0-2][0-9].([0-9]{4})[\s]+/
    set date {year}-{month}-{day}

Note that the regular expression is not actually looking for the ``/``, but accepts any
character as a separator.

Also, the date is expected to be surrounded by at least one white space character.


Rule File Syntax
~~~~~~~~~~~~~~~~

A rule file is a plain text file. Empty lines and lines starting with ``#`` or
``;`` are ignored::

    # a comment in a rule file
    ; another comment

    # the line above is also ignored, because it's empty


Match Directives
^^^^^^^^^^^^^^^^

Rules are guarded by match directives that define whether or not a set of
rules should apply to a document. A match directive is started with the
keyword ``match`` followed by one or more regular expressions, optionally
separated by ``and`` for readability::

    # Examples of match directives

    # matches a document that has "Big Corp" in its fulltext
    match /Big Corp/
    
    # matches a document that has the words "Big" and "Corp" in it,
    # but not only "Big Corp"
    match /Big/ and /Corp/

    # the same as above, just without the "and"
    match /Big/ /Corp/

    # match case insensitive
    match /big corp/i

The regular expressions for ``match`` directives must be surrounded by fencing
characters. ``/`` is most commonly used, but any will do, really::

    # other fencing characters are allowed
    match "Big" and ,Corp,

Only when the regular expressions of a ``match`` directive are found in a
document, the subsequent ``set`` and ``find`` directives are applied.
``set`` and ``find`` directives are usually indented, but that’s not a
requirement, only a visual help.


Set Directives
^^^^^^^^^^^^^^

A ``set`` directive is used to set a tag for a document. It’s following the
syntax ``set <tag name> <value>``.

If the tag name contains spaces, you must surround the tag name with ``"``.

The value can be either of two things:

 1. A regular expression,
 2. A single line text.

A regular expression must be surrounded by ``/`` characters. A single line of
text can be surrounded by ``"`` characters (for example to allow for a text with
a leading ``/`` or with trailing whitespace characters)::

    # examples of valid set directives
    match /Big Corp/
      set issuer "Big Corp"
      set type Annoying invoice
      set "silly amount" /(\$[0-9]+)/

Similar to the ``match`` directive you can set regular expressions to be case
insensitive::

    # example of a case insensitive set directive
    match /Big Corp/
      set issuer /(big [a-z]+)/i

Inside single lines of text you may refer to local variables as defined by
``find`` like this::

    # example of referring to a local variable
    match /Big Corp/
      find amount /\$([0-9]+)/
      set money "{amount} USD"

You can have multiple ``set`` directives that assign a value to the same tag::

    # example of several set directives
    match /Big Corp/ and /Invoice/
      set tags invoice
      set tags /your product: ([a-z ]+)/i


Find Directives
^^^^^^^^^^^^^^^

A ``find`` directive can be used to extract parts of the fulltext into a variable
that’s local to this match directive and can be reused in ``set``.

``find`` directives have the syntax ``find <name> /<regular expression>/``.
The regular expression must be surrounded by ``/``.

Just like regular expressions in ``match`` and ``set`` directives, you can set the
regular expression here to be case insensitive by appending `i` after the last
``/``::

    # example of case insensitive find directive
    match /Big Corp/
      find issuer /(big [a-z]+)/i
      set issuer "From {issuer}"


Final Directive
^^^^^^^^^^^^^^^

It is assumed that most rules are generic and extract snippets from the
fulltext, like date, sender, receiver, or account numbers.

However, it might be that one rule is actually extracting all there is to
extract and you don't want subsequent rules to run. In that case you can
add the ``final`` directive to a match directive::

    # example of the 'final' directive
    match /Big Corp/
      set publisher "Big Corp Limited"
      final

    match /Corp/
      set publisher "Some corporation"

In this example, if the text "Big Corp" is encountered, the publisher will
be set to "Big Corp Limited" and the following rule, checking for "Corp"
will not be executed.

