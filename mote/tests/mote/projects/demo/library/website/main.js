if (process.env.NODE_ENV === 'development') {
    require('./styles.scss');
}

require('./app/variation-toggler');
require('./app/documentation-toggler');
