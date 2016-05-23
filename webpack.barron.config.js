const Webpack = require('webpack'),
    Path = require('path'),
    Autoprefixer = require('autoprefixer'),
    CssNano = require('cssnano'),
    CleanWebpackPlugin = require('clean-webpack-plugin'),
    BundleTracker = require('webpack-bundle-tracker'),
    SassJsonImporter = require('node-sass-json-importer'),
    CopyWebpackPlugin = require('copy-webpack-plugin');

var projectDirectory = './projects/barron/website';
var modulesDirectories = ['./node_modules/', './bower_components/'];
var excludes = /(node_modules|bower_components|mote)/;

var definePlugin = new Webpack.DefinePlugin({
    '__DEV__': JSON.stringify(JSON.parse(process.env.BUILD_DEV || 'true')),
    '__PRERELEASE__': JSON.stringify(JSON.parse(process.env.BUILD_PRERELEASE || 'false'))
});

module.exports = {
    'target': 'web',
    'context': __dirname,
    'resolve': {
        'modulesDirectories': modulesDirectories,
        'extensions': [
            '',
            '.js',
            '.css',
            '.scss',
            '.sass',
            '.json'
        ]
    },
    'entry': {
        'main': [projectDirectory + '/src/main.js'],
        'test-suite': [projectDirectory + '/src/test-suite.js']
    },
    'output': {
        'path': projectDirectory + '/dist/js',
        'filename': '[name]-bundle.js',
        'publicPath': '/static/barron/website/dist/js/',
        'chunkFilename': 'chunk-[name]-[chunkhash].js'
    },
    'module': {
        'loaders': [
            {
                'test': /\.css$/,
                'loader': 'style?singleton!css?sourceMap!postcss-loader',
                'excludes': excludes
            },
            {
                'test': /\.(png|jpg)/,
                'loader': 'url?limit=100000',
            },
            {
                'test': /\.s[a|c]ss$/,
                'loader': 'style?singleton!css?sourceMap!postcss-loader!sass?sourceMap!sasslint',
                'exclude': excludes
            },
            {
                'test': /\.j[s|sx]$/,
                'loader': 'babel',
                'exclude': excludes,
                'query': {
                    'cacheDirectory': true,
                    'presets': ['es2015', 'stage-0'],
                    'plugins': ['transform-runtime']
                }
            },
            // {
            //     'test': /\.js$/,
            //     'loader': 'uglify',
            //     'exclude': excludes
            // },
            {
                'test': /\.json$/,
                'loader': 'json',
                'exclude': excludes
            }
        ]
    },
    'plugins': [
        // Cleans Dist folder before compile.
        new CleanWebpackPlugin([projectDirectory + '/dist/js'], {
            'root': __dirname,
            'verbose': true,
            'dry': false
        }),
        new Webpack.ProvidePlugin({
            '$': 'jquery/dist/jquery',
            'jQuery': 'jquery/dist/jquery',
            'jquery': 'jquery/dist/jquery',
            'window.jQuery': 'jquery/dist/jquery'
        }),
        new CopyWebpackPlugin([
                // {output}/to/file.txt
                { 'from': projectDirectory + '/src/custom.js', 'to': 'custom.js' }
        ]),
        definePlugin
    ],
    'postcss': function() {
        return [Autoprefixer({
            'browsers': ['> 1%', 'IE 7', 'IE 8', 'IE 9']
        }), CssNano];
    },
    'sasslint': {
        'configFile': __dirname + '/.sass-lint.yml'
    },
    'sassLoader': {
        'precision': 3,
        'indentWidth': 4,
        'includePaths': modulesDirectories,
        'importer': SassJsonImporter
    },
    'uglify-loader': {
        'mangle': false
    }
}
