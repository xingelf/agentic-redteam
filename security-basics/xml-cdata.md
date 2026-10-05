---
title: "XML CDATA, Escaping, and the XXE Trap"
tags: ["security-basics", "xml", "web-security"]
---

# XML CDATA, Escaping, and the XXE Trap

**TL;DR** — CDATA is a plain-text zone in XML where `<`, `>`, and `&` need no
escaping. It is a formatting convenience, not a security boundary. The real XML
security issue sits one layer up: external entity processing (XXE). CDATA does not
cause XXE and does not protect against it — the parser configuration does.

## What CDATA is

A CDATA section tells the parser "treat this as raw text, not markup":

```xml
<!-- without CDATA: escape the specials -->
<expression>5 &lt; 10 &amp; 3 &gt; 1</expression>

<!-- with CDATA: write them directly -->
<expression><![CDATA[5 < 10 & 3 > 1]]></expression>
```

Syntax rules:

```xml
<![CDATA[ your content here ]]>
```

- Cannot nest.
- Cannot contain the literal `]]>` — split it: `...]]>` + `<![CDATA[>...`.
- Uppercase `CDATA` only.
- Whitespace and line breaks are preserved.

It is handy for embedding code or markup fragments (scripts, CSS, HTML templates)
without turning every `<` into `&lt;`.

## CDATA vs escaping

| Case | Prefer |
|---|---|
| A code or markup block with many specials | CDATA |
| A short string with one or two specials | Escaping |
| External HTML/XML fragment kept verbatim | CDATA |

Both produce the same parsed text. The choice is readability, not safety.

## The actual security issue: XXE

The dangerous part of XML is not CDATA — it is the Document Type Definition (DTD)
and external entities. A parser that resolves external entities will fetch
whatever a `SYSTEM` entity points at:

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<data>&xxe;</data>
```

If the parser expands `&xxe;`, the file's contents land in the response. The same
trick reaches internal URLs (SSRF), and blind variants exfiltrate data over
out-of-band channels. Wrapping an entity reference in CDATA does not disarm it; the
entity is resolved before CDATA matters, and relying on CDATA here gives a false
sense of safety.

XXE is OWASP territory (folded into A05:2021 Security Misconfiguration) and
catalogued as CWE-611.

## Defense

Fix the parser, not the document:

1. **Disable DTDs / external entities** — the one control that matters. Examples:
   - Java: `factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);`
   - .NET: set `XmlReaderSettings.DtdProcessing = DtdProcessing.Prohibit;`
   - libxml2: do not pass `XML_PARSE_NOENT` / `XML_PARSE_DTDLOAD`.
2. **Use a hardened parser default** — modern libraries increasingly disable
   external entities by default; confirm yours does.
3. **Validate input XML** against an expected schema.
4. **Treat CDATA content as untrusted** — if it feeds into HTML, SQL, or a shell,
   it still needs the usual output encoding or parameterization. CDATA only changes
   how XML parses the text, not what your code does with it afterward.

## Takeaway

CDATA is a text-formatting tool: use it for code and fragment blocks, escape for
short strings. It has no security role. The thing to get right in XML is parser
configuration — disable DTDs and external entities, and XXE goes away regardless
of how the document is written.
