<template>
	<span class="circle" :class="classObject"></span>
</template>

<script>
	export default {
		name: 'unav-state-column',
		props: {
			rowData: {
				type: Object,
				required: true
			},
			rowIndex: {
				type: Number
			}
		},
		data () {
			console.log('row value', this.rowData)

			return {
				classObject: {
					'badge-warning':    this.rowData === 'PROCESS',
					'badge-primary':    this.rowData === '1',
					'badge-danger':     this.rowData === '',
					'badge-info':       this.rowData === '3',
					'badge-violet':     this.rowData === '4',
					'badge-dark-blue':  this.rowData === '5'
				}
			}
		}
	}
</script>

<style lang="scss" scoped>
	.circle {
		width: .75rem;
		height: .75rem;
		border-radius: 50%;
		display: inline-block;
	}
</style>
