module.exports = function(grunt) {
    // Project configuration.
    grunt.initConfig({
        'pkg': grunt.file.readJSON('package.json'),
        'svgmin': {
            'dist': {
                'options': {
                    'plugins': [
                        // Don't remove XML declaration (needed to avoid errors creating PNG on Win 7)
                        { 'removeXMLProcInst': false }
                    ]
                },
                'files': [{
                    'expand': true,
                    'cwd': 'projects/barron/website/src/patterns/atoms/icons/',
                    'src': ['*/*.svg'],
                    'dest': 'projects/barron/website/src/patterns/atoms/icons/'
                }]
            }
        },
        'grunticon': {
            'icons': {
                'files': [{
                    'expand': true,
                    'cwd': 'projects/barron/website/src/patterns/atoms/icons/',
                    'src': ['*/*.svg', '*/*.png'],
                    'dest': 'projects/barron/website/dist/images/icons/'
                }],
                'options': {
                    'template': 'projects/barron/website/src/patterns/atoms/icons/template.hbs',
                    'previewTemplate': 'projects/barron/website/src/patterns/atoms/icons/preview.hbs',
                    'previewhtml': 'element.html',
                    'enhanceSVG': true,
                    'compressPNG': true,
                    'defaultWidth': '300px',
                    'defaultHeight': '300px',
                    'dynamicColorOnly': true,
                    'colors': {
                        'yellowButtercup': '#d79b2d',
                        'greenCyprus': '#07292f',
                        'greenOracle': '#375357',
                        'black': '#000000',
                        'grey': '#787878',
                        'white': '#ffffff',
                        'whiteSmoke': '#f3f3f3',
                        'whiteGainsboro': '#e0e0e0'
                    }
                }
            }
        },
        'cssmin': {
            'target': {
                'files': [{
                    'expand': true,
                    'cwd': 'projects/barron/website/dist/images/icons/',
                    'src': ['*.css', '!*.min.css'],
                    'dest': 'projects/barron/website/dist/images/icons/',
                    'ext': '.min.css'
                }]
            }
        }
    });

    grunt.loadNpmTasks('grunt-grunticon');
    grunt.loadNpmTasks('grunt-svgmin');

    // Default task(s).
    grunt.registerTask('default', ['svgmin', 'grunticon']);
}
