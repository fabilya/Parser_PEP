# Проект парсинга PEP
## Contents
- [Description](#description)
- [Technologies](#technologies)
- [Start project](#how-to-start-a-project)
    - [Built-in methods](#built-in-methods)
    - [Arguments](#arguments)
- [Author](#author)
### Description
The parser collects data about all PEP documents, compares statuses and writes them to a file, it also collects information about the status of versions, downloads an archive with documentation and collects links about news in Python, logs its work and errors into the command line and a log file.
Before use
### Technologies
- Python 
- BeautifulSoup4
- Prettytable

### How to start a project
- Clone the repository to your computer using the commands:
```
git clone git@github.com:fabilya/bs4_parser_pep.git
```
- In the root folder, create a virtual environment and install dependencies.
```
python -m venv venv
pip install -r requirements.txt
```
- Change the directory to the src/ folder
- Run the main.py file by selecting the required parser and arguments (given below)

`python main.py [parser option] [arguments]`

### Built-in methods

`whats-new` - parser that displays a list of changes in python.
`latest_versions` -a parser that displays a list of python versions and links to their documentation.
`download` - parser downloading a zip archive with python documentation in pdf format.
`pep` - a parser that displays a list of pep document statuses and the number of documents in each status.

### Arguments
It is possible to specify arguments to change the operation of the program:

`-h, --help` - general information about commands
`python main.py -h`
`-c, --clear-cache` - clearing the cache before parsing
`-o {pretty,file}, --output {pretty,file}` - additional data output methods
`pretty` - displays data on the command line in a table
`file` - saves information in csv format in the results/ folder

### Author
[Ilya Fabiyanskiy](https://github.com/fabilya)

