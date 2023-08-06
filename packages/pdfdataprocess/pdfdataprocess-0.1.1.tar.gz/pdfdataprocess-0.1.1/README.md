# Turning a pdf dataset into CSV

In the rare occasion where researchers publish an entire dataset written in PDF format, [such as in the case of this research paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0123920), you need a quick tool to turn that PDF into a CSV file.

## What happens under the hood

### Embeded nodejs runtime

Using the `nodejs-bin` [python node runtime](https://pypi.org/project/nodejs-bin/), we are able to call `npx` to remove execute the [pdf2json npm package](https://www.npmjs.com/package/pdf2json)

When you type

```bash
pdfdataprocess mkjson
```

The `npx` call applies on the first PDF in your directory. If not found, the path you provide to flag `-f` is considered.

### Parsing the JSON-PDF

Then a highly hacky python processing  is applied to the JSON-PDF file.

The JSON-PDF is a JSON file containing the content of the PDF.

The python script iterates through the JSON-PDF and extracts the text content of each page.

How this is done is quite simple:

- if your dataset is an actual CSV file that's printed into PDF, then on each page you will have, at same height (`top` entry), a line of different values (`left` entry changes, `data` entry should be rearranged)
- this requires a few layers of pre and post-processing 
- the final result is a CSV file with the text content of each page

## Usage

```bash
pdfdataprocess mkjson # outputs the json file
```
then

```bash
pdfdataprocess pjson # outputs the csv file
```