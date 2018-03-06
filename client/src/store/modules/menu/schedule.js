import lazyLoading from './lazyLoading'

export default {
	name: 'Schedule',
	meta: {
		title: 'Schedule',
		iconClass: 'fa fa-calendar'
	},
	path: '/schedule',
	component: lazyLoading('schedule/Schedule')
}
