# ```refex```

The refexence Extractor is a command-line interface (CLI) application that uses [refextract](https://github.com/inspirehep/refextract) to extract references from a PDF file. The PDF file can be open on Okular or provided as a file path or URL.

## Instalation

```
pip install refextract-cli
```

## Usage

When provided no source, it looks for an Okular instance and process the current PDF.
```bash
refex
```

For generating Google Scholar search links and sort the results, use:
```bash
refex -g --sort year
```

If rofi is available, you can use:
```bash
refex --rofi
```


