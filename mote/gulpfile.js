"use strict()";

var gulp = require('gulp'),
    del = require('del'),
    runsequence = require('run-sequence'),
    bower = require('main-bower-files'),
    plugins = require('gulp-load-plugins')({
        rename: {
            'gulp-ruby-sass': 'sass',
            'gulp-bower-normalize': 'bowerNormalizer'
        }
    });

var paths = {
    'static': 'static/',
    'scss': {
        'src': 'static/scss/',
        'dist': 'static/css/'
    },
    'scripts': 'static/js'
};

/* ===================================== */
/* SASS */
/* ===================================== */

    gulp.task('sass', function () {

        plugins.sass(paths.scss.src,
            {
                compass: true
            })
            .on('error', function (err) {
                console.error('Error!', err.message);
            })
            .pipe(plugins.plumber())
            .pipe(plugins.flatten())
            .pipe(plugins.autoprefixer())
            .pipe(plugins.bless({
                imports: false
            }))
            //.pipe(plugins.minify({compatibility: 'ie8'}))
            .pipe(gulp.dest(paths.scss.dist));

    });

/* ===================================== */


/* ===================================== */
/* BOWER DEPENDENCIES */
/* ===================================== */

    gulp.task('bower', function() {

        del(paths.scripts + '/libs/*/*.*');

        gulp.src(bower(), {base: './bower_components'})
            .pipe(plugins.bowerNormalizer({bowerJson: './bower.json', checkPath: true}))
            .pipe(gulp.dest(paths.scripts + '/libs'));
    });

/* ===================================== */
