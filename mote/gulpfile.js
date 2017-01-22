const Gulp = require('gulp'),
    Theo = require('theo'),
    Path = require('path'),
    Del = require('del'),
    SvgStore = require('gulp-svgstore'),
    SvgMin = require('gulp-svgmin'),
    Cheerio = require('gulp-cheerio');

const Argv = require('yargs')
    .default('projectName', 'mote')
    .default('projectAspect', 'website')
    .argv;

const MotePath = `/mote/projects/${Argv.projectName}/${Argv.projectAspect}`;
const DjangoStaticDir = `/${Argv.projectName}/static/${Argv.projectName}/`;
const PublicStaticPath = `/static/${Argv.projectName}/generated_statics/bundles/`;

const ProjectPaths = {
    root: Path.join(__dirname, MotePath),
    src: Path.join(__dirname, MotePath + '/src'),
    dist: Path.join(__dirname, DjangoStaticDir + '/generated_statics')
};

const TokenConfig = [
    ['raw', 'raw.json'],
    ['ios', 'ios.json'],
    ['android', 'android.xml'],
    ['web', 'scss'],
    ['web', 'map.scss'],
    ['web', 'less'],
    ['web', 'common.js']
];

Gulp.task('pre-bundle', ['design-tokens', 'sprite-maps']);

Gulp.task('watch', function() {
    Gulp.watch(ProjectPaths.src + '/tokens/*.yml', ['design-tokens']);
    Gulp.watch(ProjectPaths.src + '/symbols/**/*.svg', ['sprite-maps']);
});

Gulp.task('design-tokens', function() {
    Del([ProjectPaths.src + '/tokens/formats']).then(function() {
        for (tokenType in TokenConfig) {
            let tokenTransform = TokenConfig[tokenType][0];
            let tokenFormat = TokenConfig[tokenType][1];

            Gulp.src(ProjectPaths.src + '/tokens/props.yml')
                .pipe(Theo.plugins.transform(tokenTransform))
                .pipe(Theo.plugins.format(tokenFormat))
                .pipe(Gulp.dest(ProjectPaths.src + '/tokens/formats'));
        }
    });
});

Gulp.task('sprite-maps', ['symbols']);

Gulp.task('symbols', function() {
    return Gulp.src(ProjectPaths.src + '/symbols/**/*.svg')
    .pipe(Cheerio({
        run: function ($) {
            $('svg:not(.KeepFills) [fill]').removeAttr('fill');
        },
        parserOptions: { xmlMode: true }
    }))
    .pipe(SvgMin(function(file) {
        const prefix = Path.basename(file.relative, Path.extname(file.relative));
        return {
            plugins: [{
                cleanupIDs: {
                    prefix: prefix + '-',
                    minify: true
                }
            }]
        }
    }))
    .pipe(SvgStore())
    .pipe(Gulp.dest(ProjectPaths.dist));
})
