# leaf-focus

Extract structured text from pdf files.

## Install

Install from PyPI using pip:

```bash
pip install leaf-focus
```

[![PyPI](https://img.shields.io/pypi/v/leaf-focus)](https://pypi.org/project/leaf-focus/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/leaf-focus)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/actions/workflow/status/anotherbyte-net/leaf-focus/test-package.yml?branch=main)](https://github.com/anotherbyte-net/leaf-focus/actions)

Download the [Xpdf command line tools](https://www.xpdfreader.com/download.html) and extract the executable files.

Provide the directory containing the executable files as `--exe-dir`.


## Usage

```text
usage: leaf-focus [-h] [--version] --exe-dir EXE_DIR [--page-images] [--ocr]
                  [--first FIRST] [--last LAST]
                  [--log-level {debug,info,warning,error,critical}]
                  input_pdf output_dir

Extract structured text from a pdf file.

positional arguments:
  input_pdf             path to the pdf file to read
  output_dir            path to the directory to save the extracted text files

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --exe-dir EXE_DIR     path to the directory containing xpdf executable files
  --page-images         save each page of the pdf as a separate image
  --ocr                 run optical character recognition on each page of the
                        pdf
  --first FIRST         the first pdf page to process
  --last LAST           the last pdf page to process
  --log-level {debug,info,warning,error,critical}
                        the log level: debug, info, warning, error, critical
```

### Examples

```bash
# Extract the pdf information and embedded text.
leaf-focus --exe-dir [path-to-xpdf-exe-dir] file.pdf file-pages

# Extract the pdf information, embedded text, an image of each page, and Optical Character Recognition results of each page.
leaf-focus --exe-dir [path-to-xpdf-exe-dir] file.pdf file-pages --ocr
```

## Dependencies

- [xpdf](https://www.xpdfreader.com/download.html)
- [keras-ocr](https://github.com/faustomorales/keras-ocr)
- [Tensorflow](https://www.tensorflow.org) (can optionally be run more efficiently [using one or more GPUs](https://www.tensorflow.org/install/pip#hardware_requirements))
