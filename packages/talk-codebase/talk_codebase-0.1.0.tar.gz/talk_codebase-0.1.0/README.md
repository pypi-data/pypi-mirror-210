# talk-codebase is a powerful tool for querying and analyzing codebases

## Description

In the chat, you can ask questions about the codebase. AI will answer your questions, and if necessary, it will offer code improvements. This is very convenient when you want to quickly find something in the codebase, but don't want to waste time searching. It is also convenient when you want to improve a specific function, you can ask "How can I improve the function {function name}?" and AI will suggest improvements. Codebase is analyzed using openai.

## Installation

```bash
pip install talk-codebase
```

## Usage

talk-codebase works only with files of popular programming languages and additionally with .txt files. All other files will be ignored.
```bash
# Start chatting with your codebase
talk-codebase chat <directory>

# Configure
talk-codebase configure

# Help
talk-codebase --help
```
