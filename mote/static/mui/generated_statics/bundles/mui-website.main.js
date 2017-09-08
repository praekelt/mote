/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/static/mui/generated_statics/bundles/";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';
	
	if (false) {
	    require('./styles.scss');
	}
	
	__webpack_require__(1);
	__webpack_require__(3);

/***/ },
/* 1 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';
	
	var _documentReady = __webpack_require__(2);
	
	(0, _documentReady.ready)(function () {
	    var Toggles = document.querySelectorAll('[data-variation-toggle]');
	
	    function onClick(el) {
	        el.addEventListener('click', function (e) {
	            e.preventDefault();
	
	            for (var i = 0; i < Toggles.length; i++) {
	                Toggles[i].classList.remove('is-active');
	            }
	
	            el.classList.add('is-active');
	
	            var target = '#' + el.getAttribute('data-variation-toggle');
	            var url = el.getAttribute('href');
	            var linksOutButton = document.querySelector('[data-linksto="' + target + '"]');
	
	            document.querySelector(target).setAttribute('src', url);
	
	            linksOutButton.setAttribute('href', url);
	
	            // Toggle the example / usage area
	            var dottedName = el.getAttribute('data-element-dotted-name');
	            // No clue why querySelector causes issues. Use jQuery.
	            //document.querySelector('.element-usage').setAttribute('style': 'display: none');
	            $('.element-usage').hide();
	            document.querySelector('[data-usage-dotted-name="' + dottedName + '"]').setAttribute('style', 'display: auto');
	        });
	    }
	
	    for (var i = 0; i < Toggles.length; i++) {
	        onClick(Toggles[i]);
	    }
	});

/***/ },
/* 2 */
/***/ function(module, exports) {

	'use strict';
	
	Object.defineProperty(exports, "__esModule", {
	    value: true
	});
	exports.ready = ready;
	function ready(fn) {
	    if (document.readyState !== 'loading') {
	        fn();
	    } else {
	        document.addEventListener('DOMContentLoaded', fn);
	    }
	}

/***/ },
/* 3 */
/***/ function(module, exports, __webpack_require__) {

	'use strict';
	
	var _documentReady = __webpack_require__(2);
	
	(0, _documentReady.ready)(function () {
	    var Toggles = document.querySelectorAll('.Documentation-toggler');
	
	    for (var i = 0; i < Toggles.length; i++) {
	        // Set the is off state on the toggles
	        var toggle = Toggles[i];
	        toggle.classList.add('is-off');
	
	        // Set the hidden state on the panels
	        var panel = Toggles[i].getAttribute('href');
	        document.querySelector(panel).classList.add('is-hidden');
	    }
	
	    function onClick(el) {
	        el.addEventListener('click', function (e) {
	            e.preventDefault();
	
	            el.classList.toggle('is-off');
	
	            var target = document.querySelector(el.getAttribute('href'));
	
	            if (target.classList.contains('is-hidden')) {
	                target.classList.remove('is-hidden');
	            } else {
	                target.classList.add('is-hidden');
	            }
	        });
	    }
	
	    for (var _i = 0; _i < Toggles.length; _i++) {
	        onClick(Toggles[_i]);
	    }
	});

/***/ }
/******/ ]);
//# sourceMappingURL=mui-website.main.js.map