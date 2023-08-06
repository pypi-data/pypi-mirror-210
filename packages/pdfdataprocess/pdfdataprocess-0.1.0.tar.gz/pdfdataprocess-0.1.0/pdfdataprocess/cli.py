from pathlib import Path
from nodejs import node, npm, npx
import typer

from .process import processJSON

app = typer.Typer(
    name = "pdf-dataset-process",
    help = "Process a PDF dataset to a JSONL file.",
    no_args_is_help=True
)

@app.command("init", help="Initialize the project.")
def init():
    """
    Initialize the project.
    """
    npm.call(['i', 'pdf2json'])
    
    
@app.command("mkjson", help="Process a PDF dataset to a JSONL file.")
def mkjson(
    file: str = typer.Option(None, '-f', '--file')
    ):
    """
    Process a PDF dataset to a JSONL file.
    """
    firstPDF = next(Path().cwd().glob("*.pdf"), None)
    if firstPDF:
        typer.echo(f"Processing {firstPDF}")
    elif file:
        typer.echo(f"Processing {file}")
        firstPDF = file
    else:
        typer.echo("No PDF files found.")
    
    if firstPDF:
        path = Path(firstPDF).resolve()
        npx.call(['pdf2json', str(path), path.with_suffix('.json')])
        
    else:
        typer.echo("No PDF files found.")
    
@app.command("process-json", help="Process a PDF converted to JSON to produce a flat dataset.")
@app.command("pjson", help="Process a PDF converted to JSON to produce a flat dataset. Alias of `process-json`")
def doprocess(
    file: str = typer.Option(None, '-f', '--file')
    ):
    firstJSON = next(Path().cwd().glob("*.json"), None)
    if firstJSON:
        typer.echo(f"Processing {firstJSON}")
    elif file:
        typer.echo(f"Processing {file}")
        firstJSON = file
    else:
        typer.echo("No JSON-PDF files found.")
        typer.Exit(1)
    processJSON(firstJSON)
    