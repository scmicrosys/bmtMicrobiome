# bmtMicrobiome
# bmtmicrobiome

### Built with

- [XCode Template](https://xcodereleases.com/

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Ensure to have the project dependencies. For this project you need to have python ^3.7 and `pip` or `poetry` (or any other dependency manager) to install the project's dependencies

### Installation

#### 1. Install the CLI package

This is a CLI, which is a program controlled from the terminal. Before beginning to use it, it is only necessary to install the Python package. The package is not (yet) distributed on pypi, therefore you will need to use the [wheel package](dist/microbiome-0.1.0-py3-none-any.whl) or the [tar package](dist/microbiome-0.1.0.tar.gz) available in the [dist](dist/) folder of this repository.

1. Create a project folder.
2. Either download the [wheel package](dist/microbiome-0.1.0-py3-none-any.whl) or [tar package](dist/microbiome-0.1.0.tar.gz) and move it to the project folder.

To install this package you can use `pip`, or any other packaging dependency management system you use, such as Anaconda or [Poetry](https://python-poetry.org/) (highly recommended!).
3. Install the package. From the project folder in which you placed the downloaded package:
```sh
pip install microbiome-0.1.0-py3-none-any.whl
```
or
```sh
poetry add ./microbiome-0.1.0-py3-none-any.whl
```

#### 2. Install and setup a PostgreSQL database

On MacOS, with [brew](https://brew.sh/):

- `brew update`
- `brew install postgres`

On Ubuntu:

- `sudo apt update`
- `sudo apt install postgresql postgresql-contrib`

Enter the PostgreSQL shell:

- `sudo -u postgres psql`
- Create username `sudo -u postgres createuser <username>`
- Create database `sudo -u postgres createdb <dbname>`
- Make the user become superuser `ALTER USER <username> WITH SUPERUSER;`
- Provide the rights to the database `GRANT ALL PRIVILEGES ON DATABASE database_name TO username;`
- Reload and restart the service: `sudo /etc/init.d/postgresql reload && sudo /etc/init.d/postgresql start`

#### 3. Install NCBI+ blast

On Ubuntu

- In depth instructions are available on the official [website](https://www.ncbi.nlm.nih.gov/books/NBK52640/)


On MacOS, with brew

- `brew install blast`


#### 4.Create folders

Within the project folder, you need to create the following necessary folders, that will be used to create the `database`, retireve the `queries` and store the `results`.

- `data`
  - `database`
  - `queries`
  - `results`


## Usage

Now that you installed the CLI, we can move on to explaining it usage.

The CLI is available by calling `microbiome` on your terminal, although this behavior might change if you installed it within a virtual environment. However, I trust that you'd know what you are doing and therefore also how to access it.

### `microbiome`: Main menu

By writing `microbiome` the following the CLI displays all the available functions and a short description of what the effect of that function will be.
![Main menu](images/main.png)

If instead, you need more information about a specific function, you can request it using `microbiome <function-name> --help`

![Function help](images/help-function.png)

### `microbiome setup`: Set variables

Before any action can be carried out, you need to setup your environemnt variables calling: `microbiome setup`

You will need to insert the path to the folder you created before and choose the names of the blast database and the PostgreSQL database. You can use the same name from the example below.

![Example setup](images/setup.png)

### `microbiome blast-create-database`: Create Blast database

Now, you can create the blast database by just typing `microbiome create-blast-database`.

**Remember**: you will need to `microbiome create-blast-database` each time you want to add new .fa files to the blast database. Lukily this process does not take too long.

The Blast database will be automatically created into the `data/database` folder you previously created.

![Example create database](images/create-db.png)

### `microbiome blast-query`: Query blast database with .fa files

Once the database is created, you can query it using other .fa files.
To do this:

1. Add one or more files to the `data/queries` folder you previously created.
2. Run `microbiome blast-query` and follow the instruction:
   1. Type `Y`(es) if you have more than one file to query, `N`(o) if you only have one file
   2. You can add an `evalue` (in the first place) and `outfmt` (in the second place) value to improve your query. This can be done in the following way: `microbiome blast-query 0.0001 2` for querying the blast database with an `evalue = 0.0001` and and `outfmt = 2`
3. The results (.xml) of the blasting will be available in the `data/results` folder.

![Example query blast](images/blast-query.png)

### `microbiome blast-parse`: Parse result and load to database

To parse the database and add the results, alongside with information about the match, the original .fa file and the .xml file created by the gapseq algorithm on that .fa file you can use `microbiome blast-parse`.

The query also can receive two additional parameters:

- `add_to_db`, will load the parsed results to the database and can be `True` or `False`. By default it is `True`.
- `top_k`, defines the number of top results to parse and to eventually add to the database. By default it is `3`.

![Example parse blast](images/blast-parse.png)

As visible in the screenshot above, the results are automatically added to the PostgreSQL database from which they can be retrieved.

The following variables are currently added to the database for each result:

- `id`, sequence, the primary key
- `full_name`, the name of the result result (ID)
- `bitscore`, the score of the match as from the blast call
- `evalue` the evalue score of the match as from the blast call
- `order_match`, the order of the match. This was created as we currently retrive the top 3 matches (but this can be configured in the `blast-parse` call)
- `query_range`, the range of the match
- `hit_range`, the hit range of the match
- `smbl_xml`, the smbl file created by gapseq
- `fasta`, the fasta file that produced the smbl
- `created`, the date of creation

