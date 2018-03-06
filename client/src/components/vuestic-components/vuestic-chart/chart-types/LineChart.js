import { Line } from 'vue-chartjs'
import DefaultOptions from '../DefaultOptions'

export default Line.extend({
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
