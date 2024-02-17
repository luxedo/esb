# ESB Boilerplates

In order to create a new boilerplate for the desired language, it's necessary to create the following structure

```
python
├── spec.json
└── template
  └── main.py
```

### `spec.json`
The `spec.json` describes how to copy the boilerplate to the destination directory.

### `template` directory
The `template` directory contains the files to be copied. In this example, it's just a python module, but it might be a full project for any language.

#### Template Tags
* `{year}`: Problem year
* `{day}`: Problem day
* `{language}`: Selected language
* `{problem_title}`: Problem title
* `{problem_url}`: Problem url
