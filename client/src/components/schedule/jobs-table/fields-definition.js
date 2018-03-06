export default {
	tableFields: [
		{
			name: '__component:state-column', // '__component:vuestic-badge-column',
			title: '',
			dataClass: 'text-center'
		},
		{
			name: 'name',
			sortField: 'name'
		},
		{
			name: 'email',
			sortField: 'email'
		},
		{
			name: 'address.line2',
			title: 'city'
		},
		{
			name: 'ID',
			title: 'ID'
		},
		{
			name: 'date_from',
			title: 'Start date'
		}
	],
	sortFunctions: {
		'name': function (item1, item2) {
			return item1 >= item2 ? 1 : -1
		},
		'email': function (item1, item2) {
			return item1 >= item2 ? 1 : -1
		}
	}
}
