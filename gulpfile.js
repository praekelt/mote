const gulp = require('gulp'),
    fs = require('fs'),
    path = require('path'),
    del = require('del'),
    argv = require('yargs').argv,
    runSequence = require('run-sequence'),
    sass = require('gulp-sass'),
    sassJsonImporter = require('node-sass-json-importer'),
    sassLint = require('gulp-sass-lint'),
    sourceMaps = require('gulp-sourcemaps'),
    autoprefixer = require('gulp-autoprefixer'),
    bless = require('gulp-bless'),
    pixRem = require('gulp-pixrem'),
    cssNano = require('gulp-cssnano'),
    flatten = require('gulp-flatten'),
    modernizr = require('gulp-modernizr'),
    gulpif = require('gulp-if'),
    plumber = require('gulp-plumber'),
    copy = require('gulp-copy'),
    specificity = require('gulp-specificity-graph'),
    uglify = require('gulp-uglify');

var browserSync = require('browser-sync').create();

require('gulp-grunt')(gulp);

// Environmental Variables
var targetProject = argv.project || 'barron';
var production = argv.production >= 1;

// Path Variables
var rootPath = './projects';
var srcPath = rootPath + '/' + targetProject + '/website/src';
var distPath = rootPath + '/' + targetProject + '/website/dist';

// Returns an Array of Directories in 'targetPath'
function scanFolderStructure(targetPath) {
    return fs.readdirSync(targetPath)
        .filter(function(file) {
            return fs.statSync(path.join(targetPath, file)).isDirectory();
        });
}

var patternLibraries = scanFolderStructure(rootPath);

var patternCategories = scanFolderStructure(srcPath + '/patterns');


gulp.task('default', function() {
    runSequence('styles', 'optimize-webpack-chunks', 'icons-build', 'copy-images');
});

gulp.task('rebuild', function() {
    runSequence('clean', 'styles', 'icons-build');
})

gulp.task('clean', function() {
    del(distPath);
});

gulp.task('styles', ['lint-sass', 'modernizr'], function() {
    del(distPath + '/css');

    return gulp.src(srcPath + '/**/*.s+(a|c)ss')
        .pipe(plumber())
        .pipe(sass({
            'importer': sassJsonImporter
        }).on('error', sass.logError))
        .pipe(autoprefixer({
            'browsers': ['> 1%', 'IE 9']
        }))
        .pipe(bless())
        .pipe(pixRem())
        .pipe(gulpif(production, cssNano()))
        .pipe(flatten({
            'includeParents': [0]
        }))
        .pipe(gulp.dest(distPath + '/css'))
        .pipe(browserSync.stream());
});

gulp.task('optimize-webpack-chunks', function() {
    return gulp.src(distPath + '/js/chunk-*')
        .pipe(plumber())
        .pipe(gulpif(production, uglify({
            'mangle': false
        })))
        .pipe(gulp.dest(distPath + '/js/'));
});

gulp.task('lint-sass', function() {
    return gulp.src(srcPath + '/**/*.s+(a|c)ss')
        .pipe(sassLint())
        .pipe(sassLint.format())
        .pipe(sassLint.failOnError());
});

gulp.task('modernizr', function() {
    var modernizrGlob = [
        srcPath + '/**/*.js',
        srcPath + '/**/*.s+(a|c)ss',
        '!' + srcPath + '/utils/vendor/modernizr-custom-build.js'
    ];

    return gulp.src(modernizrGlob)
        .pipe(modernizr('modernizr-custom-build.js', {
            'options': [
                'setClasses',
                'addTest',
                'html5printshiv',
                'testProp',
                'fnBind',
                'testAllProps',
                'prefixes',
                'domPrefixes',
                'prefixed',
                'testStyles',
                'hasEvent'
            ],
            'tests': [
                'mq',
                'csstransforms'
            ]
        }))
        .pipe(gulp.dest(srcPath + '/utils/vendor/'));
});

gulp.task('icons-process', function() {
    gulp.src(distPath + '/images/icons/*.css')
        .pipe(gulpif(production, cssNano()))
        .pipe(gulp.dest(distPath + '/images/icons/'));

    gulp.src(distPath + '/images/icons/element.html')
        .pipe(gulp.dest(srcPath + '/patterns/atoms/icons/'));
});

gulp.task('icons-build', function() {
    runSequence('grunt-svgmin', 'grunt-grunticon', 'icons-process');
});

// run `npm run gulp barron-sync` to run a browserSync instance of the watch task
gulp.task('browser-sync', ['styles'], function() {
    browserSync.init({
        'proxy': 'localhost:8000/project/barron/website/atoms/'
    });

    //trigger css injection on file change
    gulp.watch(srcPath + '/**/*.s+(a|c)ss', ['styles']);
    //trigger page reload on html change
    // gulp.watch(srcPath + '/**/*.js').on('change', browserSync.reload);
    gulp.watch(srcPath + '/**/sample.json').on('change', browserSync.reload);
    gulp.watch(srcPath + '/**/*.html').on('change', browserSync.reload);
});

// Watch Statics
gulp.task('watch', function() {
    gulp.watch(srcPath + '/**/*.s+(a|c)ss', ['styles']);
    gulp.watch([srcPath + '/**/*.js', '!' + srcPath + '/utils/vendor/modernizr-custom-build.js'], ['modernizr']);
});

gulp.task('copy-images', function() {
    return gulp.src(srcPath + '/images/**/*.*')
        .pipe(gulp.dest(distPath + '/images/'))
})

// Generate Pattern
gulp.task('genpattern', function() {
    // CLI Params
    var argPatternCategory = argv.patternCat;
    var argPatternName = argv.patternName;

    // Targeted Pattern Folder
    var outputCategory = srcPath + '/patterns/' + argPatternCategory;
    // Boilerplate Src
    var boilerplateSrc = rootPath + '/' + targetProject + '/.config/pattern-boilerplate';
    // Final Output Folder
    var boilerplateDest = outputCategory + '/' + argPatternName;

    // To ensure nothing goes awry with existing patterns, we check that the pattern category exists and that the pattern name is unique.
    var patternCategoryExists = patternCategories.indexOf(argPatternCategory) > -1
    var patternIsUnique = scanFolderStructure(outputCategory).indexOf(argPatternName) < 0;


    if (argPatternName && patternCategoryExists && patternIsUnique) {
        console.log('Copying boilerplate from ' + boilerplateSrc)
        console.log('to: ' + boilerplateDest);

        gulp.src([boilerplateSrc + '/**/*'])
            .pipe(copy(boilerplateDest, {
                'prefix': 4
            }));
    } else if (!patternCategoryExists) {
        console.error('"' + argPatternCategory + '"' + ' is not a valid category. The parameter needs to be one of these folders: ' + patternCategories);
    } else if (!patternIsUnique) {
        console.error('"' + argPatternName + '" already exists. Choose a unique name.');
    }
});
