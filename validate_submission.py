"""Validate your own submission without importing its strategy code."""
import argparse
import ast
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',nargs='?',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--starter-check',action='store_true',help='Do not require the final research_note.pdf yet')
    args=parser.parse_args()
    required=['strategy.py','README.md','requirements.txt']
    if not args.starter_check:
        required.append('research_note.pdf')
    failures=[]
    for name in required:
        if not (args.directory/name).is_file():
            failures.append('Missing '+name)
    if (args.directory/'strategy.py').is_file():
        try:
            tree=ast.parse((args.directory/'strategy.py').read_text())
            functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='generate_positions']
            if len(functions)!=1 or len(functions[0].args.args)!=2:
                failures.append('Define generate_positions(history, current_date)')
        except SyntaxError as error:
            failures.append(f'Syntax error at line {error.lineno}')
    for folder in ('src','artifacts'):
        if (args.directory/folder).exists() and any(p.is_symlink() for p in (args.directory/folder).rglob('*')):
            failures.append('Symlinks are not allowed')
    if failures:
        raise SystemExit('\n'.join(failures))
    print('Structure OK. Run the backtester for development and validation. Review the two-page PDF and final commit before submitting.')


if __name__=='__main__':
    main()
