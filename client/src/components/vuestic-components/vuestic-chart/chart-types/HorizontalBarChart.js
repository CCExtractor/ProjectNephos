import { HorizontalBar } from 'vue-chartjs'
import DefaultOptions from '../DefaultOptions'

export default HorizontalBar.extend({
	props: ['data', 'options'],

	data () {
		return {
			defaultOptions: {

			}
		}
	},

	mounted () {
		const options = Object.assign({}, DefaultOptions, this.defaultOptions, this.options)
		this.renderChart(this.data, options)
	}
})
