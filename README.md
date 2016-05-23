# Kevro/Barron Styleguide
Building this project requires:
- Node 5.9.1 and NPM 3.7.3
- [Node Version Manager](https://github.com/creationix/nvm)
- Django 1.8.6
- Python 2.7.11
- [Virtualenv](https://github.com/pypa/virtualenv)

## Setup
Once you have cloned the repo, run `$ nvm install && nvm use` to use the project's required Node version.

Next, run `$ npm run install-project` and `$ npm run build`, which will install all dependencies and build the project into usable code.

Go ahead and get a cup of coffee, this is going to take a while. (We have bundled all the dependencies that would normally be global as part of the project's node_modules.)

## Build Tasks
### Running the Dev Server
Run `$ npm run start-server`, which will activate the Python virtualenv and start the server on *port 8000*.

### Watch Tasks
Run `$ npm run barron-webpack-watch` and `$ npm run barron-gulp-watch` and assets will rebuild as you code.

### Other Tasks
Look at the scripts section of *package.json* for a comprehensive list of tasks that this project uses. The ones above should be adequate as a starting point, but there are also specific commands for building production code.

## Creating Patterns in Mote
Run `$ gulp genpattern --project='projectname' --patternCat='patterncategory' --patternName='patternname'` to create a new pattern quickly with some boilerplate.

*NB.* This _will_ require a global installation of Gulp to work. `$ npm install -g gulp`

## Tooling
There are plenty of small libraries and tools we're using, but the core ones are listed below.
### Dependency Management
- NPM (Build related dependencies)
- Bower (Client-side related dependencies)

### Build
- Webpack
- Gulp
- Node LibSass
- Babel

### Linting
- Eslint
- SassLint

It is important that you have Eslint and SassLint installed globally and ideally integrated with your IDE. However, there will also be warnings in the console during the build.

*It is vital that we have a consistent coding style, so please adhere to the linters' warnings.*

### Client-Side
#### SASS
- Modular Scale [http://www.modularscale.com/?14,26&px&1.618&sass&text]
- BreakpointSass
- Bourbon
- Susy

#### JavaScript
- Modernizr
- Conditionizr
- jQuery
- Lodash
