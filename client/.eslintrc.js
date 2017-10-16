// http://eslint.org/docs/user-guide/configuring
const path = require('path')

module.exports = {
	root: true,
	parser: 'babel-eslint',
	parserOptions: {
		sourceType: 'module'
	},
	env: {
		browser: true,
	},

	// https://github.com/feross/standard/blob/master/RULES.md#javascript-standard-style
	extends: [
		path.join(__dirname, 'node_modules', 'eslint-config-volebo', 'index.js')
	],

	// required to lint *.vue files
	plugins: [
		'html'
	],
	// add your custom rules here
	'rules': {
		// allow paren-less arrow functions
		'arrow-parens': 0,
		// allow async-await
		'generator-star-spacing': 0,
		// allow debugger during development
		'no-debugger': process.env.NODE_ENV === 'production' ? 2 : 0,


		// TEMPORARY:
		'guard-for-in': 0,
		'no-console': 1,
		'no-unused-vars': 1,
	}
}
